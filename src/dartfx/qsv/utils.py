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
