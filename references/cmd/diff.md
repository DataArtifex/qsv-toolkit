# qsv diff

<small>19.1.0</small>
```text
Find the difference between two CSVs with ludicrous speed.

NOTE: diff does not support stdin. A file path is required for both arguments.
      Further, PRIMARY KEY VALUES MUST BE UNIQUE WITHIN EACH CSV.

      To check if a CSV has unique primary key values, use `qsv extdedup`
      with the same key columns using the `--select` option:

         $ qsv extdedup --select keycol data.csv --no-output

      The duplicate count will be printed to stderr.

Examples:

# Find the difference between two CSVs
qsv diff left.csv right.csv

# Find the difference between two CSVs when the right CSV has no headers
qsv diff left.csv --no-headers-right right-noheaders.csv

# Find the difference between two CSVs when the left CSV uses a tab delimiter
qsv diff --delimiter-left '\t' left.csv right-tab.tsv

# Find the difference between two CSVs when the left CSV uses a semicolon delimiter
qsv diff --delimiter-left ';' left.csv right-semicolon.csv

# Find the difference between two CSVs and write output with tab delimiter to a file
qsv diff -o diff-tab.tsv --delimiter-output '\t' left.csv right.csv

# Find the difference between two CSVs and write output with semicolon delimiter to a file
qsv diff -o diff-semicolon.csv --delimiter-output ';' left.csv right.csv

# Find the difference comparing records with the same values in the first two columns
qsv diff --key 0,1 left.csv right.csv

# Find the difference using first two columns as key and sort result by those columns
qsv diff -k 0,1 --sort-columns 0,1 left.csv right.csv

# Find the difference but replace equal field values with empty string (key fields still appear)
qsv diff --drop-equal-fields left.csv right.csv

# Find the difference but do not output headers in the result
qsv diff --no-headers-output left.csv right.csv

# Find the difference when both CSVs have no headers (generic headers _col_1, _col_2, etc. are used)
qsv diff --no-headers-left --no-headers-right left.csv right.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_diff.rs

Usage:
    qsv diff [options] [<input-left>] [<input-right>]
    qsv diff --help

diff options:
    --no-headers-left           When set, the first row will be considered as part of
                                the left CSV to diff. (When not set, the
                                first row is the header row and will be skipped during
                                the diff. It will always appear in the output.)
    --no-headers-right          When set, the first row will be considered as part of
                                the right CSV to diff. (When not set, the
                                first row is the header row and will be skipped during
                                the diff. It will always appear in the output.)
    --no-headers-output         When set, the diff result won't have a header row in
                                its output. If not set and both CSVs have no headers,
                                headers in the result will be: _col_1,_col_2, etc.
    --delimiter-left <arg>      The field delimiter for reading CSV data on the left.
                                Must be a single character. (default: ,)
    --delimiter-right <arg>     The field delimiter for reading CSV data on the right.
                                Must be a single character. (default: ,)
    --delimiter-output <arg>    The field delimiter for writing the CSV diff result.
                                Must be a single character. (default: ,)
    -k, --key <arg...>          The column indices that uniquely identify a record
                                as a comma separated list of 0-based indices, e.g. 0,1,2
                                or column names, e.g. name,age.
                                Note that when selecting columns by name, only the
                                left CSV's headers are used to match the column names
                                and it is assumed that the right CSV has the same
                                selected column names in the same order as the left CSV.
                                (default: 0)
    --sort-columns <arg...>     The column indices by which the diff result should be
                                sorted as a comma separated list of indices, e.g. 0,1,2
                                or column names, e.g. name,age.
                                Records in the diff result that are marked as "modified"
                                ("delete" and "add" records that have the same key,
                                but have different content) will always be kept together
                                in the sorted diff result and so won't be sorted
                                independently from each other.
                                Note that when selecting columns by name, only the
                                left CSV's headers are used to match the column names
                                and it is assumed that the right CSV has the same
                                selected column names in the same order as the left CSV.
    --drop-equal-fields         Drop values of equal fields in modified rows of the CSV
                                diff result (and replace them with the empty string).
                                Key field values will not be dropped.
    -j, --jobs <arg>            The number of jobs to run in parallel.
                                When not set, the number of jobs is set to the number
                                of CPUs detected.

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout.
    -d, --delimiter <arg>       Set ALL delimiters to this character.
                                Overrides --delimiter-right, --delimiter-left
                                and --delimiter-output.
```
