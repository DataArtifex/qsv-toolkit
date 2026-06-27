from __future__ import annotations

import builtins
import re
import shutil
import subprocess


def _run_qsv_command(command: str, args: list[str]) -> str:
    """
    Helper function to run a qsv command.
    Checks that the `qsv` executable is available in the PATH.
    Raises a RuntimeError if not found.
    """
    if shutil.which("qsv") is None:
        raise RuntimeError("The 'qsv' command-line tool is not installed or not found in PATH.")
    cmd = ["qsv"]
    if command:
        cmd.append(command)
    cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


class QSVCommand:
    """Base class for all QSV commands."""

    def __init__(self, command: str, *args, **kwargs):
        self.command = command
        # Store core positional arguments passed at instantiation
        self.init_args = [str(arg) for arg in args if arg is not None]
        # Store keyword arguments (mapped to CLI options/flags)
        self.params = kwargs

    def _get_args(self) -> list[str]:
        args = []
        for key, value in self.params.items():
            if value is None or value is False:
                continue

            # Strip trailing underscore (e.g. all_ -> all, input_ -> input)
            flag_name = key[:-1] if key.endswith("_") else key

            # Special handling for common renaming or specific mappings
            if flag_name == "round_places":
                flag = "--round"
            elif flag_name in ("selection", "input_path"):
                # Positional argument, handled in run()
                continue
            else:
                flag = "--" + flag_name.replace("_", "-")

            if value is True:
                args.append(flag)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    args.extend([flag, str(item)])
            else:
                args.extend([flag, str(value)])
        return args

    def run(self, *inputs: str | None) -> str:
        # Build full CLI arguments: [flags] + [init_args] + [inputs]
        args = self._get_args()
        args.extend(self.init_args)
        args.extend(str(i) for i in inputs if i is not None)
        return _run_qsv_command(self.command, args)

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def help(cls) -> str:
        """Returns the help output for the command."""
        if cls is QSVCommand:
            return "Help not available for base QSVCommand."
        cmd_name = cls.__name__.lower()
        if cmd_name == "qsv":
            cmd_name = ""
        return _run_qsv_command(cmd_name, ["--help"])


class QSV(QSVCommand):
    """The qsv command itself."""

    def __init__(self, **kwargs):
        super().__init__("", **kwargs)

    @staticmethod
    def commands() -> list[type[QSVCommand]]:
        """Returns a list of all available command classes."""
        cmds = [cls for cls in QSVCommand.__subclasses__() if cls is not QSV]
        return sorted(cmds, key=lambda x: x.__name__)

    @staticmethod
    def version() -> str:
        """Returns the full output of `qsv --version`."""
        return _run_qsv_command("", ["--version"])

    @staticmethod
    def version_number() -> str:
        """
        Returns the QSV version number extracted from the `qsv --version` command.
        For example '19.1.0'.
        """
        output = QSV.version()
        match = re.search(r"qsv\s+([\d\.]+)", output)
        if match:
            return match.group(1)
        return "unknown"

    @staticmethod
    def list() -> builtins.list[dict[str, str]]:
        """
        Parses the output of `qsv --list` and returns a list of command name/description objects.
        """
        output = _run_qsv_command("", ["--list"])
        commands = []
        started = False
        for line in output.splitlines():
            if "Installed commands" in line:
                started = True
                continue
            if started and line.startswith("    "):
                stripped = line.strip()
                parts = stripped.split(maxsplit=1)
                if len(parts) == 2:
                    commands.append({"name": parts[0], "description": parts[1]})
            elif started and line.strip() == "":
                if commands:
                    break
        return commands

    @staticmethod
    def envlist() -> builtins.list[dict[str, str]]:
        """
        Parses the output of `qsv --envlist` and returns a list of environment variable objects.
        """
        output = _run_qsv_command("", ["--envlist"])
        env_vars = []
        for line in output.splitlines():
            if ":" in line:
                parts = line.split(":", 1)
                name = parts[0].strip()
                value = parts[1].strip().strip('"')
                env_vars.append({"name": name, "value": value})
        return env_vars


class Apply(QSVCommand):
    """Apply series of transformations to a column."""

    def __init__(self, subcommand: str, arg: str | None = None, column: str | None = None, **kwargs):
        super().__init__("apply", subcommand, arg, column, **kwargs)


class Behead(QSVCommand):
    """Drop a CSV file's header."""

    def __init__(self, **kwargs):
        super().__init__("behead", **kwargs)


class Blake3(QSVCommand):
    """Compute BLAKE3 cryptographic hashes of files."""

    def __init__(self, **kwargs):
        super().__init__("blake3", **kwargs)


class Cat(QSVCommand):
    """Concatenate CSV files by row or by column."""

    def __init__(self, subcommand: str = "rows", **kwargs):
        super().__init__("cat", subcommand, **kwargs)


class Clipboard(QSVCommand):
    """Provide input from clipboard or output to clipboard."""

    def __init__(self, **kwargs):
        super().__init__("clipboard", **kwargs)


class Color(QSVCommand):
    """Print a pretty, colorized table."""

    def __init__(self, **kwargs):
        super().__init__("color", **kwargs)


class Count(QSVCommand):
    """Returns a count of the number of records in the CSV data."""

    def __init__(self, **kwargs):
        super().__init__("count", **kwargs)


class Datefmt(QSVCommand):
    """Format date/datetime strings."""

    def __init__(self, column: str, **kwargs):
        super().__init__("datefmt", column, **kwargs)


class Dedup(QSVCommand):
    """Remove redundant rows."""

    def __init__(self, **kwargs):
        super().__init__("dedup", **kwargs)


class DescribeGPT(QSVCommand):
    """Inference metadata and provide a summary of the given CSV data using an LLM."""

    def __init__(self, **kwargs):
        super().__init__("describegpt", **kwargs)


class Diff(QSVCommand):
    """Find the difference between two CSVs."""

    def __init__(self, **kwargs):
        super().__init__("diff", **kwargs)

    def run(self, *inputs: str | None) -> str:
        input1 = inputs[0] if len(inputs) > 0 else None
        input2 = inputs[1] if len(inputs) > 1 else None
        return super().run(input1, input2)


class Edit(QSVCommand):
    """Replace a cell's value specified by row and column."""

    def __init__(self, row: int, column: str, value: str, **kwargs):
        super().__init__("edit", str(row), column, value, **kwargs)


class Enum(QSVCommand):
    """Add a new column enumerating CSV lines."""

    def __init__(self, **kwargs):
        super().__init__("enum", **kwargs)


class Excel(QSVCommand):
    """Exports an Excel sheet to a CSV."""

    def __init__(self, **kwargs):
        super().__init__("excel", **kwargs)


class Exclude(QSVCommand):
    """Excludes the records in one CSV from another."""

    def __init__(self, columns1: str, columns2: str, **kwargs):
        super().__init__("exclude", **kwargs)
        self.columns1 = columns1
        self.columns2 = columns2

    def run(self, *inputs: str | None) -> str:
        input1 = inputs[0] if len(inputs) > 0 else None
        input2 = inputs[1] if len(inputs) > 1 else None
        return super().run(self.columns1, input1, self.columns2, input2)


class Explode(QSVCommand):
    """Explode rows based on some column separator."""

    def __init__(self, column: str, **kwargs):
        super().__init__("explode", column, **kwargs)


class ExtDedup(QSVCommand):
    """Remove duplicate rows from an arbitrarily large CSV/text file."""

    def __init__(self, **kwargs):
        super().__init__("extdedup", **kwargs)


class ExtSort(QSVCommand):
    """Sort an arbitrarily large CSV/text file."""

    def __init__(self, **kwargs):
        super().__init__("extsort", **kwargs)


class Fetch(QSVCommand):
    """Fetches data from web services for every row using HTTP Get."""

    def __init__(self, url_template: str, **kwargs):
        super().__init__("fetch", url_template, **kwargs)


class FetchPost(QSVCommand):
    """Fetches data from web services for every row using HTTP Post."""

    def __init__(self, url_template: str, body_template: str, **kwargs):
        super().__init__("fetchpost", url_template, body_template, **kwargs)


class Fill(QSVCommand):
    """Fill empty values."""

    def __init__(self, **kwargs):
        super().__init__("fill", **kwargs)


class FixLengths(QSVCommand):
    """Makes all records have same length."""

    def __init__(self, **kwargs):
        super().__init__("lengths", **kwargs)


class Flatten(QSVCommand):
    """Flatten CSV records into a list of key-value pairs."""

    def __init__(self, **kwargs):
        super().__init__("flatten", **kwargs)


class Fmt(QSVCommand):
    """Reformat CSV data with different delimiters, quote styles, etc."""

    def __init__(self, **kwargs):
        super().__init__("fmt", **kwargs)


class Foreach(QSVCommand):
    """Loop over a CSV file to execute bash commands."""

    def __init__(self, column: str, command_template: str, **kwargs):
        super().__init__("foreach", column, command_template, **kwargs)


class Frequency(QSVCommand):
    """Compute a frequency table of the given CSV data."""

    def __init__(self, **kwargs):
        super().__init__("frequency", **kwargs)


class GeoConvert(QSVCommand):
    """Convert between spatial formats & CSV."""

    def __init__(self, column: str, **kwargs):
        super().__init__("geoconvert", column, **kwargs)


class Geocode(QSVCommand):
    """Geocodes a location against the Geonames cities database."""

    def __init__(self, column: str, **kwargs):
        super().__init__("geocode", column, **kwargs)


class Headers(QSVCommand):
    """Show header names."""

    def __init__(self, **kwargs):
        super().__init__("headers", **kwargs)


class Help(QSVCommand):
    """Show usage message."""

    def __init__(self, command: str | None = None):
        super().__init__("help", command)


class Implode(QSVCommand):
    """Implode rows by grouping on key(s) and joining a value column."""

    def __init__(self, column: str, **kwargs):
        super().__init__("implode", column, **kwargs)


class Index(QSVCommand):
    """Creates an index of the given CSV data."""

    def __init__(self, **kwargs):
        super().__init__("index", **kwargs)


class Input(QSVCommand):
    """Read CSV data with special parser options."""

    def __init__(self, **kwargs):
        super().__init__("input", **kwargs)


class Join(QSVCommand):
    """Joins two sets of CSV data on the specified columns."""

    def __init__(self, columns1: str, columns2: str, **kwargs):
        super().__init__("join", **kwargs)
        self.columns1 = columns1
        self.columns2 = columns2

    def run(self, *inputs: str | None) -> str:
        input1 = inputs[0] if len(inputs) > 0 else None
        input2 = inputs[1] if len(inputs) > 1 else None
        return super().run(self.columns1, input1, self.columns2, input2)


class Joinp(QSVCommand):
    """Join CSV files using the Pola.rs engine."""

    def __init__(self, columns1: str, columns2: str, **kwargs):
        super().__init__("joinp", **kwargs)
        self.columns1 = columns1
        self.columns2 = columns2

    def run(self, *inputs: str | None) -> str:
        input1 = inputs[0] if len(inputs) > 0 else None
        input2 = inputs[1] if len(inputs) > 1 else None
        return super().run(self.columns1, input1, self.columns2, input2)


class Json(QSVCommand):
    """Convert JSON to CSV."""

    def __init__(self, **kwargs):
        super().__init__("json", **kwargs)


class Jsonl(QSVCommand):
    """Convert newline-delimited JSON (JSONL/NDJSON) to CSV."""

    def __init__(self, **kwargs):
        super().__init__("jsonl", **kwargs)


class Lens(QSVCommand):
    """View a CSV file interactively."""

    def __init__(self, **kwargs):
        super().__init__("lens", **kwargs)


class Log(QSVCommand):
    """Log MCP tool invocations to qsvmcp.log."""

    def __init__(self, msg: str):
        super().__init__("log", msg)


class Luau(QSVCommand):
    """Execute Luau script on CSV data."""

    def __init__(self, script: str, **kwargs):
        super().__init__("luau", script, **kwargs)


class MoarStats(QSVCommand):
    """Computes additional statistics and outlier metadata for CSV data."""

    def __init__(self, **kwargs):
        super().__init__("moarstats", **kwargs)


class Partition(QSVCommand):
    """Partition CSV data based on a column value."""

    def __init__(self, column: str, out_dir: str, **kwargs):
        super().__init__("partition", column, out_dir, **kwargs)


class Pivotp(QSVCommand):
    """Pivots CSV files using the Pola.rs engine."""

    def __init__(self, index: str, on: str, values: str, **kwargs):
        super().__init__("pivotp", index, on, values, **kwargs)


class PragmaStat(QSVCommand):
    """Pragmatic statistical toolkit."""

    def __init__(self, operation: str, column: str | None = None, **kwargs):
        super().__init__("pragmastat", operation, column, **kwargs)


class Pro(QSVCommand):
    """Interact with the qsv pro API."""

    def __init__(self, subcommand: str, args: list[str] | None = None, **kwargs):
        init_args = [subcommand]
        if args:
            init_args.extend(args)
        super().__init__("pro", *init_args, **kwargs)


class Profile(QSVCommand):
    """Extract and infer DCAT-3 / Croissant metadata from a CSV."""

    def __init__(self, **kwargs):
        super().__init__("profile", **kwargs)


class Prompt(QSVCommand):
    """Open a file dialog to pick a file."""

    def __init__(self, **kwargs):
        super().__init__("prompt", **kwargs)


class Pseudo(QSVCommand):
    """Pseudonymise the values of a column."""

    def __init__(self, column: str, **kwargs):
        super().__init__("pseudo", column, **kwargs)


class Py(QSVCommand):
    """Evaluate a Python expression on CSV data."""

    def __init__(self, script: str, **kwargs):
        super().__init__("py", script, **kwargs)


class Rename(QSVCommand):
    """Rename the columns of CSV data efficiently."""

    def __init__(self, names: str, **kwargs):
        super().__init__("rename", names, **kwargs)


class Replace(QSVCommand):
    """Replace patterns in CSV data."""

    def __init__(self, pattern: str, replacement: str, **kwargs):
        super().__init__("replace", pattern, replacement, **kwargs)


class Reverse(QSVCommand):
    """Reverse rows of CSV data."""

    def __init__(self, **kwargs):
        super().__init__("reverse", **kwargs)


class SafeNames(QSVCommand):
    """Modify a CSV's header names to db-safe names."""

    def __init__(self, **kwargs):
        super().__init__("safenames", **kwargs)


class Sample(QSVCommand):
    """Randomly sample CSV data."""

    def __init__(self, size: int = 100, **kwargs):
        super().__init__("sample", str(size), **kwargs)


class Schema(QSVCommand):
    """Generate JSON Schema or Polars Schema from CSV data."""

    def __init__(self, **kwargs):
        super().__init__("schema", **kwargs)


class ScoreSql(QSVCommand):
    """Score a SQL query against CSV caches for performance analysis."""

    def __init__(self, query: str, **kwargs):
        super().__init__("scoresql", query, **kwargs)


class Search(QSVCommand):
    """Search CSV data with a regex."""

    def __init__(self, pattern: str, **kwargs):
        super().__init__("search", pattern, **kwargs)


class SearchSet(QSVCommand):
    """Search CSV data with a regex set."""

    def __init__(self, regexset_file: str, **kwargs):
        super().__init__("searchset", regexset_file, **kwargs)


class Select(QSVCommand):
    """Select, re-order, duplicate or drop columns."""

    def __init__(self, selection: str, **kwargs):
        super().__init__("select", selection, **kwargs)


class Slice(QSVCommand):
    """Slice records from CSV."""

    def __init__(self, **kwargs):
        super().__init__("slice", **kwargs)


class Snappy(QSVCommand):
    """Compress/decompress data using the Snappy algorithm."""

    def __init__(self, **kwargs):
        super().__init__("snappy", **kwargs)


class Sniff(QSVCommand):
    """Quickly sniff CSV metadata."""

    def __init__(self, **kwargs):
        super().__init__("sniff", **kwargs)


class Sort(QSVCommand):
    """Sort CSV data in alphabetical, numerical, reverse or random order."""

    def __init__(self, **kwargs):
        super().__init__("sort", **kwargs)


class SortCheck(QSVCommand):
    """Check if a CSV is sorted."""

    def __init__(self, **kwargs):
        super().__init__("sortcheck", **kwargs)


class Split(QSVCommand):
    """Split CSV data into many files."""

    def __init__(self, out_dir: str, **kwargs):
        super().__init__("split", out_dir, **kwargs)


class Sqlp(QSVCommand):
    """Run a SQL query against several CSVs using the Pola.rs engine."""

    def __init__(self, query: str, **kwargs):
        super().__init__("sqlp", query, **kwargs)


class Stats(QSVCommand):
    """Computes summary statistics for CSV data."""

    def __init__(self, **kwargs):
        super().__init__("stats", **kwargs)


class Synthesize(QSVCommand):
    """Generate a statistically-faithful synthetic CSV from a source CSV."""

    def __init__(self, **kwargs):
        super().__init__("synthesize", **kwargs)


class Table(QSVCommand):
    """Align CSV data into columns."""

    def __init__(self, **kwargs):
        super().__init__("table", **kwargs)


class Template(QSVCommand):
    """Render templates using CSV data."""

    def __init__(self, template: str, **kwargs):
        super().__init__("template", template, **kwargs)


class To(QSVCommand):
    """Convert CSV data to other formats (sqlite, postgres, parquet, xlsx, etc.)."""

    def __init__(self, subcommand: str, destination: str, **kwargs):
        super().__init__("to", subcommand, destination, **kwargs)


class ToJsonl(QSVCommand):
    """Convert CSV to newline-delimited JSON."""

    def __init__(self, **kwargs):
        super().__init__("tojsonl", **kwargs)


class Transpose(QSVCommand):
    """Transpose rows/columns of CSV data."""

    def __init__(self, **kwargs):
        super().__init__("transpose", **kwargs)


class Validate(QSVCommand):
    """Validate CSV data for RFC4180-compliance or with JSON Schema."""

    def __init__(self, json_schema: str | None = None, **kwargs):
        super().__init__("validate", **kwargs)
        self.json_schema = json_schema

    def run(self, *input_paths: str | None) -> str:
        args = [p for p in input_paths if p is not None]
        if self.json_schema:
            args.append(self.json_schema)
        return super().run(*args)


# --- Function Wrappers for Backward Compatibility ---


def index(input_path: str, output: str | None = None) -> str:
    """Creates an index of the given CSV data."""
    return Index(output=output).run(input_path)


def frequency(input_path: str, **kwargs) -> str:
    """Compute a frequency table of the given CSV data."""
    return Frequency(**kwargs).run(input_path)


def stats(input_path: str, **kwargs) -> str:
    """Computes summary statistics for CSV data."""
    return Stats(**kwargs).run(input_path)


def schema(input_path: str, **kwargs) -> str:
    """Generate JSON Schema or Polars Schema from CSV data."""
    return Schema(**kwargs).run(input_path)


def describegpt(input_path: str, **kwargs) -> str:
    """Inference metadata and provide a summary of the given CSV data using an LLM."""
    return DescribeGPT(**kwargs).run(input_path)


def select(input_path: str, selection: str, **kwargs) -> str:
    """Select columns from CSV data efficiently."""
    return Select(selection=selection, **kwargs).run(input_path)


def moarstats(input_path: str, **kwargs) -> str:
    """Computes additional statistics and outlier metadata for CSV data."""
    return MoarStats(**kwargs).run(input_path)


def profile(input_path: str, **kwargs) -> str:
    """Extract and infer DCAT-3 / Croissant metadata from a CSV."""
    return Profile(**kwargs).run(input_path)


def synthesize(input_path: str, **kwargs) -> str:
    """Generate a statistically-faithful synthetic CSV from a source CSV."""
    return Synthesize(**kwargs).run(input_path)
