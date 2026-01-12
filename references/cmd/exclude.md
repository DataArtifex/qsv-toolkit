# qsv exclude

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

Examples:

  $ qsv exclude id records.csv id previously-processed.csv
  $ qsv exclude col1,col2 records.csv col1,col2 previously-processed.csv
  $ qsv exclude col1-col5 records.csv col1-col5 previously-processed.csv
  $ qsv exclude id records.csv id previously-processed.csv > new-records.csv
  $ qsv exclude id records.csv id previously-processed.csv --output new-records.csv
  $ qsv exclude -v id records.csv id previously-processed.csv -o intersection.csv
  $ qsv exclude --ignore-case id records.csv id previously-processed.csv
  $ qsv exclude id records.csv id previously-processed.csv |
      qsv sort > new-sorted-records.csv
  $ qsv exclude id records.csv id previously-processed.csv | qsv sort |
      qsv --sorted dedup > new-sorted-deduped-records.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_exclude.rs.

Usage:
    qsv exclude [options] <columns1> <input1> <columns2> <input2>
    qsv exclude --help

input arguments:
    <input1> is the file from which data will be removed.
    <input2> is the file containing the data to be removed from <input1>
     e.g. 'qsv exclude id records.csv id previously-processed.csv'

exclude options:
    -i, --ignore-case      When set, matching is done case insensitively.
    -v                     When set, matching rows will be the only ones included,
                           forming set intersection, instead of the ones discarded.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
