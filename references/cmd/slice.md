# slice

```text
Returns the rows in the range specified (starting at 0, half-open interval).
The range does not include headers.

If the start of the range isn't specified, then the slice starts from the first
record in the CSV data.

If the end of the range isn't specified, then the slice continues to the last
record in the CSV data.

This operation can be made much faster by creating an index with 'qsv index'
first. With an index, the command requires parsing just the rows that are
sliced. Without an index, all rows up to the first row in the slice must be
parsed.

Usage:
    qsv slice [options] [<input>]
    qsv slice --help

slice options:
    -s, --start <arg>      The index of the record to slice from.
                           If negative, starts from the last record.
    -e, --end <arg>        The index of the record to slice to.
    -l, --len <arg>        The length of the slice (can be used instead
                           of --end).
    -i, --index <arg>      Slice a single record (shortcut for -s N -l 1).
                           If negative, starts from the last record.
    --json                 Output the result as JSON. Fields are written
                           as key-value pairs. The key is the column name.
                           The value is the field value. The output is a
                           JSON array. If --no-headers is set, then
                           the keys are the column indices (zero-based).
    --invert               slice all records EXCEPT those in the specified range.

Examples:
  # Slice from the 3rd record to the end
  $ qsv slice --start 2 data.csv

  # Slice the first three records
  $ qsv slice --start 0 --end 2 data.csv
  $ qsv slice --len 3 data.csv
  $ qsv slice -l 3 data.csv

  # Slice the last record
  $ qsv slice -s -1 data.csv

  # Slice the last 10 records
  $ qsv slice -s -10 data.csv

  # Get everything except the last 10 records
  $ qsv slice -s -10 --invert data.csv

  # Slice the first three records of the last 10 records
  $ qsv slice -s -10 -l 3 data.csv

  # Slice the second record
  $ qsv slice --index 1 data.csv
  $ qsv slice -i 1 data.csv

  # Slice from the second record, two records
  $ qsv slice -s 1 --len 2 data.csv

  # Slice records 10 to 20 as JSON
  $ qsv slice -s 9 -e 19 --json data.csv
  $ qsv slice -s 9 -l 10 --json data.csv

  # Slice records 1 to 9 and 21 to the end as JSON
  $ qsv slice -s 9 -l 10 --invert --json data.csv

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. Otherwise, the first row will always
                           appear in the output as the header row.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
