from __future__ import annotations

import os
import shutil
import xml.etree.ElementTree as ET

import pytest
from typer.testing import CliRunner

from dartfx.qsc.cli import app

runner = CliRunner()

requires_qsv = pytest.mark.skipif(
    shutil.which("qsv") is None,
    reason="qsv CLI not installed",
)


def test_cli_help() -> None:
    """Test that main command and toddic subcommand help works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "toddic" in result.stdout
    assert "Dartfx CLI for QSV tools" in result.stdout

    result = runner.invoke(app, ["toddic", "--help"])
    assert result.exit_code == 0
    assert "Generate a DDI-Codebook XML document" in result.stdout
    assert "CSV_PATH" in result.stdout


def test_cli_toddic_precomputed(tmp_path: str) -> None:
    """Test toddic using pre-computed files (no QSV CLI dependency required)."""
    csv_path = "tests/data/sdc_test.csv"
    stats_path = "tests/data/sdc_test.stats.csv.data.jsonl"
    schema_path = "tests/data/sdc_test.csv.schema.json"

    # Verify input paths exist
    assert os.path.exists(csv_path)
    assert os.path.exists(stats_path)
    assert os.path.exists(schema_path)

    # Test output to stdout
    result = runner.invoke(
        app,
        [
            "toddic",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "-v",
            "2.6",
        ],
    )
    assert result.exit_code == 0
    assert "<?xml" in result.stdout
    assert 'xmlns="ddi:codebook:2_6"' in result.stdout
    assert 'version="2.6"' in result.stdout

    # Test output to file
    out_xml = os.path.join(tmp_path, "precomputed_output.xml")
    result = runner.invoke(
        app,
        [
            "toddic",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "-o",
            out_xml,
            "-t",
            "10",
        ],
    )
    assert result.exit_code == 0
    assert os.path.exists(out_xml)

    with open(out_xml, encoding="utf-8") as f:
        content = f.read()

    assert "<?xml" in content
    assert 'xmlns="ddi:codebook:2_6"' in content
    root = ET.fromstring(content)
    ns = {"ddi": "ddi:codebook:2_6"}
    assert root.find(".//ddi:docDscr", ns) is not None
    # Verify varFormat is populated
    vf = root.find(".//ddi:dataDscr/ddi:var/ddi:varFormat", ns)
    assert vf is not None
    assert vf.attrib["type"] in ("numeric", "character")
    assert vf.attrib["schema"] == "other"
    assert vf.attrib["otherSchema"] == "qsv"
    assert "formatname" in vf.attrib


@requires_qsv
def test_cli_toddic_dynamic(tmp_path: str) -> None:
    """Test toddic with dynamic QSV run."""
    csv_path = "tests/data/sdc_test.csv"
    assert os.path.exists(csv_path)

    # Output to stdout
    result = runner.invoke(
        app,
        [
            "toddic",
            csv_path,
            "-v",
            "2.5",
            "-t",
            "5",
            "-c",
            "sex",
            "-c",
            "roof,walls",
        ],
    )
    assert result.exit_code == 0
    assert "<?xml" in result.stdout
    assert 'xmlns="ddi:codebook:2_5"' in result.stdout

    # Output to file
    out_xml = os.path.join(tmp_path, "dynamic_output.xml")
    result = runner.invoke(
        app,
        [
            "toddic",
            csv_path,
            "-o",
            out_xml,
            "-t",
            "5",
        ],
    )
    assert result.exit_code == 0
    assert os.path.exists(out_xml)

    with open(out_xml, encoding="utf-8") as f:
        content = f.read()
    assert 'xmlns="ddi:codebook:2_6"' in content


def test_cli_toddic_invalid_csv() -> None:
    """Test that passing a non-existent CSV path fails validation."""
    result = runner.invoke(app, ["toddic", "nonexistent_file.csv"])
    assert result.exit_code != 0


def test_cli_tosql_help() -> None:
    """Test tosql CLI help output."""
    result = runner.invoke(app, ["tosql", "--help"])
    assert result.exit_code == 0
    assert "Generate a SQL script to host a CSV file" in result.stdout
    assert "CSV_PATH" in result.stdout
    assert "--flavor" in result.stdout
    assert "--table" in result.stdout


def test_cli_tosql_precomputed(tmp_path: str) -> None:
    """Test tosql using pre-computed schema/stats files."""
    csv_path = "tests/data/sdc_test.csv"
    stats_path = "tests/data/sdc_test.stats.csv.data.jsonl"
    schema_path = "tests/data/sdc_test.csv.schema.json"

    # Test output to stdout
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "postgres",
            "--table",
            "MyCustomTable",
            "--schema",
            "MyCustomSchema",
        ],
    )
    assert result.exit_code == 0
    assert 'CREATE TABLE "MyCustomSchema"."MyCustomTable"' in result.stdout
    assert '"sex" VARCHAR(1)' in result.stdout

    # Test output to file
    out_sql = os.path.join(tmp_path, "precomputed_output.sql")
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "sqlite",
            "-o",
            out_sql,
        ],
    )
    assert result.exit_code == 0
    assert os.path.exists(out_sql)

    with open(out_sql, encoding="utf-8") as f:
        content = f.read()

    assert 'CREATE TABLE "tbl_sdc_test"' in content
    assert '"sex" TEXT' in content


@requires_qsv
def test_cli_tosql_dynamic(tmp_path: str) -> None:
    """Test tosql command with dynamic QSV run."""
    csv_path = "tests/data/sdc_test.csv"
    assert os.path.exists(csv_path)

    # Output to stdout
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--flavor",
            "mysql",
        ],
    )
    assert result.exit_code == 0
    assert "CREATE TABLE `tbl_sdc_test`" in result.stdout
    assert "`sex` VARCHAR(1)" in result.stdout

    # Output to file
    out_sql = os.path.join(tmp_path, "dynamic_output.sql")
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "-o",
            out_sql,
            "--flavor",
            "postgres",
        ],
    )
    assert result.exit_code == 0
    assert os.path.exists(out_sql)

    with open(out_sql, encoding="utf-8") as f:
        content = f.read()
    assert 'CREATE TABLE "tbl_sdc_test"' in content


def test_cli_tosql_new_flavors_precomputed() -> None:
    """Test tosql CLI command with new flavors using pre-computed schema/stats files."""
    csv_path = "tests/data/sdc_test.csv"
    stats_path = "tests/data/sdc_test.stats.csv.data.jsonl"
    schema_path = "tests/data/sdc_test.csv.schema.json"

    # MSSQL
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "mssql",
        ],
    )
    assert result.exit_code == 0
    assert "CREATE TABLE [tbl_sdc_test]" in result.stdout
    assert "[sex] VARCHAR(1)" in result.stdout
    assert "-- BULK INSERT [tbl_sdc_test]" in result.stdout

    # Oracle
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "oracle",
        ],
    )
    assert result.exit_code == 0
    assert 'CREATE TABLE "tbl_sdc_test"' in result.stdout
    assert '"sex" VARCHAR2(1)' in result.stdout
    assert "-- SQL*Loader Control File Syntax" in result.stdout

    # ClickHouse
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "clickhouse",
        ],
    )
    assert result.exit_code == 0
    assert 'CREATE TABLE "tbl_sdc_test"' in result.stdout
    assert '"sex" String' in result.stdout
    assert "-- clickhouse-client --query='INSERT INTO \"tbl_sdc_test\" FORMAT CSVWithNames' < '" in result.stdout

    # DuckDB
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "duckdb",
        ],
    )
    assert result.exit_code == 0
    assert 'CREATE TABLE "tbl_sdc_test"' in result.stdout
    assert '"sex" VARCHAR' in result.stdout
    assert "-- COPY \"tbl_sdc_test\" FROM 'sdc_test.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');" in result.stdout
    assert "-- OR: INSERT INTO \"tbl_sdc_test\" SELECT * FROM read_csv_auto('sdc_test.csv');" in result.stdout

    # Snowflake
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "snowflake",
        ],
    )
    assert result.exit_code == 0
    assert 'CREATE TABLE "tbl_sdc_test"' in result.stdout
    assert '"sex" VARCHAR(1)' in result.stdout
    assert '-- PUT file://sdc_test.csv @%"tbl_sdc_test";' in result.stdout

    # BigQuery
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "bigquery",
        ],
    )
    assert result.exit_code == 0
    assert "CREATE TABLE `tbl_sdc_test`" in result.stdout
    assert "`sex` STRING" in result.stdout
    assert (
        "-- bq load --source_format=CSV --skip_leading_rows=1 my_dataset.tbl_sdc_test 'sdc_test.csv'" in result.stdout
    )

    # Redshift
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "redshift",
        ],
    )
    assert result.exit_code == 0
    assert 'CREATE TABLE "tbl_sdc_test"' in result.stdout
    assert '"sex" VARCHAR(1)' in result.stdout
    assert "-- COPY \"tbl_sdc_test\" FROM 's3://my-bucket/sdc_test.csv'" in result.stdout

    # MariaDB
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--flavor",
            "mariadb",
        ],
    )
    assert result.exit_code == 0
    assert "CREATE TABLE `tbl_sdc_test`" in result.stdout
    assert "`sex` VARCHAR(1)" in result.stdout
    expected_maria_load = (
        "-- LOAD DATA INFILE 'sdc_test.csv' INTO TABLE `tbl_sdc_test` "
        "FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS;"
    )
    assert expected_maria_load in result.stdout


def test_cli_tosql_primary_key() -> None:
    """Test tosql CLI command with primary-key option."""
    csv_path = "tests/data/sdc_test.csv"
    stats_path = "tests/data/sdc_test.stats.csv.data.jsonl"
    schema_path = "tests/data/sdc_test.csv.schema.json"

    # Test single PK with case insensitivity
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "-pk",
            "SEX",
        ],
    )
    assert result.exit_code == 0
    assert 'PRIMARY KEY ("sex")' in result.stdout

    # Test composite PK
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "--primary-key",
            "age_5yr, AGE_10YR",
        ],
    )
    assert result.exit_code == 0
    assert 'PRIMARY KEY ("age_5yr", "age_10yr")' in result.stdout

    # Test invalid PK validation error
    result = runner.invoke(
        app,
        [
            "tosql",
            csv_path,
            "--stats-data",
            stats_path,
            "--schema-data",
            schema_path,
            "-pk",
            "non_existent_column",
        ],
    )
    assert result.exit_code != 0
    err_msg = "Primary key field 'non_existent_column' does not exist"
    assert err_msg in result.stderr or err_msg in result.stdout
