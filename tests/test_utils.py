import os
import shutil
import xml.etree.ElementTree as ET

import pytest

from dartfx.qsv import generate_ddi_codebook, generate_sql
from dartfx.qsv.model import QsvStatsDataModel

requires_qsv = pytest.mark.skipif(
    shutil.which("qsv") is None,
    reason="qsv CLI not installed",
)


def test_generate_ddi_codebook_static_dict():
    # Setup dummy static data
    stats_data = [
        {
            "field": "urbrur",
            "type": "Integer",
            "sum": 8514.0,
            "min": "1",
            "max": "2",
            "range": 1.0,
            "sort_order": "Unsorted",
            "sortiness": 0.9974,
            "mean": 1.859,
            "sem": 0.0051,
            "stddev": 0.3481,
            "variance": 0.1212,
            "cv": 18.724,
            "nullcount": 0,
            "n_negative": 0,
            "n_zero": 0,
            "n_positive": 4580,
            "sparsity": 0.0,
            "cardinality": 2,
        },
        {
            "field": "income",
            "type": "Float",
            "sum": 229529860215.962,
            "min": "2897.484",
            "max": "100000000.0",
            "range": 99997102.516,
            "mean": 50115690.0035,
            "stddev": 28905277.5319,
            "nullcount": 10,
            "cardinality": 4570,
            "max_precision": 3,
        },
    ]

    schema_data = {
        "properties": {
            "urbrur": {
                "description": "Urban or rural classification",
                "minimum": 1,
                "maximum": 2,
                "type": ["integer"],
                "enum": [1, 2],
            },
            "income": {
                "description": "Household income",
                "minimum": 2897.484,
                "maximum": 100000000.0,
                "type": ["number"],
            },
        }
    }

    frequency_data = {
        "rowcount": 4580,
        "fieldcount": 2,
        "fields": [
            {
                "field": "urbrur",
                "type": "Integer",
                "cardinality": 2,
                "nullcount": 0,
                "frequencies": [
                    {"value": "2", "count": 3934, "percentage": 85.8952, "rank": 1.0},
                    {"value": "1", "count": 646, "percentage": 14.1048, "rank": 2.0},
                ],
            }
        ],
    }

    # Test Version 2.5
    xml_str = generate_ddi_codebook(
        stats_data=stats_data,
        schema_data=schema_data,
        frequency_data=frequency_data,
        version="2.5",
    )

    assert "<?xml" in xml_str
    assert 'xmlns="ddi:codebook:2_5"' in xml_str
    assert 'version="2.5"' in xml_str

    root = ET.fromstring(xml_str)
    assert "ID" in root.attrib
    assert root.attrib["ID"].startswith("_")
    ns = {"ddi": "ddi:codebook:2_5"}

    doc_dscr = root.find(".//ddi:docDscr", ns)
    assert doc_dscr is not None
    softwares = doc_dscr.findall(".//ddi:software", ns)
    assert len(softwares) == 2
    software_names = [sw.text for sw in softwares]
    assert "QSV" in software_names
    assert "Data Artifex QSV Toolkit" in software_names
    assert root.find(".//ddi:stdyDscr", ns) is not None

    # Check fileDscr dimensions
    case_qnty = root.find(".//ddi:fileDscr/ddi:fileTxt/ddi:dimensns/ddi:caseQnty", ns)
    assert case_qnty is not None
    assert case_qnty.text == "4580"
    var_qnty = root.find(".//ddi:fileDscr/ddi:fileTxt/ddi:dimensns/ddi:varQnty", ns)
    assert var_qnty is not None
    assert var_qnty.text == "2"

    # Check variable details
    vars_list = root.findall(".//ddi:dataDscr/ddi:var", ns)
    assert len(vars_list) == 2

    # Var 1: urbrur (discrete, coded, dcml should not be present since not in stats_row)
    urbrur_var = root.find(".//ddi:dataDscr/ddi:var[@name='urbrur']", ns)
    assert urbrur_var is not None
    assert urbrur_var.attrib["intrvl"] == "discrete"
    assert urbrur_var.attrib["representationType"] == "coded"
    assert "dcml" not in urbrur_var.attrib

    # Labl
    labl = urbrur_var.find("ddi:labl", ns)
    assert labl is not None
    assert labl.text == "urbrur"

    # varFormat
    vf = urbrur_var.find("ddi:varFormat", ns)
    assert vf is not None
    assert vf.attrib["type"] == "numeric"
    assert vf.attrib["schema"] == "other"
    assert vf.attrib["otherSchema"] == "qsv"
    assert vf.attrib["formatname"] == "Integer"

    # Sum stats
    mean_stat = urbrur_var.find("ddi:sumStat[@type='mean']", ns)
    assert mean_stat is not None
    assert mean_stat.text == "1.859"

    # invd (0) and vald (4580)
    invd_stat = urbrur_var.find("ddi:sumStat[@type='invd']", ns)
    assert invd_stat is not None
    assert invd_stat.text == "0"
    vald_stat = urbrur_var.find("ddi:sumStat[@type='vald']", ns)
    assert vald_stat is not None
    assert vald_stat.text == "4580"

    # Category frequencies
    catgrys = urbrur_var.findall("ddi:catgry", ns)
    assert len(catgrys) == 2

    val_node0 = catgrys[0].find("ddi:catValu", ns)
    assert val_node0 is not None
    assert val_node0.text == "2"

    freq_node0 = catgrys[0].find("ddi:catStat[@type='freq']", ns)
    assert freq_node0 is not None
    assert freq_node0.text == "3934"

    pct_node0 = catgrys[0].find("ddi:catStat[@type='percent']", ns)
    assert pct_node0 is not None
    assert pct_node0.text == "85.8952"

    # Var 2: income (contin, numeric, dcml="3")
    income_var = root.find(".//ddi:dataDscr/ddi:var[@name='income']", ns)
    assert income_var is not None
    assert income_var.attrib["intrvl"] == "contin"
    assert income_var.attrib["representationType"] == "numeric"
    assert income_var.attrib["dcml"] == "3"

    vf_income = income_var.find("ddi:varFormat", ns)
    assert vf_income is not None
    assert vf_income.attrib["type"] == "numeric"
    assert vf_income.attrib["schema"] == "other"
    assert vf_income.attrib["otherSchema"] == "qsv"
    assert vf_income.attrib["formatname"] == "Float"

    # invd (10) and vald (4570)
    invd_income = income_var.find("ddi:sumStat[@type='invd']", ns)
    assert invd_income is not None
    assert invd_income.text == "10"
    vald_income = income_var.find("ddi:sumStat[@type='vald']", ns)
    assert vald_income is not None
    assert vald_income.text == "4570"

    # Check Version 2.6
    xml_str_26 = generate_ddi_codebook(
        stats_data=stats_data,
        schema_data=schema_data,
        frequency_data=frequency_data,
        version="2.6",
    )
    assert 'xmlns="ddi:codebook:2_6"' in xml_str_26
    assert 'version="2.6"' in xml_str_26


def test_generate_ddi_codebook_pydantic_stats():
    # Test using list of QsvStatsDataModel objects
    stats_obj = QsvStatsDataModel(
        field="urbrur",
        type="Integer",
        sum=8514.0,
        min="1",
        max="2",
        range=1.0,
        nullcount=0,
        cardinality=2,
    )
    schema_data = {
        "properties": {
            "urbrur": {
                "type": ["integer"],
            }
        }
    }
    xml_str = generate_ddi_codebook(
        stats_data=[stats_obj],
        schema_data=schema_data,
        version="2.5",
    )
    assert 'name="urbrur"' in xml_str
    assert 'otherType="sum">8514.0' in xml_str


@requires_qsv
def test_generate_ddi_codebook_dynamic_qsv():
    csv_path = "tests/data/sdc/sdc_test.csv"
    assert os.path.exists(csv_path)

    # Run dynamically
    xml_str = generate_ddi_codebook(
        csv_path=csv_path,
        version="2.5",
        categorical_threshold=5,  # columns with card <= 5 (like urbrur, roof,
        # walls, electcon, sex, hhcivil, etc.) will have frequencies computed
    )

    assert "<?xml" in xml_str
    assert 'xmlns="ddi:codebook:2_5"' in xml_str

    root = ET.fromstring(xml_str)
    ns = {"ddi": "ddi:codebook:2_5"}

    # Verify filename
    file_name_node = root.find(".//ddi:fileDscr/ddi:fileTxt/ddi:fileName", ns)
    assert file_name_node is not None
    assert file_name_node.text == "sdc_test.csv"

    # Verify cases and variables
    case_qnty = root.find(".//ddi:fileDscr/ddi:fileTxt/ddi:dimensns/ddi:caseQnty", ns)
    assert case_qnty is not None
    assert case_qnty.text is not None
    assert int(case_qnty.text) == 4580

    var_qnty = root.find(".//ddi:fileDscr/ddi:fileTxt/ddi:dimensns/ddi:varQnty", ns)
    assert var_qnty is not None
    assert var_qnty.text is not None
    assert int(var_qnty.text) == 20

    # sex should be categorical (cardinality 2 <= 5) and coded
    sex_var = root.find(".//ddi:dataDscr/ddi:var[@name='sex']", ns)
    assert sex_var is not None
    assert sex_var.attrib["intrvl"] == "discrete"
    assert sex_var.attrib["representationType"] == "coded"
    assert len(sex_var.findall("ddi:catgry", ns)) == 2

    # age should be discrete (since it is an integer) and numeric
    age_var = root.find(".//ddi:dataDscr/ddi:var[@name='age']", ns)
    assert age_var is not None
    assert age_var.attrib["intrvl"] == "discrete"
    assert age_var.attrib["representationType"] == "numeric"
    assert len(age_var.findall("ddi:catgry", ns)) == 0  # No frequencies generated

    # Verify output file writing
    output_file = "tests/data/sdc/sdc_test_ddi.xml"
    if os.path.exists(output_file):
        os.remove(output_file)

    generate_ddi_codebook(
        csv_path=csv_path,
        version="2.5",
        categorical_threshold=5,
        output_xml_path=output_file,
    )

    assert os.path.exists(output_file)
    with open(output_file, encoding="utf-8") as f:
        written_content = f.read()
    assert 'xmlns="ddi:codebook:2_5"' in written_content

    os.remove(output_file)


def test_generate_sql_static_postgres():
    schema_data = {
        "properties": {
            "id-field": {"type": ["integer"], "minimum": 1, "maximum": 10},
            "name": {"type": ["string"], "maxLength": 100},
            "is_active": {"type": ["boolean"]},
            "created_at": {"type": ["string"], "format": "date-time"},
        },
        "required": ["id-field"],
    }

    sql = generate_sql(
        csv_path="/some/full/path/to/test_data.csv",
        schema_data=schema_data,
        flavor="postgres",
        table_name="Users",
        schema_name="my_schema",
    )

    from dartfx.qsv.__about__ import __version__ as toolkit_version

    assert f"-- Generated by dartfx-qsv tosql {toolkit_version}" in sql
    assert 'CREATE TABLE "my_schema"."Users"' in sql
    assert '"id-field" SMALLINT' in sql
    assert '"name" VARCHAR(100)' in sql
    assert '"is_active" BOOLEAN' in sql
    assert '"created_at" TIMESTAMP' in sql
    assert "/*" in sql
    assert 'COPY "my_schema"."Users" FROM \'test_data.csv\'' in sql
    assert '\\copy "my_schema"."Users" FROM \'test_data.csv\'' in sql
    assert "*/" in sql
    assert "/some/full/path" not in sql


def test_generate_sql_static_sqlite_mysql():
    schema_data = {
        "properties": {
            "big_num": {"type": ["integer"], "minimum": 1, "maximum": 100000000000},
            "price": {"type": ["number"]},
            "notes": {"type": ["string"]},
        }
    }

    # SQLite
    sqlite_sql = generate_sql(csv_path="/another/dir/my_file.csv", schema_data=schema_data, flavor="sqlite")
    assert 'CREATE TABLE "tbl_my_file"' in sqlite_sql
    assert '"big_num" INTEGER' in sqlite_sql
    assert '"price" REAL' in sqlite_sql
    assert '"notes" TEXT' in sqlite_sql
    assert "-- .import 'my_file.csv' \"tbl_my_file\" --csv" in sqlite_sql
    assert "/another/dir" not in sqlite_sql

    # MySQL
    mysql_sql = generate_sql(csv_path="/another/dir/my_file.csv", schema_data=schema_data, flavor="mysql")
    assert "CREATE TABLE `tbl_my_file`" in mysql_sql
    assert "`big_num` BIGINT" in mysql_sql
    assert "`price` DOUBLE" in mysql_sql
    assert "`notes` TEXT" in mysql_sql
    assert "-- LOAD DATA INFILE 'my_file.csv' INTO TABLE `tbl_my_file`" in mysql_sql
    assert "/another/dir" not in mysql_sql


def test_generate_sql_invalid_flavor():
    with pytest.raises(ValueError, match="Unsupported flavor"):
        generate_sql(csv_path="dummy.csv", flavor="unsupported-db")


def test_generate_sql_primary_key():
    schema_data = {
        "properties": {
            "id-field": {"type": ["integer"]},
            "name": {"type": ["string"]},
            "is_active": {"type": ["boolean"]},
        }
    }

    # Test single PK with case-insensitive validation
    sql_postgres = generate_sql(
        csv_path="test_data.csv", schema_data=schema_data, flavor="postgres", primary_key="ID-FIELD"
    )
    assert 'PRIMARY KEY ("id-field")' in sql_postgres

    # Test composite PK (comma-separated string)
    sql_mysql = generate_sql(
        csv_path="test_data.csv", schema_data=schema_data, flavor="mysql", primary_key="id-field, NAME"
    )
    assert "PRIMARY KEY (`id-field`, `name`)" in sql_mysql

    # Test composite PK (list of strings)
    sql_mssql = generate_sql(
        csv_path="test_data.csv", schema_data=schema_data, flavor="mssql", primary_key=["ID-FIELD", "name"]
    )
    assert "PRIMARY KEY ([id-field], [name])" in sql_mssql

    # Test validation error for non-existent field
    with pytest.raises(ValueError, match="Primary key field 'non-existent' does not exist"):
        generate_sql(csv_path="test_data.csv", schema_data=schema_data, primary_key="non-existent")


def test_generate_sql_static_new_flavors():
    schema_data = {
        "properties": {
            "id": {"type": ["integer"], "minimum": 0, "maximum": 200},
            "age": {"type": ["integer"], "minimum": -50, "maximum": 50},
            "big_val": {"type": ["integer"], "minimum": 1, "maximum": 100000000000},
            "name": {"type": ["string"], "maxLength": 50},
            "ratio": {"type": ["number"]},
            "active": {"type": ["boolean"]},
            "created": {"type": ["string"], "format": "date-time"},
        }
    }

    # MSSQL
    mssql_sql = generate_sql(csv_path="/some/path/my_file.csv", schema_data=schema_data, flavor="mssql")
    assert "CREATE TABLE [tbl_my_file]" in mssql_sql
    assert "[id] SMALLINT" in mssql_sql
    assert "[big_val] BIGINT" in mssql_sql
    assert "[name] VARCHAR(50)" in mssql_sql
    assert "[ratio] FLOAT" in mssql_sql
    assert "[active] BIT" in mssql_sql
    assert "[created] DATETIME2" in mssql_sql
    assert "-- BULK INSERT [tbl_my_file] FROM 'my_file.csv'" in mssql_sql
    assert "/some/path" not in mssql_sql

    # Oracle
    oracle_sql = generate_sql(csv_path="/some/path/my_file.csv", schema_data=schema_data, flavor="oracle")
    assert 'CREATE TABLE "tbl_my_file"' in oracle_sql
    assert '"id" INTEGER' in oracle_sql
    assert '"name" VARCHAR2(50)' in oracle_sql
    assert '"ratio" DOUBLE PRECISION' in oracle_sql
    assert '"active" NUMBER(1)' in oracle_sql
    assert '"created" TIMESTAMP' in oracle_sql
    assert "-- SQL*Loader Control File Syntax:" in oracle_sql
    assert "-- INFILE 'my_file.csv'" in oracle_sql
    assert "/some/path" not in oracle_sql

    # ClickHouse
    ch_sql = generate_sql(csv_path="/some/path/my_file.csv", schema_data=schema_data, flavor="clickhouse")
    assert 'CREATE TABLE "tbl_my_file"' in ch_sql
    assert '"id" UInt8' in ch_sql
    assert '"age" Int8' in ch_sql
    assert '"big_val" UInt64' in ch_sql
    assert '"name" String' in ch_sql
    assert '"ratio" Float64' in ch_sql
    assert '"active" Bool' in ch_sql
    assert '"created" DateTime' in ch_sql
    assert "-- clickhouse-client --query='INSERT INTO \"tbl_my_file\" FORMAT CSVWithNames' < 'my_file.csv'" in ch_sql
    assert "/some/path" not in ch_sql

    # DuckDB
    duck_sql = generate_sql(csv_path="/some/path/my_file.csv", schema_data=schema_data, flavor="duckdb")
    assert 'CREATE TABLE "tbl_my_file"' in duck_sql
    assert '"id" SMALLINT' in duck_sql
    assert '"age" SMALLINT' in duck_sql
    assert '"big_val" BIGINT' in duck_sql
    assert '"name" VARCHAR' in duck_sql
    assert '"ratio" DOUBLE' in duck_sql
    assert '"active" BOOLEAN' in duck_sql
    assert '"created" TIMESTAMP' in duck_sql
    assert "-- COPY \"tbl_my_file\" FROM 'my_file.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');" in duck_sql
    assert "-- OR: INSERT INTO \"tbl_my_file\" SELECT * FROM read_csv_auto('my_file.csv');" in duck_sql
    assert "/some/path" not in duck_sql

    # Snowflake
    sf_sql = generate_sql(csv_path="/some/path/my_file.csv", schema_data=schema_data, flavor="snowflake")
    assert 'CREATE TABLE "tbl_my_file"' in sf_sql
    assert '"id" SMALLINT' in sf_sql
    assert '"name" VARCHAR(50)' in sf_sql
    assert '"ratio" DOUBLE' in sf_sql
    assert '"created" TIMESTAMP_NTZ' in sf_sql
    assert '-- PUT file://my_file.csv @%"tbl_my_file";' in sf_sql
    expected_sf_copy = (
        '-- COPY INTO "tbl_my_file" FROM @%"tbl_my_file" '
        "FILE_FORMAT = (TYPE = CSV, SKIP_HEADER = 1, FIELD_OPTIONALLY_ENCLOSED_BY = '\"');"
    )
    assert expected_sf_copy in sf_sql
    assert "/some/path" not in sf_sql

    # BigQuery
    bq_sql = generate_sql(csv_path="/some/path/my_file.csv", schema_data=schema_data, flavor="bigquery")
    assert "CREATE TABLE `tbl_my_file`" in bq_sql
    assert "`id` INT64" in bq_sql
    assert "`name` STRING" in bq_sql
    assert "`ratio` FLOAT64" in bq_sql
    assert "`created` DATETIME" in bq_sql
    assert "-- bq load --source_format=CSV --skip_leading_rows=1 my_dataset.tbl_my_file 'my_file.csv'" in bq_sql
    assert "/some/path" not in bq_sql

    # Redshift
    rs_sql = generate_sql(csv_path="/some/path/my_file.csv", schema_data=schema_data, flavor="redshift")
    assert 'CREATE TABLE "tbl_my_file"' in rs_sql
    assert '"id" SMALLINT' in rs_sql
    assert '"name" VARCHAR(50)' in rs_sql
    assert '"ratio" DOUBLE PRECISION' in rs_sql
    assert '"created" TIMESTAMP' in rs_sql
    expected_rs_copy = (
        "-- COPY \"tbl_my_file\" FROM 's3://my-bucket/my_file.csv' "
        "IAM_ROLE 'arn:aws:iam::123456789012:role/MyRedshiftRole' "
        "FORMAT AS CSV DELIMITER ',' IGNOREHEADER 1;"
    )
    assert expected_rs_copy in rs_sql
    assert "/some/path" not in rs_sql

    # MariaDB
    maria_sql = generate_sql(csv_path="/some/path/my_file.csv", schema_data=schema_data, flavor="mariadb")
    assert "CREATE TABLE `tbl_my_file`" in maria_sql
    assert "`id` SMALLINT" in maria_sql
    assert "`name` VARCHAR(50)" in maria_sql
    assert "`ratio` DOUBLE" in maria_sql
    assert "`created` DATETIME" in maria_sql
    expected_maria_load = (
        "-- LOAD DATA INFILE 'my_file.csv' INTO TABLE `tbl_my_file` "
        "FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS;"
    )
    assert expected_maria_load in maria_sql
    assert "/some/path" not in maria_sql


@requires_qsv
def test_generate_sql_dynamic(tmp_path):
    csv_path = "tests/data/sdc/sdc_test.csv"
    sql = generate_sql(csv_path=csv_path, flavor="postgres")

    assert 'CREATE TABLE "tbl_sdc_test"' in sql
    assert '"sex" VARCHAR(1)' in sql
    assert '"sampling_weight" SMALLINT' in sql or '"sampling_weight" INTEGER' in sql
    assert '"income" DOUBLE PRECISION' in sql

    # Test output file
    out_file = tmp_path / "test_out.sql"
    generate_sql(csv_path=csv_path, flavor="postgres", output_sql_path=out_file)
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert 'CREATE TABLE "tbl_sdc_test"' in content


def test_stat_file_conversion_and_metadata(tmp_path):
    import json
    import os

    import pandas as pd
    import pyreadstat

    from dartfx.qsv import convert_stat_file_to_csv, export_stat_metadata_to_json, read_stat_metadata

    # 1. Create a dummy dataframe
    df = pd.DataFrame({"id": [1.0, 2.0, 3.0], "name": ["Alice", "Bob", "Charlie"], "age": [25.0, 30.0, 35.0]})

    # Define labels
    column_labels = ["Identifier", "Name of person", "Age of person"]
    variable_value_labels = {"id": {1.0: "First", 2.0: "Second", 3.0: "Third"}}

    # 2. Write to a temporary SPSS (.sav) file
    sav_file = tmp_path / "test_data.sav"
    pyreadstat.write_sav(df, str(sav_file), column_labels=column_labels, variable_value_labels=variable_value_labels)

    # Verify SPSS file exists
    assert sav_file.exists()

    # 3. Test read_stat_metadata
    meta = read_stat_metadata(sav_file)
    assert meta["column_names"] == ["id", "name", "age"]
    assert meta["column_labels"] == column_labels
    assert "id" in meta["variable_value_labels"]

    # 4. Test convert_stat_file_to_csv and export_stat_metadata_to_json
    csv_path = convert_stat_file_to_csv(sav_file)
    json_path = export_stat_metadata_to_json(sav_file)

    assert os.path.exists(csv_path)
    assert os.path.exists(json_path)
    assert csv_path == f"{sav_file}.csv"
    assert json_path == f"{sav_file}.json"

    # Verify CSV content
    converted_df = pd.read_csv(csv_path)
    assert list(converted_df.columns) == ["id", "name", "age"]
    assert list(converted_df["name"]) == ["Alice", "Bob", "Charlie"]

    # Verify JSON content
    with open(json_path, encoding="utf-8") as f:
        meta_json = json.load(f)
    assert meta_json["column_names"] == ["id", "name", "age"]
    assert meta_json["column_labels"] == column_labels

    # 5. Verify outdated check
    # Modify CSV to verify it's not overwritten unless overwrite=True or source modified
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("id,name,age\n99,Mock,99\n")

    # If we call convert_stat_file_to_csv now without overwrite, it should NOT overwrite because the CSV is newer
    convert_stat_file_to_csv(sav_file)
    with open(csv_path, encoding="utf-8") as f:
        content = f.read()
    assert "Mock" in content  # untouched because it wasn't outdated

    # If we call it with overwrite=True, it should overwrite
    convert_stat_file_to_csv(sav_file, overwrite=True)
    with open(csv_path, encoding="utf-8") as f:
        content = f.read()
    assert "Mock" not in content
    assert "Alice" in content

    # 6. Verify error on invalid extension
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("dummy")
    with pytest.raises(ValueError, match="Unsupported file extension"):
        read_stat_metadata(bad_file)
