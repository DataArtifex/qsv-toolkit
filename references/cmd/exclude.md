# qsv exclude

<small>19.1.0</small>
```text
Removes a set of CSV data from another set based on the specified columns.

Also can compute the intersection of two CSV sets with the -v flag.

Matching is always done by ignoring leading and trailing whitespace. By default,
matching is done case sensitively, but this can be disabled with the --ignore-case
flag.

The columns arguments specify the columns to match for each input. Columns can
be referenced by name or index, starting at 1. Specify multiple columns by
separating them with a comma. Specify a range of columns with `-`. Both
columns1 and columns2 must specify exactly the same number of columns.
(See 'qsv select --help' for the full syntax.)

Either <input1> or <input2> can be set to `-` to read from stdin, but not both.

Examples:

  # Remove all records in previously-processed.csv from records.csv
  qsv exclude id records.csv id previously-processed.csv

  # Remove all records in previously-processed.csv matching on multiple columns
  qsv exclude col1,col2 records.csv col1,col2 previously-processed.csv

  # Remove all records in previously-processed.csv matching on column ranges
  qsv exclude col1-col5 records.csv col1-col5 previously-processed.csv

  # Remove all records in previously-processed.csv with the same id from records.csv
  # and write to new-records.csv
  qsv exclude id records.csv id previously-processed.csv > new-records.csv

  # Remove all records in previously-processed.csv with the same id from records.csv
  # and write to new-records.csv
  qsv exclude id records.csv id previously-processed.csv --output new-records.csv

  # Get the intersection of records.csv and previously-processed.csv on id column
  # (i.e., only records present in both files)
  qsv exclude -v id records.csv id previously-processed.csv -o intersection.csv

  # Do a case insensitive exclusion on the id column
  qsv exclude --ignore-case id records.csv id previously-processed.csv

  # Read records.csv from stdin
  cat records.csv | qsv exclude id - id previously-processed.csv

  # Chain exclude with sort to create a new sorted records file without previously processed records
  qsv exclude id records.csv id previously-processed.csv | \
      qsv sort > new-sorted-records.csv

  # Chain exclude with sort and dedup to create a new sorted deduped records file
  qsv exclude id records.csv id previously-processed.csv | qsv sort | \
      qsv --sorted dedup > new-sorted-deduped-records.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_exclude.rs.

Usage:
    qsv exclude [options] <columns1> <input1> <columns2> <input2>
    qsv exclude --help

input arguments:
    <input1> is the file from which data will be removed.
    <input2> is the file containing the data to be removed from <input1>
     e.g. 'qsv exclude id records.csv id previously-processed.csv'
    Either input may be set to `-` to read from stdin, but not both.

exclude options:
    -i, --ignore-case      When set, matching is done case insensitively.
    -v, --invert           When set, matching rows will be the only ones included,
                           forming set intersection, instead of the ones discarded.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load <input2>
                           into memory using CONSERVATIVE heuristics.
```
