import re
import shutil
from unittest.mock import patch

import pytest

from dartfx.qsv.cmd import QSV, Apply, Count, Profile, Stats, Synthesize

requires_qsv = pytest.mark.skipif(
    shutil.which("qsv") is None,
    reason="qsv CLI not installed",
)


def test_qsv_commands_list():
    commands = QSV.commands()
    assert len(commands) >= 60
    assert any(cmd.__name__ == "Apply" for cmd in commands)
    assert any(cmd.__name__ == "Stats" for cmd in commands)
    assert any(cmd.__name__ == "Blake3" for cmd in commands)


@requires_qsv
def test_qsv_list():
    commands = QSV.list()
    assert len(commands) >= 60
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
    # envlist can be empty depending on the environment
    assert len(env_vars) >= 0
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


def test_new_commands():
    assert Profile.name() == "profile"
    assert Synthesize.name() == "synthesize"

    cmd_profile = Profile(spec="dataset.yaml", no_dcat=True)
    args = cmd_profile._get_args()
    assert "--spec" in args
    assert "dataset.yaml" in args
    assert "--no-dcat" in args

    cmd_synthesize = Synthesize(rows=500, seed=42)
    args = cmd_synthesize._get_args()
    assert "--rows" in args
    assert "500" in args
    assert "--seed" in args
    assert "42" in args


def test_clean_get_viz_wrappers():
    from dartfx.qsv.cmd import Clean, Get, Viz

    assert Clean.name() == "clean"
    assert Get.name() == "get"
    assert Viz.name() == "viz"

    cmd_clean = Clean(force=True, stale=True)
    args = cmd_clean._get_args()
    assert "--force" in args
    assert "--stale" in args

    cmd_get = Get("cache-fetch", "data.csv", output="test.csv")
    args = cmd_get._get_args()
    assert "--output" in args
    assert "test.csv" in args
    assert cmd_get.init_args == ["cache-fetch", "data.csv"]

    cmd_viz = Viz(subcommand="smart", smarter=True)
    args = cmd_viz._get_args()
    assert "--smarter" in args
    assert cmd_viz.init_args == ["smart"]


def test_denull_fixedwidth_readstat_writestat_wrappers():
    from dartfx.qsv.cmd import Denull, FixedWidth, ReadStat, WriteStat

    assert Denull.name() == "denull"
    assert FixedWidth.name() == "fixedwidth"
    assert ReadStat.name() == "readstat"
    assert WriteStat.name() == "writestat"

    cmd_denull = Denull(apply=True, max_distinct=32, json=True)
    args = cmd_denull._get_args()
    assert "--apply" in args
    assert "--max-distinct" in args
    assert "32" in args
    assert "--json" in args

    cmd_fw = FixedWidth(positions="1,10,25", output="out.csv")
    args = cmd_fw._get_args()
    assert "--positions" in args
    assert "1,10,25" in args
    assert "--output" in args
    assert "out.csv" in args

    cmd_rs = ReadStat(value_labels=True, format_catalog="formats.sas7bcat", dictionary="dict.json")
    args = cmd_rs._get_args()
    assert "--value-labels" in args
    assert "--format-catalog" in args
    assert "formats.sas7bcat" in args
    assert "--dictionary" in args
    assert "dict.json" in args

    cmd_ws = WriteStat(dictionary="dict.json", format="sav", lossy=True, output="survey.sav")
    args = cmd_ws._get_args()
    assert "--dictionary" in args
    assert "dict.json" in args
    assert "--format" in args
    assert "sav" in args
    assert "--lossy" in args
    assert "--output" in args
    assert "survey.sav" in args
