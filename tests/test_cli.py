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
