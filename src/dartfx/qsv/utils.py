from __future__ import annotations

import csv
import io
import json
import os
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

from dartfx.qsv.model import QsvStatsDataModel


def _load_json_data(data: Any) -> Any:
    """Load JSON/dict data from a file path, JSON string, or dictionary."""
    if isinstance(data, dict):
        return data
    if isinstance(data, (str, os.PathLike)):
        # Check if it's a file path
        if os.path.exists(data):
            with open(data, encoding="utf-8") as f:
                return json.load(f)
        else:
            return json.loads(str(data))
    raise ValueError("Invalid JSON data source.")


def _parse_stats_json_or_jsonl(content: str) -> list[dict[str, Any]]:
    """Parse JSON or JSONL content into a list of dictionaries."""
    content = content.strip()
    if content.startswith("["):
        return json.loads(content)
    # Parse as JSONL
    results = []
    for line in content.splitlines():
        line = line.strip()
        if line:
            results.append(json.loads(line))
    return results


def _load_stats_data(data: Any) -> list[dict[str, Any]]:
    """Load stats data from lists (Pydantic/dicts), file paths, or raw strings."""
    if isinstance(data, list):
        if not data:
            return []
        if hasattr(data[0], "model_dump"):  # Pydantic v2
            return [item.model_dump(by_alias=True) for item in data]
        elif hasattr(data[0], "dict"):  # Pydantic v1 fallback
            return [item.dict(by_alias=True) for item in data]
        return [dict(item) for item in data]

    if isinstance(data, (str, os.PathLike)):
        if os.path.exists(data):
            path_str = str(data).lower()
            if path_str.endswith(".jsonl") or path_str.endswith(".json"):
                with open(data, encoding="utf-8") as f:
                    content = f.read()
                return _parse_stats_json_or_jsonl(content)
            else:
                # Default to CSV
                with open(data, encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    return list(reader)
        else:
            data_str = str(data).strip()
            if data_str.startswith("{") or data_str.startswith("["):
                return _parse_stats_json_or_jsonl(data_str)
            else:
                reader = csv.DictReader(io.StringIO(data_str))
                return list(reader)
    raise ValueError("Invalid stats data source.")


def generate_ddi_codebook(
    csv_path: str | os.PathLike[str] | None = None,
    stats_data: list[dict[str, Any]] | list[QsvStatsDataModel] | str | os.PathLike[str] | None = None,
    schema_data: dict[str, Any] | str | os.PathLike[str] | None = None,
    frequency_data: dict[str, Any] | str | os.PathLike[str] | None = None,
    version: str = "2.6",
    output_xml_path: str | os.PathLike[str] | None = None,
    categorical_threshold: int = 20,
    categorical_columns: list[str] | None = None,
) -> str:
    """
    Aggregates the outputs of QSV stats, frequency, and schema, and creates a
    DDI-Codebook 2.5 or 2.6 XML document. Frequencies are optional.

    Args:
        csv_path: Optional path to the source CSV file. If provided and other data is missing,
            the corresponding QSV commands are run automatically.
        stats_data: Pre-computed stats data (Pydantic models list, dict list, file path, or string).
        schema_data: Pre-computed schema data (dict, file path, or string).
        frequency_data: Pre-computed frequency data (dict, file path, or string).
        version: DDI-Codebook version ("2.5" or "2.6"). Default is "2.6".

        output_xml_path: Optional file path to write the generated XML.
        categorical_threshold: Threshold cardinality below which numeric/string columns
            without explicit schema enums are considered categorical (default 20).
        categorical_columns: Explicit list of categorical column names. If provided, overrides auto-detection.

    Returns:
        str: Pretty-printed XML string conforming to the DDI-Codebook schema.
    """
    if version not in ("2.5", "2.6"):
        raise ValueError("Only DDI-Codebook versions '2.5' and '2.6' are supported.")

    # 1. Gather stats and schema (either pre-supplied or executed dynamically)
    if stats_data is None:
        if not csv_path:
            raise ValueError("Must provide either stats_data or csv_path to run QSV stats.")
        from dartfx.qsv.cmd import Stats

        stats_csv = Stats(infer_dates=True, infer_boolean=True).run(str(csv_path))
        parsed_stats = _load_stats_data(stats_csv)
    else:
        parsed_stats = _load_stats_data(stats_data)

    if schema_data is None:
        if not csv_path:
            raise ValueError("Must provide either schema_data or csv_path to run QSV schema.")
        from dartfx.qsv.cmd import Schema

        schema_json = Schema(stdout=True).run(str(csv_path))
        parsed_schema = _load_json_data(schema_json)
    else:
        parsed_schema = _load_json_data(schema_data)

    # Helper maps
    stats_dict = {row["field"]: row for row in parsed_stats}
    properties = parsed_schema.get("properties", {})

    def get_cardinality(field_name: str) -> int | None:
        row = stats_dict.get(field_name)
        if not row:
            return None
        val = row.get("cardinality")
        if val is None or val == "":
            return None
        try:
            return int(val)
        except ValueError:
            return None

    def get_field_type(field_name: str) -> str | None:
        row = stats_dict.get(field_name)
        if not row:
            return None
        return row.get("type")

    # 2. Identify categorical columns
    detected_categorical = []
    for col, prop in properties.items():
        if categorical_columns is not None:
            if col in categorical_columns:
                detected_categorical.append(col)
            continue

        # Auto-detect categorical columns
        has_enum = "enum" in prop
        card = get_cardinality(col)
        col_type = get_field_type(col) or prop.get("type", ["String"])
        if isinstance(col_type, list):
            col_type = col_type[0] if col_type else "String"
        col_type_str = str(col_type)

        if has_enum:
            detected_categorical.append(col)
        elif card is not None and card <= categorical_threshold:
            if col_type_str in ("Integer", "String", "Boolean"):
                detected_categorical.append(col)

    # 3. Gather frequency (either pre-supplied, executed dynamically, or fallback to empty)
    if frequency_data is None:
        if csv_path and detected_categorical:
            from dartfx.qsv.cmd import Frequency

            freq_json = Frequency(select=",".join(detected_categorical), limit=0, unq_limit=1, json=True).run(
                str(csv_path)
            )
            parsed_frequency = _load_json_data(freq_json)
        else:
            parsed_frequency = {"fields": []}
    else:
        parsed_frequency = _load_json_data(frequency_data)

    # 4. XML construction
    version_underscore = "2_5" if version == "2.5" else "2_6"
    ns = f"ddi:codebook:{version_underscore}"

    ET.register_namespace("", ns)
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

    root_attrs = {
        "ID": f"_{uuid.uuid4()}",
        "version": version,
        "{http://www.w3.org/XML/1998/namespace}lang": "en",
        "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": (
            f"{ns} http://www.ddialliance.org/Specification/DDI-Codebook/{version}/XMLSchema/codebook.xsd"
        ),
    }
    root = ET.Element(f"{{{ns}}}codeBook", root_attrs)

    # Extract filename
    filename = "dataset.csv"
    if csv_path:
        filename = os.path.basename(csv_path)
    elif isinstance(parsed_frequency, dict) and isinstance(parsed_frequency.get("input"), str):
        filename = os.path.basename(parsed_frequency["input"])

    # QSV version for metadata
    qsv_version = "unknown"
    try:
        from dartfx.qsv.cmd import QSV

        qsv_version = QSV.version_number()
    except Exception:
        pass

    # <docDscr>
    docDscr = ET.SubElement(root, f"{{{ns}}}docDscr")
    citation = ET.SubElement(docDscr, f"{{{ns}}}citation")
    titlStmt = ET.SubElement(citation, f"{{{ns}}}titlStmt")
    titl = ET.SubElement(titlStmt, f"{{{ns}}}titl")
    titl.text = f"{filename}"
    prodStmt = ET.SubElement(citation, f"{{{ns}}}prodStmt")
    current_date = datetime.now().strftime("%Y-%m-%d")
    prodDate = ET.SubElement(prodStmt, f"{{{ns}}}prodDate", {"date": current_date})
    prodDate.text = current_date
    try:
        from dartfx.qsv.__about__ import __version__ as toolkit_version
    except ImportError:
        toolkit_version = "unknown"
    software_toolkit = ET.SubElement(prodStmt, f"{{{ns}}}software", {"version": toolkit_version})
    software_toolkit.text = "Data Artifex QSV Toolkit"
    software_qsv = ET.SubElement(prodStmt, f"{{{ns}}}software", {"version": qsv_version})
    software_qsv.text = "QSV"

    # <stdyDscr>
    stdyDscr = ET.SubElement(root, f"{{{ns}}}stdyDscr")
    citation_stdy = ET.SubElement(stdyDscr, f"{{{ns}}}citation")
    titlStmt_stdy = ET.SubElement(citation_stdy, f"{{{ns}}}titlStmt")
    titl_stdy = ET.SubElement(titlStmt_stdy, f"{{{ns}}}titl")
    titl_stdy.text = f"{filename}"

    # Row/Var dimensions
    rowcount = None
    if isinstance(parsed_frequency, dict) and "rowcount" in parsed_frequency:
        rowcount = parsed_frequency["rowcount"]
    elif csv_path:
        try:
            from dartfx.qsv.cmd import Count

            res = Count().run(str(csv_path))
            rowcount = int(res.strip())
        except Exception:
            pass

    fieldcount = None
    if properties:
        fieldcount = len(properties)
    elif parsed_stats:
        fieldcount = len(parsed_stats)
    elif isinstance(parsed_frequency, dict) and "fieldcount" in parsed_frequency:
        fieldcount = parsed_frequency["fieldcount"]

    # <fileDscr>
    file_id = "F1"
    fileDscr = ET.SubElement(root, f"{{{ns}}}fileDscr", {"ID": file_id})
    fileTxt = ET.SubElement(fileDscr, f"{{{ns}}}fileTxt")
    fileName = ET.SubElement(fileTxt, f"{{{ns}}}fileName")
    fileName.text = filename

    if rowcount is not None or fieldcount is not None:
        dimensns = ET.SubElement(fileTxt, f"{{{ns}}}dimensns")
        if rowcount is not None:
            caseQnty = ET.SubElement(dimensns, f"{{{ns}}}caseQnty")
            caseQnty.text = str(rowcount)
        if fieldcount is not None:
            varQnty = ET.SubElement(dimensns, f"{{{ns}}}varQnty")
            varQnty.text = str(fieldcount)

    fileType = ET.SubElement(fileTxt, f"{{{ns}}}fileType")
    fileType.text = "Comma-delimited CSV file"

    # <dataDscr>
    dataDscr = ET.SubElement(root, f"{{{ns}}}dataDscr")

    # Order of columns
    columns = list(properties.keys()) if properties else [row["field"] for row in parsed_stats]

    # Map frequencies by field
    freq_fields = parsed_frequency.get("fields", []) if isinstance(parsed_frequency, dict) else []
    freq_dict = {f["field"]: f for f in freq_fields if "field" in f}

    for idx, col in enumerate(columns, start=1):
        prop = properties.get(col, {})
        stats_row = stats_dict.get(col, {})

        is_cat = col in detected_categorical

        qsv_type = stats_row.get("type") or prop.get("type", ["String"])
        if isinstance(qsv_type, list):
            qsv_type = qsv_type[0] if qsv_type else "String"
        qsv_type_str = str(qsv_type).lower()

        is_numeric = qsv_type_str in ("integer", "float", "number")
        is_contin_type = qsv_type_str in ("float", "number")
        intrvl_val = "contin" if (is_contin_type and not is_cat) else "discrete"

        if is_cat:
            rep_type = "coded"
        elif "date" in qsv_type_str or "time" in qsv_type_str:
            rep_type = "datetime"
        elif "boolean" in qsv_type_str:
            rep_type = "boolean"
        elif is_numeric:
            rep_type = "numeric"
        else:
            rep_type = "text"

        var_attrs = {
            "ID": f"V{idx}",
            "name": col,
            "files": file_id,
            "intrvl": intrvl_val,
            "representationType": rep_type,
        }

        max_prec = stats_row.get("max_precision")
        if max_prec is not None and max_prec != "":
            try:
                var_attrs["dcml"] = str(int(max_prec))
            except ValueError:
                pass

        var_elem = ET.SubElement(dataDscr, f"{{{ns}}}var", var_attrs)

        labl_elem = ET.SubElement(var_elem, f"{{{ns}}}labl")
        labl_elem.text = col

        # Add summary statistics
        def add_sum_stat(stat_type: str, val: Any, other_type: str | None = None, var_elem=var_elem) -> None:

            if val is not None and val != "":
                attrs = {"type": stat_type}
                if other_type:
                    attrs["otherType"] = other_type
                elem = ET.SubElement(var_elem, f"{{{ns}}}sumStat", attrs)
                elem.text = str(val)

        add_sum_stat("mean", stats_row.get("mean"))
        add_sum_stat("medn", stats_row.get("q2_median"))
        add_sum_stat("mode", stats_row.get("mode"))
        add_sum_stat("stdev", stats_row.get("stddev"))
        add_sum_stat("min", stats_row.get("min"))
        add_sum_stat("max", stats_row.get("max"))

        nullcount = stats_row.get("nullcount")
        if nullcount is not None and nullcount != "":
            try:
                nullcount_int = int(nullcount)
                add_sum_stat("invd", nullcount_int)
                if rowcount is not None:
                    if isinstance(rowcount, (int, str, float)):
                        add_sum_stat("vald", max(0, int(rowcount) - nullcount_int))
            except ValueError:
                add_sum_stat("invd", nullcount)

        add_sum_stat("other", stats_row.get("sum"), "sum")
        add_sum_stat("other", stats_row.get("range"), "range")
        add_sum_stat("other", stats_row.get("variance"), "variance")
        add_sum_stat("other", stats_row.get("cv"), "cv")
        add_sum_stat("other", stats_row.get("skewness"), "skewness")
        add_sum_stat("other", stats_row.get("sparsity"), "sparsity")
        add_sum_stat("other", stats_row.get("cardinality"), "cardinality")

        # Category Frequencies
        freq_field = freq_dict.get(col, {})
        frequencies = freq_field.get("frequencies", [])
        for f_item in frequencies:
            cat_val = f_item.get("value")
            if cat_val is None:
                continue

            catgry = ET.SubElement(var_elem, f"{{{ns}}}catgry")

            catValu = ET.SubElement(catgry, f"{{{ns}}}catValu")
            catValu.text = str(cat_val)

            labl = ET.SubElement(catgry, f"{{{ns}}}labl")
            labl.text = str(cat_val)

            count = f_item.get("count")
            if count is not None:
                catStat_freq = ET.SubElement(catgry, f"{{{ns}}}catStat", {"type": "freq"})
                catStat_freq.text = str(count)

            pct = f_item.get("percentage")
            if pct is not None:
                catStat_pct = ET.SubElement(catgry, f"{{{ns}}}catStat", {"type": "percent"})
                catStat_pct.text = str(pct)

        # Add varFormat element
        vf_attrs = {
            "type": "numeric" if qsv_type_str in ("integer", "float", "number") else "character",
            "schema": "other",
            "otherSchema": "qsv",
            "formatname": qsv_type,
        }
        if "date" in qsv_type_str or "time" in qsv_type_str or rep_type == "datetime":
            vf_attrs["category"] = "date"
        ET.SubElement(var_elem, f"{{{ns}}}varFormat", vf_attrs)

    # Indent and serialize
    ET.indent(root, space="    ")
    xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

    if output_xml_path:
        with open(output_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_str)

    return xml_str


def generate_sql(
    csv_path: str | os.PathLike[str],
    schema_data: dict[str, Any] | str | os.PathLike[str] | None = None,
    stats_data: list[dict[str, Any]] | list[QsvStatsDataModel] | str | os.PathLike[str] | None = None,
    frequency_data: dict[str, Any] | str | os.PathLike[str] | None = None,
    flavor: str = "postgres",
    table_name: str | None = None,
    schema_name: str | None = None,
    output_sql_path: str | os.PathLike[str] | None = None,
    primary_key: list[str] | str | None = None,
) -> str:
    """
    Generates a SQL script to host/load a CSV file, based on the output of
    qsv schema, and optional stats and frequency data.

    Args:
        csv_path: Path to the source CSV file. Used for defaulting table name and path in comments.
        schema_data: Pre-computed schema data (dict, file path, or JSON string).
        stats_data: Pre-computed stats data (list of dicts, list of Pydantic models, file path, or string).
        frequency_data: Pre-computed frequency data (dict, file path, or JSON string).
        flavor: SQL flavor ("postgres", "sqlite", "mysql", "mssql", "oracle", "clickhouse",
            "duckdb", "snowflake", "bigquery", "redshift", "mariadb"). Default is "postgres".
        table_name: Custom table name. If not specified, defaults to "tbl_<csv-filename>".
        schema_name: Optional database schema name (postgres/mysql/mariadb/bigquery only).
        output_sql_path: Optional path to write the generated SQL script.

    Returns:
        str: The generated SQL script.
    """
    flavor_lower = flavor.lower()
    if flavor_lower == "postgresql":
        flavor_lower = "postgres"

    supported_flavors = (
        "postgres",
        "sqlite",
        "mysql",
        "mssql",
        "oracle",
        "clickhouse",
        "duckdb",
        "snowflake",
        "bigquery",
        "redshift",
        "mariadb",
    )
    if flavor_lower not in supported_flavors:
        raise ValueError(f"Unsupported flavor '{flavor}'. Supported: {', '.join(supported_flavors)}.")

    # 1. Resolve JSON Schema (reuse existing internal methods)
    if schema_data is None:
        from dartfx.qsv.cmd import Schema

        schema_json = Schema(stdout=True).run(str(csv_path))
        parsed_schema = _load_json_data(schema_json)
    else:
        parsed_schema = _load_json_data(schema_data)

    # 2. Resolve Stats Data (optional but resolved if None and csv_path exists)
    parsed_stats = None
    if stats_data is None:
        if csv_path:
            try:
                from dartfx.qsv.cmd import Stats

                stats_csv = Stats(infer_dates=True, infer_boolean=True).run(str(csv_path))
                parsed_stats = _load_stats_data(stats_csv)
            except Exception:
                # Fallback to no stats if running stats fails
                pass
    else:
        parsed_stats = _load_stats_data(stats_data)

    # 3. Resolve Frequency Data (optional)
    if frequency_data is not None:
        _load_json_data(frequency_data)

    # 4. Resolve table name
    if not table_name:
        base = os.path.splitext(os.path.basename(csv_path))[0]
        import re

        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", base)
        table_name = f"tbl_{sanitized}"

    # 5. Resolve quoting rules
    if flavor_lower in ("mysql", "mariadb", "bigquery"):
        quote_char = "`"
    else:
        quote_char = '"'

    def quote(identifier: str) -> str:
        if flavor_lower == "mssql":
            escaped = identifier.replace("]", "]]")
            return f"[{escaped}]"
        else:
            escaped = identifier.replace(quote_char, quote_char + quote_char)
            return f"{quote_char}{escaped}{quote_char}"

    quoted_table = quote(table_name)
    if schema_name:
        quoted_table = f"{quote(schema_name)}.{quoted_table}"

    # Helpers
    stats_dict = {row["field"]: row for row in parsed_stats} if parsed_stats else {}
    properties = parsed_schema.get("properties", {})

    # Resolve and validate primary key fields (case-insensitive)
    resolved_pk_fields = []
    if primary_key:
        pk_fields = []
        if isinstance(primary_key, str):
            pk_fields = [pk_item.strip() for pk_item in primary_key.split(",") if pk_item.strip()]
        elif isinstance(primary_key, (list, tuple)):
            for pk_item in primary_key:
                if isinstance(pk_item, str) and pk_item.strip():
                    pk_fields.append(pk_item.strip())

        actual_fields = list(properties.keys())
        field_name_map = {f.lower(): f for f in actual_fields}

        for pk in pk_fields:
            pk_lower = pk.lower()
            if pk_lower not in field_name_map:
                raise ValueError(
                    f"Primary key field '{pk}' does not exist in the CSV schema (columns: {', '.join(actual_fields)})."
                )
            resolved_pk_fields.append(field_name_map[pk_lower])

    # Helper function to map integer types
    def get_integer_type(minimum, maximum, flv):
        if minimum is not None and maximum is not None:
            try:
                min_val = int(minimum)
                max_val = int(maximum)
                if min_val < -2147483648 or max_val > 2147483647:
                    return "BIGINT"
                elif min_val >= -32768 and max_val <= 32767:
                    return "SMALLINT"
            except (ValueError, TypeError):
                pass
        return "INT" if flv == "mysql" else "INTEGER"

    # Helper function to map ClickHouse integer types
    def get_clickhouse_integer_type(minimum, maximum):
        if minimum is not None and maximum is not None:
            try:
                min_val = int(minimum)
                max_val = int(maximum)
                if min_val >= 0:
                    if max_val <= 255:
                        return "UInt8"
                    elif max_val <= 65535:
                        return "UInt16"
                    elif max_val <= 4294967295:
                        return "UInt32"
                    else:
                        return "UInt64"
                else:
                    if min_val >= -128 and max_val <= 127:
                        return "Int8"
                    elif min_val >= -32768 and max_val <= 32767:
                        return "Int16"
                    elif min_val >= -2147483648 and max_val <= 2147483647:
                        return "Int32"
                    else:
                        return "Int64"
            except (ValueError, TypeError):
                pass
        return "Int32"

    # 6. Map columns
    columns_defs = []
    for col, prop in properties.items():
        # Get types
        json_types = prop.get("type", [])
        if isinstance(json_types, str):
            json_types = [json_types]
        primary_types = [t for t in json_types if t != "null"]
        primary_type = primary_types[0] if primary_types else "string"

        stats_row = stats_dict.get(col, {})
        stats_type = stats_row.get("type")  # e.g., "Integer", "Float", "String", "Date", "DateTime", "Boolean"
        stats_type_str = str(stats_type).lower() if stats_type else ""

        col_type = "TEXT"  # fallback

        # Resolve min/max from stats or schema
        minimum = None
        maximum = None
        if stats_row:
            minimum = stats_row.get("min")
            maximum = stats_row.get("max")
        if minimum is None:
            minimum = prop.get("minimum")
        if maximum is None:
            maximum = prop.get("maximum")

        is_date = "date" in stats_type_str or prop.get("format") == "date"
        is_datetime = "datetime" in stats_type_str or prop.get("format") == "date-time"

        if flavor_lower == "postgres":
            if is_date:
                col_type = "DATE"
            elif is_datetime:
                col_type = "TIMESTAMP"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = get_integer_type(minimum, maximum, "postgres")
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "DOUBLE PRECISION"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "BOOLEAN"
            else:
                max_len = prop.get("maxLength")
                col_type = f"VARCHAR({max_len})" if max_len else "TEXT"

        elif flavor_lower == "sqlite":
            if primary_type == "integer" or stats_type_str == "integer":
                col_type = "INTEGER"
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "REAL"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "INTEGER"
            else:
                col_type = "TEXT"

        elif flavor_lower == "mysql":
            if is_date:
                col_type = "DATE"
            elif is_datetime:
                col_type = "DATETIME"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = get_integer_type(minimum, maximum, "mysql")
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "DOUBLE"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "BOOLEAN"
            else:
                max_len = prop.get("maxLength")
                col_type = f"VARCHAR({max_len})" if max_len else "TEXT"

        elif flavor_lower == "mssql":
            if is_date:
                col_type = "DATE"
            elif is_datetime:
                col_type = "DATETIME2"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = get_integer_type(minimum, maximum, "mssql")
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "FLOAT"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "BIT"
            else:
                max_len = prop.get("maxLength")
                col_type = f"VARCHAR({max_len})" if max_len else "VARCHAR(MAX)"

        elif flavor_lower == "oracle":
            if is_date:
                col_type = "DATE"
            elif is_datetime:
                col_type = "TIMESTAMP"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = "INTEGER"
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "DOUBLE PRECISION"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "NUMBER(1)"
            else:
                max_len = prop.get("maxLength")
                col_type = f"VARCHAR2({max_len})" if max_len else "VARCHAR2(4000)"

        elif flavor_lower == "clickhouse":
            if is_date:
                col_type = "Date"
            elif is_datetime:
                col_type = "DateTime"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = get_clickhouse_integer_type(minimum, maximum)
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "Float64"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "Bool"
            else:
                col_type = "String"

        elif flavor_lower == "duckdb":
            if is_date:
                col_type = "DATE"
            elif is_datetime:
                col_type = "TIMESTAMP"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = get_integer_type(minimum, maximum, "duckdb")
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "DOUBLE"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "BOOLEAN"
            else:
                col_type = "VARCHAR"

        elif flavor_lower == "snowflake":
            if is_date:
                col_type = "DATE"
            elif is_datetime:
                col_type = "TIMESTAMP_NTZ"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = get_integer_type(minimum, maximum, "snowflake")
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "DOUBLE"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "BOOLEAN"
            else:
                max_len = prop.get("maxLength")
                col_type = f"VARCHAR({max_len})" if max_len else "VARCHAR"

        elif flavor_lower == "bigquery":
            if is_date:
                col_type = "DATE"
            elif is_datetime:
                col_type = "DATETIME"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = "INT64"
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "FLOAT64"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "BOOL"
            else:
                col_type = "STRING"

        elif flavor_lower == "redshift":
            if is_date:
                col_type = "DATE"
            elif is_datetime:
                col_type = "TIMESTAMP"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = get_integer_type(minimum, maximum, "redshift")
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "DOUBLE PRECISION"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "BOOLEAN"
            else:
                max_len = prop.get("maxLength")
                col_type = f"VARCHAR({max_len})" if max_len else "VARCHAR(256)"

        elif flavor_lower == "mariadb":
            if is_date:
                col_type = "DATE"
            elif is_datetime:
                col_type = "DATETIME"
            elif primary_type == "integer" or stats_type_str == "integer":
                col_type = get_integer_type(minimum, maximum, "mariadb")
            elif primary_type == "number" or stats_type_str in ("float", "number"):
                col_type = "DOUBLE"
            elif primary_type == "boolean" or stats_type_str == "boolean":
                col_type = "BOOLEAN"
            else:
                max_len = prop.get("maxLength")
                col_type = f"VARCHAR({max_len})" if max_len else "TEXT"

        columns_defs.append(f"    {quote(col)} {col_type}")

    if resolved_pk_fields:
        quoted_pks = [quote(f) for f in resolved_pk_fields]
        columns_defs.append(f"    PRIMARY KEY ({', '.join(quoted_pks)})")

    try:
        from dartfx.qsv.__about__ import __version__ as toolkit_version
    except ImportError:
        toolkit_version = "unknown"

    # Build CREATE TABLE
    sql_script = [
        f"-- Generated by dartfx-qsv tosql {toolkit_version}",
        f"-- Table: {quoted_table}",
        f"-- Flavor: {flavor}",
        f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"CREATE TABLE {quoted_table} (",
        ",\n".join(columns_defs),
        ");",
        "",
    ]

    # Generate load instructions in comments
    csv_filename = os.path.basename(csv_path)
    escaped_csv_filename = str(csv_filename).replace("'", "''")

    quoted_cols = [quote(col) for col in properties.keys()]
    cols_str = ", ".join(quoted_cols)

    if flavor_lower == "postgres":
        sql_script.append("/*")
        sql_script.append("To load the CSV data into this table:")
        sql_script.append(
            f"COPY {quoted_table} FROM '{escaped_csv_filename}' WITH (FORMAT csv, HEADER true, DELIMITER ',');"
        )
        sql_script.append("OR (if the file is local to your client and not on the database server):")
        sql_script.append(
            f"\\copy {quoted_table} FROM '{escaped_csv_filename}' WITH (FORMAT csv, HEADER true, DELIMITER ',');"
        )
        sql_script.append("*/")
    else:
        sql_script.append("-- To load the CSV data into this table:")
        if flavor_lower == "sqlite":
            sql_script.append(f"-- .import '{escaped_csv_filename}' {quoted_table} --csv")
        elif flavor_lower == "mysql":
            sql_script.append(
                f"-- LOAD DATA INFILE '{escaped_csv_filename}' INTO TABLE {quoted_table} "
                f"FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS;"
            )
        elif flavor_lower == "mssql":
            sql_script.append(
                f"-- BULK INSERT {quoted_table} FROM '{escaped_csv_filename}' "
                f"WITH (FORMAT = 'CSV', FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\\n');"
            )
        elif flavor_lower == "oracle":
            control_file_lines = [
                "-- SQL*Loader Control File Syntax:",
                "-- LOAD DATA",
                f"-- INFILE '{escaped_csv_filename}'",
                f"-- INTO TABLE {quoted_table}",
                "-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"'",
                f"-- ({cols_str})",
            ]
            sql_script.extend(control_file_lines)
        elif flavor_lower == "clickhouse":
            sql_script.append(
                f"-- clickhouse-client --query='INSERT INTO {quoted_table} "
                f"FORMAT CSVWithNames' < '{escaped_csv_filename}'"
            )
        elif flavor_lower == "duckdb":
            sql_script.append(
                f"-- COPY {quoted_table} FROM '{escaped_csv_filename}' (FORMAT CSV, HEADER TRUE, DELIMITER ',');"
            )
            sql_script.append(
                f"-- OR: INSERT INTO {quoted_table} SELECT * FROM read_csv_auto('{escaped_csv_filename}');"
            )
        elif flavor_lower == "snowflake":
            sql_script.append(f"-- PUT file://{escaped_csv_filename} @%{quoted_table};")
            sql_script.append(
                f"-- COPY INTO {quoted_table} FROM @%{quoted_table} "
                "FILE_FORMAT = (TYPE = CSV, SKIP_HEADER = 1, FIELD_OPTIONALLY_ENCLOSED_BY = '\"');"
            )
        elif flavor_lower == "bigquery":
            sql_script.append(
                f"-- bq load --source_format=CSV --skip_leading_rows=1 my_dataset.{table_name} '{escaped_csv_filename}'"
            )
        elif flavor_lower == "redshift":
            sql_script.append(
                f"-- COPY {quoted_table} FROM 's3://my-bucket/{escaped_csv_filename}' "
                f"IAM_ROLE 'arn:aws:iam::123456789012:role/MyRedshiftRole' "
                f"FORMAT AS CSV DELIMITER ',' IGNOREHEADER 1;"
            )
        elif flavor_lower == "mariadb":
            sql_script.append(
                f"-- LOAD DATA INFILE '{escaped_csv_filename}' INTO TABLE {quoted_table} "
                f"FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS;"
            )

    full_sql = "\n".join(sql_script) + "\n"

    if output_sql_path:
        with open(output_sql_path, "w", encoding="utf-8") as sql_file:
            sql_file.write(full_sql)

    return full_sql


def _is_outdated(source_path: str | os.PathLike[str], target_path: str | os.PathLike[str]) -> bool:
    """Check if the target file does not exist or is older than the source file."""
    if not os.path.exists(target_path):
        return True
    return os.path.getmtime(source_path) > os.path.getmtime(target_path)


def metadata_to_dict(meta: Any) -> dict[str, Any]:
    """Convert a pyreadstat metadata container to a dictionary."""
    meta_dict = {
        "column_names": getattr(meta, "column_names", []),
        "column_labels": getattr(meta, "column_labels", []),
        "column_names_to_labels": getattr(meta, "column_names_to_labels", {}),
        "file_label": getattr(meta, "file_label", None),
        "file_format": getattr(meta, "file_format", None),
        "number_of_rows": getattr(meta, "number_of_rows", None),
        "number_of_columns": getattr(meta, "number_of_columns", None),
        "variable_value_labels": getattr(meta, "variable_value_labels", {}),
        "value_labels": getattr(meta, "value_labels", {}),
        "original_variable_types": getattr(meta, "original_variable_types", {}),
        "readstat_variable_types": getattr(meta, "readstat_variable_types", {}),
        "table_name": getattr(meta, "table_name", None),
    }

    def clean_dict(d: Any) -> Any:
        if isinstance(d, dict):
            return {str(k): clean_dict(v) for k, v in d.items()}
        if isinstance(d, list):
            return [clean_dict(x) for x in d]
        return d

    return clean_dict(meta_dict)


def get_pyreadstat_reader(extension: str) -> Any:
    """Get the pyreadstat reader function for a given file extension."""
    import pyreadstat

    ext = extension.lower()
    if ext == ".sav":
        return pyreadstat.read_sav
    elif ext == ".zsav":
        return pyreadstat.read_sav
    elif ext == ".por":
        return pyreadstat.read_por
    elif ext == ".dta":
        return pyreadstat.read_dta
    elif ext == ".sas7bdat":
        return pyreadstat.read_sas7bdat
    elif ext == ".sas7bcat":
        return pyreadstat.read_sas7bcat
    elif ext in (".xport", ".xpt"):
        return pyreadstat.read_xport
    else:
        raise ValueError(f"Unsupported file extension: {extension}")


def read_stat_metadata(file_path: str | os.PathLike[str]) -> dict[str, Any]:
    """
    Reads a SAS, Stata, or SPSS file and extracts its metadata as a dictionary.

    Args:
        file_path: Path to the statistical data file.

    Returns:
        A dictionary containing the file metadata.
    """
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    _, ext = os.path.splitext(file_path)
    reader = get_pyreadstat_reader(ext)

    if ext.lower() == ".sas7bcat":
        meta = reader(file_path)
    else:
        _, meta = reader(file_path, metadataonly=True)

    return metadata_to_dict(meta)


def convert_stat_file_to_csv(
    file_path: str | os.PathLike[str],
    csv_path: str | os.PathLike[str] | None = None,
    overwrite: bool = False,
) -> str:
    """
    Converts a SAS, Stata, or SPSS file to a CSV file.

    Args:
        file_path: Path to the input SAS, Stata, or SPSS file.
        csv_path: Optional path to the output CSV file. Defaults to <input_file_name>.csv.
        overwrite: If True, forces conversion even if the target file is up-to-date.

    Returns:
        The path to the generated CSV file.
    """
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    if csv_path is None:
        csv_path = f"{file_path}.csv"
    else:
        csv_path = os.path.abspath(csv_path)

    if overwrite or _is_outdated(file_path, csv_path):
        _, ext = os.path.splitext(file_path)
        reader = get_pyreadstat_reader(ext)

        if ext.lower() == ".sas7bcat":
            import pandas as pd

            df = pd.DataFrame()
        else:
            df, _ = reader(file_path)

        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        df.to_csv(csv_path, index=False)

    return str(csv_path)


def export_stat_metadata_to_json(
    file_path: str | os.PathLike[str],
    json_path: str | os.PathLike[str] | None = None,
    overwrite: bool = False,
) -> str:
    """
    Extracts metadata from a SAS, Stata, or SPSS file and exports it to a JSON file.

    Args:
        file_path: Path to the input SAS, Stata, or SPSS file.
        json_path: Optional path to the output JSON file. Defaults to <input_file_name>.json.
        overwrite: If True, forces export even if the target file is up-to-date.

    Returns:
        The path to the generated JSON file.
    """
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    if json_path is None:
        json_path = f"{file_path}.json"
    else:
        json_path = os.path.abspath(json_path)

    if overwrite or _is_outdated(file_path, json_path):
        meta_dict = read_stat_metadata(file_path)

        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meta_dict, f, indent=2, ensure_ascii=False)

    return str(json_path)
