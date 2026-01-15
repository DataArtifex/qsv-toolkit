import subprocess
from typing import Optional, List, Union

def _run_qsv_command(command: str, args: List[str]) -> str:
    """
    Helper function to run a qsv command.
    Checks that the `qsv` executable is available in the PATH.
    Raises a RuntimeError if not found.
    """
    import shutil
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
        self.params = {}

    def _get_args(self) -> List[str]:
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

    def run(self, *inputs: str) -> str:
        args = self._get_args()
        args.extend(inputs)
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
        update_mcp_skills: bool = False,
        version: bool = False
    ):
        super().__init__("")
        self.params = {
            "list": list,
            "envlist": envlist,
            "update": update,
            "updatenow": updatenow,
            "update-mcp-skills": update_mcp_skills,
            "version": version
        }

    @staticmethod
    def commands() -> List[type]:
        """Returns a list of all available command classes."""
        cmds = [cls for cls in QSVCommand.__subclasses__() if cls is not QSV]
        return sorted(cmds, key=lambda x: x.__name__)

class Apply(QSVCommand):
    """Apply series of transformations to a column."""

    def __init__(
        self,
        column: str,
        operation: Optional[str] = None,
        replacement: Optional[str] = None,
        formatstr: Optional[str] = None,
        new_column: Optional[str] = None,
        rename: Optional[str] = None,
        comparand: Optional[str] = None,
        jobs: Optional[int] = None,
        batch: int = 50000,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        progressbar: bool = False
    ):
        super().__init__("apply")
        self.column = column
        self.operation = operation
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
            "progressbar": progressbar
        }
    
    def run(self, input_path: Optional[str] = None) -> str:
        args = []
        if self.operation:
            args.append(self.operation)
        args.append(self.column)
        if input_path:
            args.append(input_path)
        return super().run(*args)

class Behead(QSVCommand):
    """Drop a CSV file's header."""

    def __init__(
        self,
        flexible: bool = False,
        output: Optional[str] = None
    ):
        super().__init__("behead")
        self.params = {
            "flexible": flexible,
            "output": output
        }

class Cat(QSVCommand):
    """Concatenate CSV files by row or by column."""

    def __init__(
        self,
        subcommand: str = "rows",
        pad: bool = False,
        flexible: bool = False,
        group: str = "none",
        group_name: str = "file",
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
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
            "delimiter": delimiter
        }
    
    def run(self, *input_paths: str) -> str:
        return super().run(self.subcommand, *input_paths)

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
        delimiter: Optional[str] = None
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
            "delimiter": delimiter
        }

class Dedup(QSVCommand):
    """Remove redundant rows."""

    def __init__(
        self,
        select: Optional[str] = None,
        numeric: bool = False,
        ignore_case: bool = False,
        unique: bool = False,
        dupes_output: Optional[str] = None,
        jobs: Optional[int] = None,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        memcheck: bool = False
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
            "memcheck": memcheck
        }

class DescribeGPT(QSVCommand):
    """Inference metadata and provide a summary of the given CSV data using an LLM."""

    def __init__(
        self,
        all_: bool = False,
        description: bool = False,
        dictionary: bool = False,
        tags: bool = False,
        dictionary_output: Optional[str] = None,
        ckan_api: Optional[str] = None,
        ckan_token: Optional[str] = None,
        stats_options: Optional[str] = None,
        num_tags: int = 10,
        tag_vocab: Optional[str] = None,
        cache_dir: str = "~/.qsv-cache",
        enum_threshold: int = 10,
        num_examples: int = 5,
        truncate_str: int = 25,
        addl_cols: bool = False,
        addl_cols_list: str = "sort_order, sortiness, mean, median, mad, stddev, variance, cv",
        prompt: Optional[str] = None,
        sql_results: Optional[str] = None,
        prompt_file: Optional[str] = None,
        sample_size: int = 100,
        fewshot_examples: bool = False,
        session: Optional[str] = None,
        session_len: int = 10,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        language: Optional[str] = None,
        addl_props: Optional[str] = None,
        api_key: Optional[str] = None,
        max_tokens: int = 10000,
        timeout: int = 300,
        user_agent: Optional[str] = None,
        export_prompt: Optional[str] = None,
        no_cache: bool = False,
        disk_cache_dir: Optional[str] = None,
        redis_cache: bool = False,
        fresh: bool = False,
        forget: bool = False,
        flush_cache: bool = False,
        format: str = "markdown",
        output: Optional[str] = None,
        quiet: bool = False,
        delimiter: Optional[str] = None,
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
            "addl_cols_list": addl_cols_list if addl_cols_list != "sort_order, sortiness, mean, median, mad, stddev, variance, cv" else None,
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
            "delimiter": delimiter
        }

class Enum(QSVCommand):
    """Add a new column enumerating CSV lines."""
    def __init__(
        self,
        new_column: str = "index",
        start: int = 0,
        uuid: bool = False,
        constant: Optional[str] = None,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("enum")
        self.params = {
            "new_column": new_column if new_column != "index" else None,
            "start": start if start != 0 else None,
            "uuid": uuid,
            "constant": constant,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter
        }

class Explode(QSVCommand):
    """Explode rows based on some column separator."""
    def __init__(
        self,
        column: str,
        separator: str = ",",
        rename: Optional[str] = None,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("explode")
        self.column = column
        self.params = {
            "separator": separator if separator != "," else None,
            "rename": rename,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter
        }
    
    def run(self, input_path: Optional[str] = None) -> str:
        return super().run(self.column, input_path)

class Fill(QSVCommand):
    """Fill empty values."""
    def __init__(
        self,
        value: Optional[str] = None,
        backfill: bool = False,
        groupby: Optional[str] = None,
        select: Optional[str] = None,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("fill")
        self.params = {
            "value": value,
            "backfill": backfill,
            "groupby": groupby,
            "select": select,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter
        }

class FixLengths(QSVCommand):
    """Makes all records have same length."""
    def __init__(
        self,
        length: Optional[int] = None,
        output: Optional[str] = None,
        delimiter: Optional[str] = None
    ):
        super().__init__("fixlengths")
        self.params = {
            "length": length,
            "output": output,
            "delimiter": delimiter
        }

class Flatten(QSVCommand):
    """Prints flattened records such that fields are labeled separated by a new line."""
    def __init__(
        self,
        condense: Optional[int] = None,
        field_separator: Optional[str] = None,
        separator: str = "#",
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("flatten")
        self.params = {
            "condense": condense,
            "field_separator": field_separator,
            "separator": separator if separator != "#" else None,
            "no_headers": no_headers,
            "delimiter": delimiter
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
        escape: Optional[str] = None,
        no_final_newline: bool = False,
        output: Optional[str] = None,
        delimiter: Optional[str] = None
    ):
        super().__init__("fmt")
        self.params = {
            "out_delimiter": out_delimiter if out_delimiter != "," else None,
            "crlf": crlf,
            "ascii": ascii,
            "quote": quote if quote != '"' else None,
            "quote_always": quote_always,
            "quote_never": quote_never,
            "escape": escape,
            "no_final_newline": no_final_newline,
            "output": output,
            "delimiter": delimiter
        }

class Frequency(QSVCommand):
    """Compute a frequency table of the given CSV data."""
    def __init__(
        self,
        select: Optional[str] = None,
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
        jobs: Optional[int] = None,
        json: bool = False,
        pretty_json: bool = False,
        no_stats: bool = False,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        memcheck: bool = False,
        toon: bool = False,
        weight: Optional[str] = None
    ):
        super().__init__("frequency")
        self.params = {
            "select": select,
            "limit": limit if limit != 10 else None,
            "unq_limit": unq_limit if unq_limit != 10 else None,
            "lmt_threshold": lmt_threshold if lmt_threshold != 0 else None,
            "rank_strategy": rank_strategy if rank_strategy != "dense" else None,
            "pct_dec_places": pct_dec_places if pct_dec_places != -5 else None,
            "other_sorted": other_sorted,
            "other_text": other_text if other_text != "Other" else None,
            "asc": asc,
            "no_trim": no_trim,
            "null_text": null_text if null_text != "(NULL)" else None,
            "no_nulls": no_nulls,
            "ignore_case": ignore_case,
            "all_unique_text": all_unique_text if all_unique_text != "<ALL_UNIQUE>" else None,
            "vis_whitespace": vis_whitespace,
            "jobs": jobs,
            "json": json,
            "pretty_json": pretty_json,
            "no_stats": no_stats,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "memcheck": memcheck,
            "toon": toon,
            "weight": weight
        }

class Headers(QSVCommand):
    """Show header names."""
    def __init__(
        self,
        justify: Optional[str] = None,
        delimiter: Optional[str] = None,
        no_headers: bool = False
    ):
        super().__init__("headers")
        self.params = {
            "justify": justify,
            "delimiter": delimiter,
            "no_headers": no_headers
        }

class Index(QSVCommand):
    """Creates an index of the given CSV data."""
    def __init__(self, output: Optional[str] = None):
        super().__init__("index")
        self.params = {"output": output}

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
        keys_output: Optional[str] = None,
        ignore_case: bool = False,
        ignore_leading_zeros: bool = False,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("join")
        self.columns1 = columns1
        self.columns2 = columns2
        self.params = {
            "left": left,
            "left_anti": left_anti,
            "left_semi": left_semi,
            "right": right,
            "right_anti": right_anti,
            "right_semi": right_semi,
            "full": full,
            "cross": cross,
            "nulls": nulls,
            "keys_output": keys_output,
            "ignore_case": ignore_case,
            "ignore_leading_zeros": ignore_leading_zeros,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter
        }

    def run(self, input1: str, input2: str) -> str:
        return super().run(self.columns1, input1, self.columns2, input2)

class MoarStats(QSVCommand):
    """Computes additional statistics and outlier metadata for CSV data."""
    def __init__(
        self,
        stats_options: str = "--infer-dates --infer-boolean --mad --quartiles --percentiles --force --stats-jsonl",
        round_places: int = 4,
        use_percentiles: bool = False,
        pct_thresholds: str = "5,95",
        advanced: bool = False,
        output: Optional[str] = None
    ):
        super().__init__("moarstats")
        self.params = {
            "stats_options": stats_options if stats_options != "--infer-dates --infer-boolean --mad --quartiles --percentiles --force --stats-jsonl" else None,
            "round_places": round_places,
            "use_percentiles": use_percentiles,
            "pct_thresholds": pct_thresholds if pct_thresholds != "5,95" else None,
            "advanced": advanced,
            "output": output
        }

class Py(QSVCommand):
    """Evaluate a Python expression on CSV data."""
    def __init__(
        self,
        script: str,
        new_column: Optional[str] = None,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("py")
        self.script = script
        self.params = {
            "new_column": new_column,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter
        }
    
    def run(self, input_path: Optional[str] = None) -> str:
        return super().run(self.script, input_path)

class Rename(QSVCommand):
    """Rename the columns of CSV data efficiently."""
    def __init__(
        self,
        names: str,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("rename")
        self.names = names
        self.params = {
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter
        }
    
    def run(self, input_path: str) -> str:
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
        select: Optional[str] = None,
        unicode: bool = False,
        size_limit: int = 50,
        dfa_size_limit: int = 10,
        not_one: bool = False,
        jobs: Optional[int] = None,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        progressbar: bool = False,
        quiet: bool = False
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
            "quiet": quiet
        }
    
    def run(self, input_path: Optional[str] = None) -> str:
        return super().run(self.pattern, self.replacement, input_path)

class Reverse(QSVCommand):
    """Reverse rows of CSV data."""
    def __init__(
        self,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        memcheck: bool = False
    ):
        super().__init__("reverse")
        self.params = {
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "memcheck": memcheck
        }

class Sample(QSVCommand):
    """Randomly sample CSV data."""
    def __init__(
        self,
        size: int = 100,
        seed: Optional[int] = None,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("sample")
        self.size_arg = size
        self.params = {
            "seed": seed,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter
        }
    
    def run(self, input_path: str) -> str:
        return super().run(str(self.size_arg), input_path)

class Schema(QSVCommand):
    """Generate JSON Schema or Polars Schema from CSV data."""
    def __init__(
        self,
        enum_threshold: int = 50,
        ignore_case: bool = False,
        strict_dates: bool = False,
        strict_formats: bool = False,
        pattern_columns: Optional[str] = None,
        dates_whitelist: str = "date,time,due,open,close,created",
        prefer_dmy: bool = False,
        force: bool = False,
        stdout: bool = False,
        jobs: Optional[int] = None,
        output: Optional[str] = None,
        polars: bool = False,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        memcheck: bool = False
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
            "memcheck": memcheck
        }

class Search(QSVCommand):
    """Search CSV data with a regex."""
    def __init__(
        self,
        pattern: str,
        ignore_case: bool = False,
        select: Optional[str] = None,
        invert_match: bool = False,
        unicode: bool = False,
        flag: Optional[str] = None,
        preview: int = 0,
        count: bool = False,
        size_limit: int = 50,
        dfa_size_limit: int = 10,
        json: bool = False,
        not_one: bool = False,
        jobs: Optional[int] = None,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        progressbar: bool = False,
        quiet: bool = False
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
            "quiet": quiet
        }
    
    def run(self, input_path: Optional[str] = None) -> str:
        return super().run(self.pattern, input_path)

class SearchSet(QSVCommand):
    """Search CSV data with a regex set."""
    def __init__(
        self,
        regexset_file: str,
        ignore_case: bool = False,
        literal: bool = False,
        exact: bool = False,
        select: Optional[str] = None,
        invert_match: bool = False,
        unicode: bool = False,
        flag: Optional[str] = None,
        flag_matches_only: bool = False,
        unmatched_output: Optional[str] = None,
        quick: bool = False,
        count: bool = False,
        json: bool = False,
        size_limit: int = 50,
        dfa_size_limit: int = 10,
        not_one: bool = False,
        jobs: Optional[int] = None,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        progressbar: bool = False,
        quiet: bool = False
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
            "quiet": quiet
        }
    
    def run(self, input_path: Optional[str] = None) -> str:
        return super().run(self.regexset_file, input_path)

class Select(QSVCommand):
    """Select, re-order, duplicate or drop columns."""
    def __init__(
        self,
        selection: str,
        random: bool = False,
        seed: Optional[int] = None,
        sort: bool = False,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("select")
        self.selection = selection
        self.params = {
            "random": random,
            "seed": seed,
            "sort": sort,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter
        }

    def run(self, input_path: str) -> str:
        return super().run(self.selection, input_path)

class Slice(QSVCommand):
    """Slice records from CSV."""
    def __init__(
        self,
        index: Optional[int] = None,
        len: Optional[int] = None,
        next: bool = False,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None
    ):
        super().__init__("slice")
        self.params = {
            "index": index,
            "len": len,
            "next": next,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter
        }

class Sniff(QSVCommand):
    """Quickly sniff CSV metadata."""
    def __init__(
        self,
        sample: int = 100,
        prefer_dmy: bool = False,
        delimiter: Optional[str] = None,
        json: bool = False,
        pretty_json: bool = False,
        no_headers: bool = False
    ):
        super().__init__("sniff")
        self.params = {
            "sample": sample if sample != 100 else None,
            "prefer_dmy": prefer_dmy,
            "delimiter": delimiter,
            "json": json,
            "pretty_json": pretty_json,
            "no_headers": no_headers
        }

class Sort(QSVCommand):
    """Sort CSV data in alphabetical, numerical, reverse or random order."""
    def __init__(
        self,
        select: Optional[str] = None,
        numeric: bool = False,
        natural: bool = False,
        reverse: bool = False,
        ignore_case: bool = False,
        unique: bool = False,
        random: bool = False,
        seed: Optional[int] = None,
        rng: str = "standard",
        jobs: Optional[int] = None,
        faster: bool = False,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        memcheck: bool = False
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
            "memcheck": memcheck
        }

class Sqlp(QSVCommand):
    """Run a SQL query against several CSVs using the Pola.rs engine."""
    def __init__(
        self,
        query: str,
        format: str = "csv",
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        try_parsedates: bool = False,
        low_memory: bool = False,
        no_cache: bool = False,
        ignore_errors: bool = False
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
            "ignore_errors": ignore_errors
        }
    
    def run(self, *input_paths: str) -> str:
        return super().run(self.query, *input_paths)

class Stats(QSVCommand):
    """Computes summary statistics for CSV data."""

    def __init__(
        self,
        select: Optional[str] = None,
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
        dates_whitelist: str = "date,time,due,open,close,created",
        prefer_dmy: bool = False,
        force: bool = False,
        jobs: Optional[int] = None,
        stats_jsonl: bool = False,
        cache_threshold: int = 5000,
        vis_whitespace: bool = False,
        dataset_stats: bool = False,
        output: Optional[str] = None,
        no_headers: bool = False,
        delimiter: Optional[str] = None,
        memcheck: bool = False,
        weight: Optional[str] = None
    ):
        super().__init__("stats")
        self.params = {
            "select": select,
            "everything": everything,
            "typesonly": typesonly,
            "infer_boolean": infer_boolean,
            "boolean_patterns": boolean_patterns if boolean_patterns != "1:0,t*:f*,y*:n*" else None,
            "mode": mode,
            "cardinality": cardinality,
            "median": median,
            "mad": mad,
            "quartiles": quartiles,
            "percentiles": percentiles,
            "percentile_list": percentile_list if percentile_list != "5,10,40,60,90,95" else None,
            "round_places": round_places,
            "nulls": nulls,
            "infer_dates": infer_dates,
            "dates_whitelist": dates_whitelist if dates_whitelist != "date,time,due,open,close,created" else None,
            "prefer_dmy": prefer_dmy,
            "force": force,
            "jobs": jobs,
            "stats_jsonl": stats_jsonl,
            "cache_threshold": cache_threshold if cache_threshold != 5000 else None,
            "vis_whitespace": vis_whitespace,
            "dataset_stats": dataset_stats,
            "output": output,
            "no_headers": no_headers,
            "delimiter": delimiter,
            "memcheck": memcheck,
            "weight": weight
        }

class Validate(QSVCommand):
    """Validate CSV data for RFC4180-compliance or with JSON Schema."""
    def __init__(
        self,
        json_schema: Optional[str] = None,
        trim: bool = False,
        no_format_validation: bool = False,
        fail_fast: bool = False,
        valid_suffix: str = "valid",
        invalid_suffix: str = "invalid",
        json: bool = False,
        pretty_json: bool = False,
        valid_output: Optional[str] = None,
        jobs: Optional[int] = None,
        batch: int = 50000,
        delimiter: Optional[str] = None,
        progressbar: bool = False,
        quiet: bool = False
    ):
        super().__init__("validate")
        self.json_schema = json_schema
        self.params = {
            "trim": trim,
            "no_format_validation": no_format_validation,
            "fail_fast": fail_fast,
            "valid": valid_suffix if valid_suffix != "valid" else None,
            "invalid": invalid_suffix if invalid_suffix != "invalid" else None,
            "json": json,
            "pretty_json": pretty_json,
            "valid_output": valid_output,
            "jobs": jobs,
            "batch": batch if batch != 50000 else None,
            "delimiter": delimiter,
            "progressbar": progressbar,
            "quiet": quiet
        }
    
    def run(self, *input_paths: str) -> str:
        args = list(input_paths)
        if self.json_schema:
            args.append(self.json_schema)
        return super().run(*args)

# --- Function Wrappers for Backward Compatibility ---

def index(input_path: str, output: Optional[str] = None) -> str:
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
