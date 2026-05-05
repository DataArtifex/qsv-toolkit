import re
import shutil
from unittest.mock import patch

import pytest

from dartfx.qsv.cmd import QSV, Apply, Count, Stats

requires_qsv = pytest.mark.skipif(
    shutil.which("qsv") is None,
    reason="qsv CLI not installed",
)


def test_qsv_commands_list():
    commands = QSV.commands()
    assert len(commands) >= 71
    assert any(cmd.__name__ == "Apply" for cmd in commands)
    assert any(cmd.__name__ == "Stats" for cmd in commands)
    assert any(cmd.__name__ == "Blake3" for cmd in commands)


@requires_qsv
def test_qsv_list():
    commands = QSV.list()
    assert len(commands) >= 71
    # Check for a few well-known commands
    names = [c["name"] for c in commands]
    assert "apply" in names
    assert "stats" in names
    assert "count" in names
    # Verify structure
    for cmd in commands:
        assert "name" in cmd
        assert "description" in cmd
        assert isinstance(cmd["name"], str)
        assert isinstance(cmd["description"], str)


@requires_qsv
def test_env_list():
    env_vars = QSV.envlist()
    # There should at least be QSV_DESCRIBEGPT_DB_ENGINE in the user's environment
    assert len(env_vars) >= 1
    # Verify structure
    for var in env_vars:
        assert "name" in var
        assert "value" in var
        assert isinstance(var["name"], str)
        assert isinstance(var["value"], str)


@requires_qsv
def test_qsv_version():
    v = QSV.version()
    assert "qsv" in v.lower()
    assert any(ch.isdigit() for ch in v)


@requires_qsv
def test_qsv_version_number():
    vn = QSV.version_number()
    # Should be something like 19.1.0

    assert re.match(r"^\d+\.\d+\.\d+$", vn)


def test_command_name():
    assert Apply.name() == "apply"
    assert Stats.name() == "stats"


def test_get_args_boolean():
    cmd = Count(human_readable=True, json=True)
    args = cmd._get_args()
    assert "--human-readable" in args
    assert "--json" in args


def test_get_args_string():
    cmd = Stats(select="col1,col2")
    args = cmd._get_args()
    assert "--select" in args
    assert "col1,col2" in args


def test_get_args_special_mapping():
    cmd = Stats(round_places=2)
    args = cmd._get_args()
    assert "--round" in args
    assert "2" in args


def test_apply_run_args():
    with patch("dartfx.qsv.cmd._run_qsv_command", return_value="ok") as mock_run:
        apply_cmd = Apply(subcommand="operations", arg="upper", column="name")
        apply_cmd.run("test.csv")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][1]
        assert args[0] == "operations"
        assert args[1] == "upper"
        assert args[2] == "name"
        assert args[3] == "test.csv"
