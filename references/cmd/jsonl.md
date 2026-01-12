# qsv jsonl

```text
Convert newline-delimited JSON (JSONL/NDJSON) to CSV.

The command tries to do its best but since it is not possible to
straightforwardly convert JSON lines to CSV, the process might lose some complex
fields from the input.

Also, it will fail if the JSON documents are not consistent with one another,
as the first JSON line will be used to infer the headers of the CSV output.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_jsonl.rs.

Usage:
    qsv jsonl [options] [<input>]
    qsv jsonl --help

jsonl options:
    --ignore-errors        Skip malformed input lines.
    -j, --jobs <arg>       The number of jobs to run in parallel.
                           When not set, the number of jobs is set to the 
                           number of CPUs detected.
    -b, --batch <size>     The number of rows per batch to load into memory,
                           before running in parallel. Set to 0 to load all
                           rows in one batch. [default: 50000]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The delimiter to use when writing CSV data.
                           Must be a single character. [default: ,]
```
