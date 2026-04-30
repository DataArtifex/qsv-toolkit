from __future__ import annotations

import builtins
import re
import shutil
import subprocess
from typing import Any


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

    def __init__(self, command: str):
        self.command = command
        self.params: dict[str, Any] = {}

    def _get_args(self) -> list[str]:
        args = []
        for key, value in self.params.items():
            if value is None or value is False:
                continue

            # Special handling for common renaming or specific mappings
            if key == "round_places":
                flag = "--round"
            elif key == "all_":
                flag = "--all"
            elif key == "selection":
                # Positional argument, handled in run()
                continue
            elif key == "input_path":
                # Positional argument, handled in run()
                continue
            else:
                flag = "--" + key.replace("_", "-")

            if value is True:
                args.append(flag)
            elif isinstance(value, list):
                for item in value:
                    args.extend([flag, str(item)])
            else:
                args.extend([flag, str(value)])
        return args

    def run(self, *inputs: str | None) -> str:
        args = self._get_args()
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

    def __init__(
        self,
        list: bool = False,
        envlist: bool = False,
        update: bool = False,
        updatenow: bool = False,
        generate_help_md: bool = False,
        update_mcp_skills: bool = False,
        version: bool = False,
    ):
        super().__init__("")
        self.params = {
            "list": list,
            "envlist": envlist,
            "update": update,
            "updatenow": updatenow,
            "generate-help-md": generate_help_md,
            "update-mcp-skills": update_mcp_skills,
            "version": version,
        }

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

    def __init__(
        self,
        subcommand: str,
        arg: str | None = None,
        column: str | None = None,
        replacement: str | None = None,
        formatstr: str | None = None,
        new_column: str | None = None,
        rename: str | None = None,
        comparand: str | None = None,
        jobs: int | None = None,
        batch: int = 50000,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
    ):
        super().__init__("apply")
        self.subcommand = subcommand
        self.arg = arg
        self.column = column
        self.params = {
            "replacement": replacement,
            "formatstr": formatstr,
            "new_column": new_column,
            "rename": rename,
            "comparand": comparand,
            "jobs": jobs,
            "batch": batch if batch != 50000 else None,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        args = [self.subcommand]
        if self.arg:
            args.append(self.arg)
        if self.column:
            args.append(self.column)
        if input_path:
            args.append(input_path)
        return super().run(*args)


class Behead(QSVCommand):
    """Drop a CSV file's header."""

    def __init__(self, flexible: bool = False, output: str | None = None):
        super().__init__("behead")
        self.params = {"flexible": flexible, "output": output}


class Blake3(QSVCommand):
    """Compute BLAKE3 cryptographic hashes of files."""

    def __init__(self, output: str | None = None, no_headers: bool = False, delimiter: str | None = None):
        super().__init__("blake3")
        self.params = {"output": output, "no_headers": no_headers, "delimiter": delimiter}


class Cat(QSVCommand):
    """Concatenate CSV files by row or by column."""

    def __init__(
        self,
        subcommand: str = "rows",
        pad: bool = False,
        flexible: bool = False,
        group: str = "none",
        group_name: str = "file",
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("cat")
        self.subcommand = subcommand
        self.params = {
            "pad": pad,
            "flexible": flexible,
            "group": group if group != "none" else None,
            "group_name": group_name if group_name != "file" else None,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, *input_paths: str | None) -> str:
        return super().run(self.subcommand, *input_paths)


class Clipboard(QSVCommand):
    """Provide input from clipboard or output to clipboard."""

    def __init__(self, output: bool = False, input: bool = False):
        super().__init__("clipboard")
        self.params = {"output": output, "input": input}


class Color(QSVCommand):
    """Print a pretty, colorized table."""

    def __init__(self, output: str | None = None, no_headers: bool = False, delimiter: str | None = None):
        super().__init__("color")
        self.params = {"output": output, "no_headers": no_headers, "delimiter": delimiter}


class Count(QSVCommand):
    """Returns a count of the number of records in the CSV data."""

    def __init__(
        self,
        human_readable: bool = False,
        width: bool = False,
        width_no_delims: bool = False,
        json: bool = False,
        no_polars: bool = False,
        low_memory: bool = False,
        flexible: bool = False,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("count")
        self.params = {
            "human_readable": human_readable,
            "width": width,
            "width_no_delims": width_no_delims,
            "json": json,
            "no_polars": no_polars,
            "low_memory": low_memory,
            "flexible": flexible,
            "no_headers": no_headers,
            "delimiter": delimiter,
        }


class Datefmt(QSVCommand):
    """Format date/datetime strings."""

    def __init__(
        self,
        column: str,
        formatstr: str | None = None,
        prefer_dmy: bool = False,
        keep_invalid: bool = False,
        new_column: str | None = None,
        rename: str | None = None,
        jobs: int | None = None,
        batch: int = 50000,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
    ):
        super().__init__("datefmt")
        self.column = column
        self.params = {
            "formatstr": formatstr,
            "prefer-dmy": prefer_dmy,
            "keep-invalid": keep_invalid,
            "new-column": new_column,
            "rename": rename,
            "jobs": jobs,
            "batch": batch if batch != 50000 else None,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.column, input_path)


class Dedup(QSVCommand):
    """Remove redundant rows."""

    def __init__(
        self,
        select: str | None = None,
        numeric: bool = False,
        ignore_case: bool = False,
        unique: bool = False,
        dupes_output: str | None = None,
        jobs: int | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        memcheck: bool = False,
    ):
        super().__init__("dedup")
        self.params = {
            "select": select,
            "numeric": numeric,
            "ignore_case": ignore_case,
            "unique": unique,
            "dupes_output": dupes_output,
            "jobs": jobs,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "memcheck": memcheck,
        }


class DescribeGPT(QSVCommand):
    """Inference metadata and provide a summary of the given CSV data using an LLM."""

    def __init__(
        self,
        all_: bool = False,
        description: bool = False,
        dictionary: bool = False,
        tags: bool = False,
        dictionary_output: str | None = None,
        ckan_api: str | None = None,
        ckan_token: str | None = None,
        stats_options: str | None = None,
        num_tags: int = 10,
        tag_vocab: str | None = None,
        cache_dir: str = "~/.qsv-cache",
        enum_threshold: int = 10,
        num_examples: int = 5,
        truncate_str: int = 25,
        addl_cols: bool = False,
        addl_cols_list: str = "sort_order, sortiness, mean, median, mad, stddev, variance, cv",
        prompt: str | None = None,
        sql_results: str | None = None,
        prompt_file: str | None = None,
        sample_size: int = 100,
        fewshot_examples: bool = False,
        session: str | None = None,
        session_len: int = 10,
        base_url: str | None = None,
        model: str | None = None,
        language: str | None = None,
        addl_props: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 10000,
        timeout: int = 300,
        user_agent: str | None = None,
        export_prompt: str | None = None,
        no_cache: bool = False,
        disk_cache_dir: str | None = None,
        redis_cache: bool = False,
        fresh: bool = False,
        forget: bool = False,
        flush_cache: bool = False,
        format: str = "markdown",
        output: str | None = None,
        quiet: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("describegpt")
        self.params = {
            "all_": all_,
            "description": description,
            "dictionary": dictionary,
            "tags": tags,
            "dictionary_output": dictionary_output,
            "ckan_api": ckan_api,
            "ckan_token": ckan_token,
            "stats_options": stats_options,
            "num_tags": num_tags if num_tags != 10 else None,
            "tag_vocab": tag_vocab,
            "cache_dir": cache_dir if cache_dir != "~/.qsv-cache" else None,
            "enum_threshold": enum_threshold if enum_threshold != 10 else None,
            "num_examples": num_examples if num_examples != 5 else None,
            "truncate_str": truncate_str if truncate_str != 25 else None,
            "addl_cols": addl_cols,
            "addl_cols_list": (
                addl_cols_list
                if addl_cols_list != "sort_order, sortiness, mean, median, mad, stddev, variance, cv"
                else None
            ),
            "prompt": prompt,
            "sql_results": sql_results,
            "prompt_file": prompt_file,
            "sample_size": sample_size if sample_size != 100 else None,
            "fewshot_examples": fewshot_examples,
            "session": session,
            "session_len": session_len if session_len != 10 else None,
            "base_url": base_url,
            "model": model,
            "language": language,
            "addl_props": addl_props,
            "api_key": api_key,
            "max_tokens": max_tokens if max_tokens != 10000 else None,
            "timeout": timeout if timeout != 300 else None,
            "user_agent": user_agent,
            "export_prompt": export_prompt,
            "no_cache": no_cache,
            "disk_cache_dir": disk_cache_dir,
            "redis_cache": redis_cache,
            "fresh": fresh,
            "forget": forget,
            "flush_cache": flush_cache,
            "format": format if format != "markdown" else None,
            "output": output,
            "quiet": quiet,
            "delimiter": delimiter,
        }


class Diff(QSVCommand):
    """Find the difference between two CSVs."""

    def __init__(
        self,
        key: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        output: str | None = None,
    ):
        super().__init__("diff")
        self.params = {"key": key, "no-headers": no_headers, "delimiter": delimiter, "output": output}

    def run(self, input1: str | None = None, input2: str | None = None, *_args: str | None) -> str:
        return super().run(input1, input2)


class Edit(QSVCommand):
    """Replace a cell's value specified by row and column."""

    def __init__(
        self,
        row: int,
        column: str,
        value: str,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("edit")
        self.row = row
        self.column = column
        self.value = value
        self.params = {"output": output, "no-headers": no_headers, "delimiter": delimiter}

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(str(self.row), self.column, self.value, input_path)


class Enum(QSVCommand):
    """Add a new column enumerating CSV lines."""

    def __init__(
        self,
        new_column: str = "index",
        start: int = 0,
        uuid: bool = False,
        constant: str | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("enum")
        self.params = {
            "new_column": new_column if new_column != "index" else None,
            "start": start if start != 0 else None,
            "uuid": uuid,
            "constant": constant,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
        }


class Excel(QSVCommand):
    """Exports an Excel sheet to a CSV."""

    def __init__(
        self,
        sheet: str | None = None,
        list_sheets: bool = False,
        output: str | None = None,
        delimiter: str | None = None,
    ):
        super().__init__("excel")
        self.params = {"sheet": sheet, "list-sheets": list_sheets, "output": output, "delimiter": delimiter}


class Exclude(QSVCommand):
    """Excludes the records in one CSV from another."""

    def __init__(
        self,
        columns1: str,
        columns2: str,
        ignore_case: bool = False,
        invert: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("exclude")
        self.columns1 = columns1
        self.columns2 = columns2
        self.params = {
            "ignore-case": ignore_case,
            "invert": invert,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, input1: str | None = None, input2: str | None = None, *_args: str | None) -> str:
        return super().run(self.columns1, input1, self.columns2, input2)


class Explode(QSVCommand):
    """Explode rows based on some column separator."""

    def __init__(
        self,
        column: str,
        separator: str = ",",
        rename: str | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("explode")
        self.column = column
        self.params = {
            "separator": separator if separator != "," else None,
            "rename": rename,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.column, input_path)


class ExtDedup(QSVCommand):
    """Remove duplicate rows from an arbitrarily large CSV/text file."""

    def __init__(
        self,
        select: str | None = None,
        no_output: bool = False,
        dupes_output: str | None = None,
        human_readable: bool = False,
        memory_limit: int = 10,
        temp_dir: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        quiet: bool = False,
    ):
        super().__init__("extdedup")
        self.params = {
            "select": select,
            "no-output": no_output,
            "dupes-output": dupes_output,
            "human-readable": human_readable,
            "memory-limit": memory_limit if memory_limit != 10 else None,
            "temp-dir": temp_dir,
            "no-headers": no_headers,
            "delimiter": delimiter,
            "quiet": quiet,
        }


class ExtSort(QSVCommand):
    """Sort an arbitrarily large CSV/text file."""

    def __init__(
        self,
        select: str | None = None,
        reverse: bool = False,
        memory_limit: int = 20,
        tmp_dir: str = "./",
        jobs: int | None = None,
        delimiter: str | None = None,
        no_headers: bool = False,
    ):
        super().__init__("extsort")
        self.params = {
            "select": select,
            "reverse": reverse,
            "memory-limit": memory_limit if memory_limit != 20 else None,
            "tmp-dir": tmp_dir if tmp_dir != "./" else None,
            "jobs": jobs,
            "delimiter": delimiter,
            "no-headers": no_headers,
        }


class Fetch(QSVCommand):
    """Fetches data from web services for every row using HTTP Get."""

    def __init__(
        self,
        url_template: str,
        column: str | None = None,
        new_column: str | None = None,
        header: list[str] | None = None,
        user_agent: str | None = None,
        timeout: int = 30,
        max_retries: int = 5,
        jql: str | None = None,
        http_filter: str | None = None,
        dry_run: bool = False,
        jobs: int | None = None,
        batch: int = 1000,
        rate_limit: int = 0,
        cache_dir: str | None = None,
        flush_cache: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
    ):
        super().__init__("fetch")
        self.url_template = url_template
        self.params = {
            "column": column,
            "new-column": new_column,
            "header": header,
            "user-agent": user_agent,
            "timeout": timeout if timeout != 30 else None,
            "max-retries": max_retries if max_retries != 5 else None,
            "jql": jql,
            "http-filter": http_filter,
            "dry-run": dry_run,
            "jobs": jobs,
            "batch": batch if batch != 1000 else None,
            "rate-limit": rate_limit if rate_limit != 0 else None,
            "cache-dir": cache_dir,
            "flush-cache": flush_cache,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.url_template, input_path)


class FetchPost(QSVCommand):
    """Fetches data from web services for every row using HTTP Post."""

    def __init__(
        self,
        url_template: str,
        body_template: str,
        column: str | None = None,
        new_column: str | None = None,
        header: list[str] | None = None,
        user_agent: str | None = None,
        timeout: int = 30,
        max_retries: int = 5,
        jql: str | None = None,
        http_filter: str | None = None,
        dry_run: bool = False,
        jobs: int | None = None,
        batch: int = 1000,
        rate_limit: int = 0,
        cache_dir: str | None = None,
        flush_cache: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
    ):
        super().__init__("fetchpost")
        self.url_template = url_template
        self.body_template = body_template
        self.params = {
            "column": column,
            "new-column": new_column,
            "header": header,
            "user-agent": user_agent,
            "timeout": timeout if timeout != 30 else None,
            "max-retries": max_retries if max_retries != 5 else None,
            "jql": jql,
            "http-filter": http_filter,
            "dry-run": dry_run,
            "jobs": jobs,
            "batch": batch if batch != 1000 else None,
            "rate-limit": rate_limit if rate_limit != 0 else None,
            "cache-dir": cache_dir,
            "flush-cache": flush_cache,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.url_template, self.body_template, input_path)


class Fill(QSVCommand):
    """Fill empty values."""

    def __init__(
        self,
        value: str | None = None,
        backfill: bool = False,
        groupby: str | None = None,
        select: str | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("fill")
        self.params = {
            "value": value,
            "backfill": backfill,
            "groupby": groupby,
            "select": select,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
        }


class FixLengths(QSVCommand):
    """Makes all records have same length."""

    def __init__(self, length: int | None = None, output: str | None = None, delimiter: str | None = None):
        super().__init__("fixlengths")
        self.params = {"length": length, "output": output, "delimiter": delimiter}


class Flatten(QSVCommand):
    """Prints flattened records such that fields are labeled separated by a new line."""

    def __init__(
        self,
        condense: int | None = None,
        field_separator: str | None = None,
        separator: str = "#",
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("flatten")
        self.params = {
            "condense": condense,
            "field-separator": field_separator,
            "separator": separator if separator != "#" else None,
            "no-headers": no_headers,
            "delimiter": delimiter,
        }


class Fmt(QSVCommand):
    """Formats CSV data with a custom delimiter or CRLF line endings."""

    def __init__(
        self,
        out_delimiter: str = ",",
        crlf: bool = False,
        ascii: bool = False,
        quote: str = '"',
        quote_always: bool = False,
        quote_never: bool = False,
        escape: str | None = None,
        no_final_newline: bool = False,
        output: str | None = None,
        delimiter: str | None = None,
    ):
        super().__init__("fmt")
        self.params = {
            "out-delimiter": out_delimiter if out_delimiter != "," else None,
            "crlf": crlf,
            "ascii": ascii,
            "quote": quote if quote != '"' else None,
            "quote-always": quote_always,
            "quote-never": quote_never,
            "escape": escape,
            "no-final-newline": no_final_newline,
            "output": output,
            "delimiter": delimiter,
        }


class Foreach(QSVCommand):
    """Loop over a CSV file to execute bash commands."""

    def __init__(
        self,
        column: str,
        command_template: str,
        new_column: str | None = None,
        unquoted: bool = False,
        jobs: int | None = None,
        batch: int = 1,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
    ):
        super().__init__("foreach")
        self.column = column
        self.command_template = command_template
        self.params = {
            "new-column": new_column,
            "unquoted": unquoted,
            "jobs": jobs,
            "batch": batch if batch != 1 else None,
            "no-headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.column, self.command_template, input_path)


class Frequency(QSVCommand):
    """Compute a frequency table of the given CSV data."""

    def __init__(
        self,
        select: str | None = None,
        limit: int = 10,
        unq_limit: int = 10,
        lmt_threshold: int = 0,
        rank_strategy: str = "dense",
        pct_dec_places: int = -5,
        other_sorted: bool = False,
        other_text: str = "Other",
        asc: bool = False,
        no_trim: bool = False,
        null_text: str = "(NULL)",
        no_nulls: bool = False,
        ignore_case: bool = False,
        all_unique_text: str = "<ALL_UNIQUE>",
        vis_whitespace: bool = False,
        jobs: int | None = None,
        json: bool = False,
        pretty_json: bool = False,
        no_stats: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        memcheck: bool = False,
        toon: bool = False,
        weight: str | None = None,
    ):
        super().__init__("frequency")
        self.params = {
            "select": select,
            "limit": limit if limit != 10 else None,
            "unq-limit": unq_limit if unq_limit != 10 else None,
            "lmt-threshold": lmt_threshold if lmt_threshold != 0 else None,
            "rank-strategy": rank_strategy if rank_strategy != "dense" else None,
            "pct-dec-places": pct_dec_places if pct_dec_places != -5 else None,
            "other-sorted": other_sorted,
            "other-text": other_text if other_text != "Other" else None,
            "asc": asc,
            "no-trim": no_trim,
            "null-text": null_text if null_text != "(NULL)" else None,
            "no-nulls": no_nulls,
            "ignore-case": ignore_case,
            "all-unique-text": all_unique_text if all_unique_text != "<ALL_UNIQUE>" else None,
            "vis-whitespace": vis_whitespace,
            "jobs": jobs,
            "json": json,
            "pretty-json": pretty_json,
            "no-stats": no_stats,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
            "memcheck": memcheck,
            "toon": toon,
            "weight": weight,
        }


class Geocode(QSVCommand):
    """Geocodes a location against the Geonames cities database."""

    def __init__(
        self,
        column: str,
        new_column: str | None = None,
        country: str | None = None,
        language: str | None = None,
        min_score: int = 50,
        admin1: bool = False,
        admin2: bool = False,
        timezone: bool = False,
        population: bool = False,
        jobs: int | None = None,
        batch: int = 1000,
        cache_dir: str | None = None,
        flush_cache: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
    ):
        super().__init__("geocode")
        self.column = column
        self.params = {
            "new-column": new_column,
            "country": country,
            "language": language,
            "min-score": min_score if min_score != 50 else None,
            "admin1": admin1,
            "admin2": admin2,
            "timezone": timezone,
            "population": population,
            "jobs": jobs,
            "batch": batch if batch != 1000 else None,
            "cache-dir": cache_dir,
            "flush-cache": flush_cache,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.column, input_path)


class GeoConvert(QSVCommand):
    """Convert between spatial formats & CSV."""

    def __init__(
        self,
        column: str,
        format: str = "geojson",
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("geoconvert")
        self.column = column
        self.params = {
            "format": format if format != "geojson" else None,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.column, input_path)


class Headers(QSVCommand):
    """Show header names."""

    def __init__(self, justify: str | None = None, delimiter: str | None = None, no_headers: bool = False):
        super().__init__("headers")
        self.params = {"justify": justify, "delimiter": delimiter, "no_headers": no_headers}


class Help(QSVCommand):
    """Show usage message."""

    def __init__(self, command: str | None = None):
        super().__init__("help")
        self.command_arg = command

    def run(self, *_args: str | None) -> str:
        if self.command_arg:
            return super().run(self.command_arg)
        return super().run()


class Implode(QSVCommand):
    """Implode rows by grouping on key(s) and joining a value column."""

    def __init__(
        self,
        column: str,
        separator: str = ",",
        rename: str | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("implode")
        self.column = column
        self.params = {
            "separator": separator if separator != "," else None,
            "rename": rename,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.column, input_path)


class Index(QSVCommand):
    """Creates an index of the given CSV data."""

    def __init__(self, output: str | None = None):
        super().__init__("index")
        self.params = {"output": output}


class Input(QSVCommand):
    """Read CSVs w/ special quoting, skipping, trimming & transcoding rules."""

    def __init__(
        self,
        quote: str = '"',
        escape: str | None = None,
        no_quoting: bool = False,
        skip_lines: int = 0,
        trim_headers: bool = False,
        trim_fields: bool = False,
        comment: str | None = None,
        encoding: str = "utf-8",
        output: str | None = None,
        delimiter: str | None = None,
    ):
        super().__init__("input")
        self.params = {
            "quote": quote if quote != '"' else None,
            "escape": escape,
            "no-quoting": no_quoting,
            "skip-lines": skip_lines if skip_lines != 0 else None,
            "trim-headers": trim_headers,
            "trim-fields": trim_fields,
            "comment": comment,
            "encoding": encoding if encoding != "utf-8" else None,
            "output": output,
            "delimiter": delimiter,
        }


class Join(QSVCommand):
    """Joins two sets of CSV data on the specified columns."""

    def __init__(
        self,
        columns1: str,
        columns2: str,
        left: bool = False,
        left_anti: bool = False,
        left_semi: bool = False,
        right: bool = False,
        right_anti: bool = False,
        right_semi: bool = False,
        full: bool = False,
        cross: bool = False,
        nulls: bool = False,
        keys_output: str | None = None,
        ignore_case: bool = False,
        ignore_leading_zeros: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("join")
        self.columns1 = columns1
        self.columns2 = columns2
        self.params = {
            "left": left,
            "left-anti": left_anti,
            "left-semi": left_semi,
            "right": right,
            "right-anti": right_anti,
            "right-semi": right_semi,
            "full": full,
            "cross": cross,
            "nulls": nulls,
            "keys-output": keys_output,
            "ignore-case": ignore_case,
            "ignore-leading-zeros": ignore_leading_zeros,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, input1: str | None = None, input2: str | None = None, *_args: str | None) -> str:
        return super().run(self.columns1, input1, self.columns2, input2)


class Joinp(QSVCommand):
    """Join CSV files using the Pola.rs engine."""

    def __init__(
        self,
        columns1: str,
        columns2: str,
        left: bool = False,
        left_anti: bool = False,
        left_semi: bool = False,
        right: bool = False,
        right_anti: bool = False,
        right_semi: bool = False,
        full: bool = False,
        cross: bool = False,
        nulls: bool = False,
        ignore_case: bool = False,
        ignore_leading_zeros: bool = False,
        output: str | None = None,
        delimiter: str | None = None,
        quiet: bool = False,
    ):
        super().__init__("joinp")
        self.columns1 = columns1
        self.columns2 = columns2
        self.params = {
            "left": left,
            "left-anti": left_anti,
            "left-semi": left_semi,
            "right": right,
            "right-anti": right_anti,
            "right-semi": right_semi,
            "full": full,
            "cross": cross,
            "nulls": nulls,
            "ignore-case": ignore_case,
            "ignore-leading-zeros": ignore_leading_zeros,
            "output": output,
            "delimiter": delimiter,
            "quiet": quiet,
        }

    def run(self, input1: str | None = None, input2: str | None = None, *_args: str | None) -> str:
        return super().run(self.columns1, input1, self.columns2, input2)


class Json(QSVCommand):
    """Convert JSON to CSV."""

    def __init__(self, jaq: str | None = None, select: str | None = None, output: str | None = None):
        super().__init__("json")
        self.params = {"jaq": jaq, "select": select, "output": output}


class Jsonl(QSVCommand):
    """Convert newline-delimited JSON (JSONL/NDJSON) to CSV."""

    def __init__(
        self,
        ignore_errors: bool = False,
        jobs: int | None = None,
        batch: int = 50000,
        output: str | None = None,
        delimiter: str | None = None,
    ):
        super().__init__("jsonl")
        self.params = {
            "ignore-errors": ignore_errors,
            "jobs": jobs,
            "batch": batch if batch != 50000 else None,
            "output": output,
            "delimiter": delimiter,
        }


class Lens(QSVCommand):
    """View a CSV file interactively."""

    def __init__(self, delimiter: str | None = None):
        super().__init__("lens")
        self.params = {"delimiter": delimiter}


class Log(QSVCommand):
    """Log MCP tool invocations to qsvmcp.log."""

    def __init__(self, msg: str):
        super().__init__("log")
        self.msg = msg

    def run(self, *_args: str | None) -> str:
        return super().run(self.msg)


class Luau(QSVCommand):
    """Execute Luau script on CSV data."""

    def __init__(
        self,
        script: str,
        new_column: str | None = None,
        max_errors: int = 100,
        no_globals: bool = False,
        remap: bool = False,
        jobs: int | None = None,
        batch: int = 50000,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
    ):
        super().__init__("luau")
        self.script = script
        self.params = {
            "new-column": new_column,
            "max-errors": max_errors if max_errors != 100 else None,
            "no-globals": no_globals,
            "remap": remap,
            "jobs": jobs,
            "batch": batch if batch != 50000 else None,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.script, input_path)


class MoarStats(QSVCommand):
    """Computes additional statistics and outlier metadata for CSV data."""

    def __init__(
        self,
        stats_options: str = "--infer-dates --infer-boolean --mad --quartiles --percentiles --force --stats-jsonl",
        round_places: int = 4,
        use_percentiles: bool = False,
        pct_thresholds: str = "5,95",
        advanced: bool = False,
        output: str | None = None,
    ):
        super().__init__("moarstats")
        self.params = {
            "stats_options": (
                stats_options
                if stats_options
                != "--infer-dates --infer-boolean --mad --quartiles --percentiles --force --stats-jsonl"
                else None
            ),
            "round_places": round_places,
            "use_percentiles": use_percentiles,
            "pct_thresholds": pct_thresholds if pct_thresholds != "5,95" else None,
            "advanced": advanced,
            "output": output,
        }


class Partition(QSVCommand):
    """Partition CSV data based on a column value."""

    def __init__(
        self,
        column: str,
        out_dir: str,
        filename_template: str = "{}.csv",
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("partition")
        self.column = column
        self.out_dir = out_dir
        self.params = {
            "filename-template": filename_template if filename_template != "{}.csv" else None,
            "no-headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.column, self.out_dir, input_path)


class Pivotp(QSVCommand):
    """Pivots CSV files using the Pola.rs engine."""

    def __init__(
        self,
        index: str,
        on: str,
        values: str,
        aggregate: str = "first",
        output: str | None = None,
        delimiter: str | None = None,
    ):
        super().__init__("pivotp")
        self.index = index
        self.on = on
        self.values = values
        self.params = {
            "aggregate": aggregate if aggregate != "first" else None,
            "output": output,
            "delimiter": delimiter,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.index, self.on, self.values, input_path)


class PragmaStat(QSVCommand):
    """Pragmatic statistical toolkit."""

    def __init__(
        self,
        operation: str,
        column: str | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("pragmastat")
        self.operation = operation
        self.column = column
        self.params = {"output": output, "no-headers": no_headers, "delimiter": delimiter}

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        args = [self.operation]
        if self.column:
            args.append(self.column)
        if input_path:
            args.append(input_path)
        return super().run(*args)


class Pro(QSVCommand):
    """Interact with the qsv pro API."""

    def __init__(self, subcommand: str, args: list[str] | None = None):
        super().__init__("pro")
        self.subcommand = subcommand
        self.args = args or []

    def run(self, *_args: str | None) -> str:
        return super().run(self.subcommand, *self.args)


class Prompt(QSVCommand):
    """Open a file dialog to pick a file."""

    def __init__(
        self,
        filter: str | None = None,
        msg: str | None = None,
        dir: str | None = None,
        save: bool = False,
        fd_output: bool = False,
        output: str | None = None,
        quiet: bool = False,
    ):
        super().__init__("prompt")
        self.params = {
            "filter": filter,
            "msg": msg,
            "dir": dir,
            "save": save,
            "fd-output": fd_output,
            "output": output,
            "quiet": quiet,
        }


class Pseudo(QSVCommand):
    """Pseudonymise the values of a column."""

    def __init__(
        self,
        column: str,
        start: int = 0,
        increment: int = 1,
        formatstr: str = "{}",
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("pseudo")
        self.column = column
        self.params = {
            "start": start if start != 0 else None,
            "increment": increment if increment != 1 else None,
            "formatstr": formatstr if formatstr != "{}" else None,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.column, input_path)


class Py(QSVCommand):
    """Evaluate a Python expression on CSV data."""

    def __init__(
        self,
        script: str,
        new_column: str | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("py")
        self.script = script
        self.params = {"new_column": new_column, "output": output, "no_headers": no_headers, "delimiter": delimiter}

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.script, input_path)


class Rename(QSVCommand):
    """Rename the columns of CSV data efficiently."""

    def __init__(self, names: str, output: str | None = None, no_headers: bool = False, delimiter: str | None = None):
        super().__init__("rename")
        self.names = names
        self.params = {"output": output, "no_headers": no_headers, "delimiter": delimiter}

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.names, input_path)


class Replace(QSVCommand):
    """Replace patterns in CSV data."""

    def __init__(
        self,
        pattern: str,
        replacement: str,
        ignore_case: bool = False,
        literal: bool = False,
        exact: bool = False,
        select: str | None = None,
        unicode: bool = False,
        size_limit: int = 50,
        dfa_size_limit: int = 10,
        not_one: bool = False,
        jobs: int | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
        quiet: bool = False,
    ):
        super().__init__("replace")
        self.pattern = pattern
        self.replacement = replacement
        self.params = {
            "ignore_case": ignore_case,
            "literal": literal,
            "exact": exact,
            "select": select,
            "unicode": unicode,
            "size_limit": size_limit if size_limit != 50 else None,
            "dfa_size_limit": dfa_size_limit if dfa_size_limit != 10 else None,
            "not_one": not_one,
            "jobs": jobs,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
            "quiet": quiet,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.pattern, self.replacement, input_path)


class Reverse(QSVCommand):
    """Reverse rows of CSV data."""

    def __init__(
        self, output: str | None = None, no_headers: bool = False, delimiter: str | None = None, memcheck: bool = False
    ):
        super().__init__("reverse")
        self.params = {"output": output, "no_headers": no_headers, "delimiter": delimiter, "memcheck": memcheck}


class SafeNames(QSVCommand):
    """Modify a CSV's header names to db-safe names."""

    def __init__(
        self,
        mode: str = "Always",
        reserved: str = "_id",
        prefix: str = "unsafe_",
        output: str | None = None,
        delimiter: str | None = None,
    ):
        super().__init__("safenames")
        self.params = {
            "mode": mode if mode != "Always" else None,
            "reserved": reserved if reserved != "_id" else None,
            "prefix": prefix if prefix != "unsafe_" else None,
            "output": output,
            "delimiter": delimiter,
        }


class Sample(QSVCommand):
    """Randomly sample CSV data."""

    def __init__(
        self,
        size: int = 100,
        seed: int | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("sample")
        self.size_arg = size
        self.params = {"seed": seed, "output": output, "no_headers": no_headers, "delimiter": delimiter}

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(str(self.size_arg), input_path)


class Schema(QSVCommand):
    """Generate JSON Schema or Polars Schema from CSV data."""

    def __init__(
        self,
        enum_threshold: int = 50,
        ignore_case: bool = False,
        strict_dates: bool = False,
        strict_formats: bool = False,
        pattern_columns: str | None = None,
        dates_whitelist: str = "date,time,due,open,close,created",
        prefer_dmy: bool = False,
        force: bool = False,
        stdout: bool = False,
        jobs: int | None = None,
        output: str | None = None,
        polars: bool = False,
        no_headers: bool = False,
        delimiter: str | None = None,
        memcheck: bool = False,
    ):
        super().__init__("schema")
        self.params = {
            "enum_threshold": enum_threshold if enum_threshold != 50 else None,
            "ignore_case": ignore_case,
            "strict_dates": strict_dates,
            "strict_formats": strict_formats,
            "pattern_columns": pattern_columns,
            "dates_whitelist": dates_whitelist if dates_whitelist != "date,time,due,open,close,created" else None,
            "prefer_dmy": prefer_dmy,
            "force": force,
            "stdout": stdout,
            "jobs": jobs,
            "output": output,
            "polars": polars,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "memcheck": memcheck,
        }


class ScoreSql(QSVCommand):
    """Score a SQL query against CSV caches for performance analysis."""

    def __init__(self, query: str, delimiter: str | None = None):
        super().__init__("scoresql")
        self.query = query
        self.params = {"delimiter": delimiter}

    def run(self, *_args: str | None) -> str:
        return super().run(self.query)


class Search(QSVCommand):
    """Search CSV data with a regex."""

    def __init__(
        self,
        pattern: str,
        ignore_case: bool = False,
        select: str | None = None,
        invert_match: bool = False,
        unicode: bool = False,
        flag: str | None = None,
        preview: int = 0,
        count: bool = False,
        size_limit: int = 50,
        dfa_size_limit: int = 10,
        json: bool = False,
        not_one: bool = False,
        jobs: int | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
        quiet: bool = False,
    ):
        super().__init__("search")
        self.pattern = pattern
        self.params = {
            "ignore_case": ignore_case,
            "select": select,
            "invert_match": invert_match,
            "unicode": unicode,
            "flag": flag,
            "preview": preview if preview != 0 else None,
            "count": count,
            "size_limit": size_limit if size_limit != 50 else None,
            "dfa_size_limit": dfa_size_limit if dfa_size_limit != 10 else None,
            "json": json,
            "not_one": not_one,
            "jobs": jobs,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
            "quiet": quiet,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.pattern, input_path)


class SearchSet(QSVCommand):
    """Search CSV data with a regex set."""

    def __init__(
        self,
        regexset_file: str,
        ignore_case: bool = False,
        literal: bool = False,
        exact: bool = False,
        select: str | None = None,
        invert_match: bool = False,
        unicode: bool = False,
        flag: str | None = None,
        flag_matches_only: bool = False,
        unmatched_output: str | None = None,
        quick: bool = False,
        count: bool = False,
        json: bool = False,
        size_limit: int = 50,
        dfa_size_limit: int = 10,
        not_one: bool = False,
        jobs: int | None = None,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        progressbar: bool = False,
        quiet: bool = False,
    ):
        super().__init__("searchset")
        self.regexset_file = regexset_file
        self.params = {
            "ignore_case": ignore_case,
            "literal": literal,
            "exact": exact,
            "select": select,
            "invert_match": invert_match,
            "unicode": unicode,
            "flag": flag,
            "flag_matches_only": flag_matches_only,
            "unmatched_output": unmatched_output,
            "quick": quick,
            "count": count,
            "json": json,
            "size_limit": size_limit if size_limit != 50 else None,
            "dfa_size_limit": dfa_size_limit if dfa_size_limit != 10 else None,
            "not_one": not_one,
            "jobs": jobs,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "progressbar": progressbar,
            "quiet": quiet,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.regexset_file, input_path)


class Select(QSVCommand):
    """Select, re-order, duplicate or drop columns."""

    def __init__(
        self,
        selection: str,
        random: bool = False,
        seed: int | None = None,
        sort: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("select")
        self.selection = selection
        self.params = {
            "random": random,
            "seed": seed,
            "sort": sort,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.selection, input_path)


class Slice(QSVCommand):
    """Slice records from CSV."""

    def __init__(
        self,
        index: int | None = None,
        len: int | None = None,
        next: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("slice")
        self.params = {
            "index": index,
            "len": len,
            "next": next,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
        }


class Snappy(QSVCommand):
    """Compress/decompress data using the Snappy algorithm."""

    def __init__(self, decompress: bool = False, jobs: int | None = None, output: str | None = None):
        super().__init__("snappy")
        self.params = {"decompress": decompress, "jobs": jobs, "output": output}


class Sniff(QSVCommand):
    """Quickly sniff CSV metadata."""

    def __init__(
        self,
        sample: int = 100,
        prefer_dmy: bool = False,
        delimiter: str | None = None,
        json: bool = False,
        pretty_json: bool = False,
        no_headers: bool = False,
    ):
        super().__init__("sniff")
        self.params = {
            "sample": sample if sample != 100 else None,
            "prefer_dmy": prefer_dmy,
            "delimiter": delimiter,
            "json": json,
            "pretty_json": pretty_json,
            "no_headers": no_headers,
        }


class Sort(QSVCommand):
    """Sort CSV data in alphabetical, numerical, reverse or random order."""

    def __init__(
        self,
        select: str | None = None,
        numeric: bool = False,
        natural: bool = False,
        reverse: bool = False,
        ignore_case: bool = False,
        unique: bool = False,
        random: bool = False,
        seed: int | None = None,
        rng: str = "standard",
        jobs: int | None = None,
        faster: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        memcheck: bool = False,
    ):
        super().__init__("sort")
        self.params = {
            "select": select,
            "numeric": numeric,
            "natural": natural,
            "reverse": reverse,
            "ignore_case": ignore_case,
            "unique": unique,
            "random": random,
            "seed": seed,
            "rng": rng if rng != "standard" else None,
            "jobs": jobs,
            "faster": faster,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "memcheck": memcheck,
        }


class SortCheck(QSVCommand):
    """Check if a CSV is sorted."""

    def __init__(
        self,
        select: str | None = None,
        numeric: bool = False,
        natural: bool = False,
        reverse: bool = False,
        ignore_case: bool = False,
        all_: bool = False,
        json: bool = False,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("sortcheck")
        self.params = {
            "select": select,
            "numeric": numeric,
            "natural": natural,
            "reverse": reverse,
            "ignore-case": ignore_case,
            "all": all_,
            "json": json,
            "no-headers": no_headers,
            "delimiter": delimiter,
        }


class Split(QSVCommand):
    """Split CSV data into many files."""

    def __init__(
        self,
        out_dir: str,
        size: int = 500,
        chunks: int | None = None,
        buf_size: int = 8192,
        filename_template: str = "{}.csv",
        jobs: int | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("split")
        self.out_dir = out_dir
        self.params = {
            "size": size if size != 500 else None,
            "chunks": chunks,
            "buf-size": buf_size if buf_size != 8192 else None,
            "filename-template": filename_template if filename_template != "{}.csv" else None,
            "jobs": jobs,
            "no-headers": no_headers,
            "delimiter": delimiter,
        }

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.out_dir, input_path)


class Sqlp(QSVCommand):
    """Run a SQL query against several CSVs using the Pola.rs engine."""

    def __init__(
        self,
        query: str,
        format: str = "csv",
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        try_parsedates: bool = False,
        low_memory: bool = False,
        no_cache: bool = False,
        ignore_errors: bool = False,
    ):
        super().__init__("sqlp")
        self.query = query
        self.params = {
            "format": format if format != "csv" else None,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "try_parsedates": try_parsedates,
            "low_memory": low_memory,
            "no_cache": no_cache,
            "ignore_errors": ignore_errors,
        }

    def run(self, *input_paths: str | None) -> str:
        return super().run(self.query, *input_paths)


class Stats(QSVCommand):
    """Computes summary statistics for CSV data."""

    def __init__(
        self,
        select: str | None = None,
        everything: bool = False,
        typesonly: bool = False,
        infer_boolean: bool = False,
        boolean_patterns: str = "1:0,t*:f*,y*:n*",
        mode: bool = False,
        cardinality: bool = False,
        median: bool = False,
        mad: bool = False,
        quartiles: bool = False,
        percentiles: bool = False,
        percentile_list: str = "5,10,40,60,90,95",
        round_places: int = 4,
        nulls: bool = False,
        infer_dates: bool = False,
        dates_whitelist: str = "sniff",
        prefer_dmy: bool = False,
        force: bool = False,
        jobs: int | None = None,
        stats_jsonl: bool = False,
        cache_threshold: int = 5000,
        vis_whitespace: bool = False,
        dataset_stats: bool = False,
        output: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
        memcheck: bool = False,
        weight: str | None = None,
    ):
        super().__init__("stats")
        self.params = {
            "select": select,
            "everything": everything,
            "typesonly": typesonly,
            "infer-boolean": infer_boolean,
            "boolean-patterns": boolean_patterns if boolean_patterns != "1:0,t*:f*,y*:n*" else None,
            "mode": mode,
            "cardinality": cardinality,
            "median": median,
            "mad": mad,
            "quartiles": quartiles,
            "percentiles": percentiles,
            "percentile-list": percentile_list if percentile_list != "5,10,40,60,90,95" else None,
            "round_places": round_places,
            "nulls": nulls,
            "infer-dates": infer_dates,
            "dates-whitelist": dates_whitelist if dates_whitelist != "sniff" else None,
            "prefer-dmy": prefer_dmy,
            "force": force,
            "jobs": jobs,
            "stats-jsonl": stats_jsonl,
            "cache-threshold": cache_threshold if cache_threshold != 5000 else None,
            "vis-whitespace": vis_whitespace,
            "dataset-stats": dataset_stats,
            "output": output,
            "no-headers": no_headers,
            "delimiter": delimiter,
            "memcheck": memcheck,
            "weight": weight,
        }


class Table(QSVCommand):
    """Align CSV data into columns."""

    def __init__(
        self,
        width: int = 100,
        pad: int = 2,
        align: str = "left",
        output: str | None = None,
        delimiter: str | None = None,
    ):
        super().__init__("table")
        self.params = {
            "width": width if width != 100 else None,
            "pad": pad if pad != 2 else None,
            "align": align if align != "left" else None,
            "output": output,
            "delimiter": delimiter,
        }


class Template(QSVCommand):
    """Render templates using CSV data."""

    def __init__(
        self,
        template: str,
        out_dir: str | None = None,
        no_headers: bool = False,
        delimiter: str | None = None,
    ):
        super().__init__("template")
        self.template = template
        self.params = {"out-dir": out_dir, "no-headers": no_headers, "delimiter": delimiter}

    def run(self, input_path: str | None = None, *_args: str | None) -> str:
        return super().run(self.template, input_path)


class ToJsonl(QSVCommand):
    """Convert CSV to newline-delimited JSON."""

    def __init__(self, output: str | None = None, no_headers: bool = False, delimiter: str | None = None):
        super().__init__("tojsonl")
        self.params = {"output": output, "no-headers": no_headers, "delimiter": delimiter}


class To(QSVCommand):
    """Convert CSVs to Parquet/PostgreSQL/XLSX/SQLite/Data Package."""

    def __init__(
        self,
        subcommand: str,
        destination: str,
        print_package: bool = False,
        dump: bool = False,
        stats: bool = False,
        stats_csv: str | None = None,
        quiet: bool = False,
        schema: str | None = None,
        infer_len: int | None = None,
        try_parse_dates: bool = False,
        drop: bool = False,
        evolve: bool = False,
        pipe: bool = False,
        table: str | None = None,
        separator: str = " ",
        compression: str = "zstd",
        compress_level: int | None = None,
        all_strings: bool = False,
        jobs: int | None = None,
        delimiter: str | None = None,
    ):
        super().__init__("to")
        self.subcommand = subcommand
        self.destination = destination
        self.params = {
            "print-package": print_package,
            "dump": dump,
            "stats": stats,
            "stats-csv": stats_csv,
            "quiet": quiet,
            "schema": schema,
            "infer-len": infer_len,
            "try-parse-dates": try_parse_dates,
            "drop": drop,
            "evolve": evolve,
            "pipe": pipe,
            "table": table,
            "separator": separator if separator != " " else None,
            "compression": compression if compression != "zstd" else None,
            "compress-level": compress_level,
            "all-strings": all_strings,
            "jobs": jobs,
            "delimiter": delimiter,
        }

    def run(self, *input_paths: str | None) -> str:
        return super().run(self.subcommand, self.destination, *input_paths)


class Transpose(QSVCommand):
    """Transpose rows/columns of CSV data."""

    def __init__(
        self,
        multipass: bool = False,
        select: str | None = None,
        long: str | None = None,
        output: str | None = None,
        delimiter: str | None = None,
        memcheck: bool = False,
    ):
        super().__init__("transpose")
        self.params = {
            "multipass": multipass,
            "select": select,
            "long": long,
            "output": output,
            "delimiter": delimiter,
            "memcheck": memcheck,
        }


class Validate(QSVCommand):
    """Validate CSV data for RFC4180-compliance or with JSON Schema."""

    def __init__(
        self,
        json_schema: str | None = None,
        trim: bool = False,
        no_format_validation: bool = False,
        fail_fast: bool = False,
        valid_suffix: str = "valid",
        invalid_suffix: str = "invalid",
        json: bool = False,
        pretty_json: bool = False,
        valid_output: str | None = None,
        jobs: int | None = None,
        batch: int = 50000,
        delimiter: str | None = None,
        progressbar: bool = False,
        quiet: bool = False,
    ):
        super().__init__("validate")
        self.json_schema = json_schema
        self.params = {
            "trim": trim,
            "no-format-validation": no_format_validation,
            "fail-fast": fail_fast,
            "valid": valid_suffix if valid_suffix != "valid" else None,
            "invalid": invalid_suffix if invalid_suffix != "invalid" else None,
            "json": json,
            "pretty-json": pretty_json,
            "valid-output": valid_output,
            "jobs": jobs,
            "batch": batch if batch != 50000 else None,
            "delimiter": delimiter,
            "progressbar": progressbar,
            "quiet": quiet,
        }

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
