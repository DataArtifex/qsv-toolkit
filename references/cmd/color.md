# qsv color

<small>19.1.0</small>
```text
Outputs tabular data as a pretty, colorized table that always fits into the
terminal.

Tabular data formats include CSV and its dialects, Arrow, Avro/IPC, Parquet,
JSON Array & JSONL. Note that non-CSV formats require the "polars" feature.

Requires buffering all tabular data into memory. Therefore, you should use the
'sample' or 'slice' command to trim down large CSV data before formatting
it with this command.

Color is turned off when redirecting or running CI. Set QSV_FORCE_COLOR=1
to override this behavior.

The color theme is detected based on the current terminal background color
if possible. Set QSV_THEME to DARK or LIGHT to skip detection. QSV_TERMWIDTH
can be used to override terminal size.

Usage:
    qsv color [options] [<input>]
    qsv color --help

color options:
    -C, --color            Force color on, even in situations where colors
                           would normally be disabled.
    -n, --row-numbers      Show row numbers.
    -t, --title <str>      Add a title row above the headers.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
```
