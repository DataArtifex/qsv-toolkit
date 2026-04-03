from dartfx.qsv.cmd import QSV


def test_qsv_version_output_contains_version_text() -> None:
    output = QSV(version=True).run().strip()
    assert output
    assert "qsv" in output.lower()
    assert "version" in output.lower() or any(ch.isdigit() for ch in output)
