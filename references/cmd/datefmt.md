# qsv datefmt

```text
Formats recognized date fields (19 formats recognized) to a specified date format
using strftime date format specifiers.

For recognized date formats, see
https://github.com/dathere/qsv-dateparser?tab=readme-ov-file#accepted-date-formats

See https://docs.rs/chrono/latest/chrono/format/strftime/ for 
accepted date format specifiers for --formatstr.
Defaults to ISO 8601/RFC 3339 format when --formatstr is not specified.
( "%Y-%m-%dT%H:%M:%S%z" - e.g. 2001-07-08T00:34:60.026490+09:30 )

Examples:
Format dates in Open Date column to ISO 8601/RFC 3339 format:

  $ qsv datefmt 'Open Date' file.csv

Format multiple date columns in file.csv to ISO 8601/RFC 3339 format:

  $ qsv datefmt 'Open Date,Modified Date,Closed Date' file.csv

Format all columns that end with "_date" case-insensitive in file.csv to ISO 8601/RFC 3339 format:

  $ qsv datefmt '/(?i)_date$/' file.csv

Format dates in OpenDate column using '%Y-%m-%d' format:

  $ qsv datefmt OpenDate --formatstr '%Y-%m-%d' file.csv

Format multiple date columns using '%Y-%m-%d' format:

  $ qsv datefmt OpenDate,CloseDate,ReopenDate --formatstr '%Y-%m-%d' file.csv

Get the week number for OpenDate and store it in the week_number column:

  $ qsv datefmt OpenDate --formatstr '%V' --new-column week_number file.csv

Get the day of the week for several date columns and store it in the corresponding weekday columns:

  $ qsv datefmt OpenDate,CloseDate --formatstr '%u' --rename Open_weekday,Close_weekday file.csv

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_datefmt.rs.

Usage:
qsv datefmt [--formatstr=<string>] [options] <column> [<input>]
qsv datefmt --help

datefmt arguments:
    <column>                    The column/s to apply the date formats to.
                                Note that the <column> argument supports multiple columns.
                                See 'qsv select --help' for the format details.

    --formatstr=<string>        The date format to use for the datefmt operation.
                                The date format to use. For formats, see
                                https://docs.rs/chrono/latest/chrono/format/strftime/
                                Default to ISO 8601 / RFC 3339 date & time format -
                                "%Y-%m-%dT%H:%M:%S%z" - e.g. 2001-07-08T00:34:60.026490+09:30
                                [default: %+]
        
    <input>                     The input file to read from. If not specified, reads from stdin.

datefmt options:
    -c, --new-column <name>     Put the transformed values in a new column instead.
    -r, --rename <name>         New name for the transformed column.
    --prefer-dmy                Prefer to parse dates in dmy format. Otherwise, use mdy format.
    --keep-zero-time            If a formatted date ends with "T00:00:00+00:00", keep the time
                                instead of removing it.
    --input-tz=<string>         The timezone to use for the input date if the date does not have
                                timezone specified. The timezone must be a valid IANA timezone name or
                                the string "local" for the local timezone.
                                See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
                                for a list of valid timezone names.
                                [default: UTC]
    --output-tz=<string>        The timezone to use for the output date.
                                The timezone must be a valid IANA timezone name or the string "local".
                                [default: UTC]
    --default-tz=<string>       The timezone to use for BOTH input and output dates when they do have timezone.
                                Shortcut for --input-tz and --output-tz set to the same timezone.
                                The timezone must be a valid IANA timezone name or the string "local".
    --utc                       Shortcut for --input-tz and --output-tz set to UTC.
    --zulu                      Shortcut for --output-tz set to UTC and --formatstr set to "%Y-%m-%dT%H:%M:%SZ".
    -R, --ts-resolution <res>   The resolution to use when parsing Unix timestamps.
                                Valid values are "sec", "milli", "micro", "nano".
                                [default: sec]
    -j, --jobs <arg>            The number of jobs to run in parallel.
                                When not set, the number of jobs is set to the number of CPUs detected.
    -b, --batch <size>          The number of rows per batch to load into memory, before running in parallel.
                                Automatically determined for CSV files with more than 50000 rows.
                                Set to 0 to load all rows in one batch. Set to 1 to force batch optimization
                                even for files with less than 50000 rows.
                                [default: 50000]

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout.
    -n, --no-headers            When set, the first row will not be interpreted
                                as headers.
    -d, --delimiter <arg>       The field delimiter for reading CSV data.
                                Must be a single character. (default: ,)
    -p, --progressbar           Show progress bars. Not valid for stdin.
```
