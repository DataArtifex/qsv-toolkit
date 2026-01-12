# qsv tojsonl

```text
Smartly converts CSV to a newline-delimited JSON (JSONL/NDJSON).

By computing stats on the CSV first, it "smartly" infers the appropriate JSON data type
for each column (string, number, boolean, null).

It will infer a column as boolean if its cardinality is 2, and the first character of
the values are one of the following case-insensitive combinations:
  t/f; t/null; 1/0; 1/null; y/n & y/null are treated as true/false.

The `tojsonl` command will reuse a `stats.csv.data.jsonl` file if it exists and is
current (i.e. stats generated with --cardinality and --infer-dates options) and will
skip recomputing stats.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_tojsonl.rs.

Usage:
    qsv tojsonl [options] [<input>]
    qsv tojsonl --help

Tojsonl options:
    --trim                 Trim leading and trailing whitespace from fields
                           before converting to JSON.
    --no-boolean           Do not infer boolean fields.
    -j, --jobs <arg>       The number of jobs to run in parallel.
                           When not set, the number of jobs is set to the
                           number of CPUs detected.
    -b, --batch <size>     The number of rows per batch to load into memory,
                           before running in parallel. Automatically determined
                           for CSV files with more than 50000 rows.
                           Set to 0 to load all rows in one batch.
                           Set to 1 to force batch optimization even for files with
                           less than 50000 rows.
                           [default: 50000]                           

Common options:
    -h, --help             Display this message
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -o, --output <file>    Write output to <file> instead of stdout.
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
    -q, --quiet            Do not display enum/const list inferencing messages.
```
