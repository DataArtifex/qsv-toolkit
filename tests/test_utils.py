import os
import shutil
import xml.etree.ElementTree as ET

import pytest

from dartfx.qsv import generate_ddi_codebook
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
    ns = {"ddi": "ddi:codebook:2_5"}

    # Check docDscr and stdyDscr
    assert root.find(".//ddi:docDscr", ns) is not None
    assert root.find(".//ddi:stdyDscr", ns) is not None

    # Check fileDscr dimensions
    case_cnt = root.find(".//ddi:fileDscr/ddi:fileTxt/ddi:dimensns/ddi:caseCnt", ns)
    assert case_cnt is not None
    assert case_cnt.text == "4580"
    var_cnt = root.find(".//ddi:fileDscr/ddi:fileTxt/ddi:dimensns/ddi:varCnt", ns)
    assert var_cnt is not None
    assert var_cnt.text == "2"

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
    assert labl.text == "Urban or rural classification"

    # varFormat
    vf = urbrur_var.find("ddi:varFormat", ns)
    assert vf is not None
    assert vf.attrib["type"] == "numeric"
    assert vf.attrib["schema"] == "other"

    # Sum stats
    mean_stat = urbrur_var.find("ddi:sumStat[@type='mean']", ns)
    assert mean_stat is not None
    assert mean_stat.text == "1.859"

    # invld (0) and vald (4580)
    invld_stat = urbrur_var.find("ddi:sumStat[@type='invld']", ns)
    assert invld_stat is not None
    assert invld_stat.text == "0"
    vald_stat = urbrur_var.find("ddi:sumStat[@type='vald']", ns)
    assert vald_stat is not None
    assert vald_stat.text == "4580"

    # Category frequencies
    catgrys = urbrur_var.findall("ddi:catgry", ns)
    assert len(catgrys) == 2

    val_node0 = catgrys[0].find("ddi:catVal", ns)
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

    # invld (10) and vald (4570)
    invld_income = income_var.find("ddi:sumStat[@type='invld']", ns)
    assert invld_income is not None
    assert invld_income.text == "10"
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
    csv_path = "tests/data/sdc_test.csv"
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
    case_cnt = root.find(".//ddi:fileDscr/ddi:fileTxt/ddi:dimensns/ddi:caseCnt", ns)
    assert case_cnt is not None
    assert case_cnt.text is not None
    assert int(case_cnt.text) == 4580

    var_cnt = root.find(".//ddi:fileDscr/ddi:fileTxt/ddi:dimensns/ddi:varCnt", ns)
    assert var_cnt is not None
    assert var_cnt.text is not None
    assert int(var_cnt.text) == 20

    # sex should be categorical (cardinality 2 <= 5) and coded
    sex_var = root.find(".//ddi:dataDscr/ddi:var[@name='sex']", ns)
    assert sex_var is not None
    assert sex_var.attrib["intrvl"] == "discrete"
    assert sex_var.attrib["representationType"] == "coded"
    assert len(sex_var.findall("ddi:catgry", ns)) == 2

    # age should be continuous (cardinality 96 > 5) and numeric
    age_var = root.find(".//ddi:dataDscr/ddi:var[@name='age']", ns)
    assert age_var is not None
    assert age_var.attrib["intrvl"] == "contin"
    assert age_var.attrib["representationType"] == "numeric"
    assert len(age_var.findall("ddi:catgry", ns)) == 0  # No frequencies generated

    # Verify output file writing
    output_file = "tests/data/sdc_test_ddi.xml"
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
