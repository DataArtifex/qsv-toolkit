import dartfx.qsv.cmd as qsv_cmd
from dartfx.qsv.cmd import QSV


def test_qsv_version_output_contains_version_text() -> None:
    def fake_run_qsv_command(command: str, args: list[str]) -> str:
        assert command == ""
        assert args == ["--version"]
        return "qsv 0.124.0"

    qsv_cmd._run_qsv_command = fake_run_qsv_command
    output = QSV(version=True).run().strip()
    assert output
    assert "qsv" in output.lower()
    assert "version" in output.lower() or any(ch.isdigit() for ch in output)
