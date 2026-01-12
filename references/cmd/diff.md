# qsv diff

```text
Find the difference between two CSVs with ludicrous speed.

NOTE: diff does not support stdin. A file path is required for both arguments.
      Further, PRIMARY KEY VALUES MUST BE UNIQUE WITHIN EACH CSV.
      When diffing CSVs with just a single --key column and a stats cache is
      available, diff will automatically validate for primary key uniqueness.
      If more than one --key column is specified, however, this auto-validation
      is not done.

      To check if a CSV has unique primary key values, use `qsv extdedup`
      with the same key columns using the `--select` option:

         $ qsv extdedup --select keycol data.csv --no-output

      The duplicate count will be printed to stderr.

Examples:

Find the difference between two CSVs:
    $ qsv diff left.csv right.csv

Find the difference between two CSVs. The right CSV has no headers:
    $ qsv diff left.csv --no-headers-right right-noheaders.csv

Find the difference between two CSVs. The left CSV uses a tab as the delimiter:
    $ qsv diff --delimiter-left '\t' left.csv right-tab.tsv
    # or ';' as the delimiter
    $ qsv diff --delimiter-left ';' left.csv right-semicolon.csv

Find the difference between two CSVs. The output CSV uses a tab as the delimiter
and is written to a file:
    $ qsv diff -o diff-tab.tsv --delimiter-output '\t' left.csv right.csv
    # or ';' as the delimiter
    $ qsv diff -o diff-semicolon.csv --delimiter-output ';' left.csv right.csv

Find the difference between two CSVs, comparing records that have the same values
in the first two columns:
    $ qsv diff --key 0,1 left.csv right.csv

Find the difference between two CSVs, comparing records that have the same values
in the first two columns and sort the result by the first two columns:
    $ qsv diff -k 0,1 --sort-columns 0,1 left.csv right.csv

Find the difference between two CSVs, but do not output equal field values
in the result (equal field values are replaced with the empty string). Key
field values _will_ appear in the output:
    $ qsv diff --drop-equal-fields left.csv right.csv

Find the difference between two CSVs, but do not output headers in the result:
    $ qsv diff --no-headers-output left.csv right.csv

Find the difference between two CSVs. Both CSVs have no headers, but the result should have
headers, so generic headers will be used in the form of: _col_1, _col_2, etc.:
    $ qsv diff --no-headers-left --no-headers-right left.csv right.csv

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
    --force                     Force diff and ignore stats caches for the left & right CSVs.
                                Otherwise, if available, the stats cache will be used to:
                                 * short-circuit the diff if their fingerprint hashes are
                                   identical.
                                 * check for primary key uniqueness when only one --key
                                   column is specified.

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout.
    -d, --delimiter <arg>       Set ALL delimiters to this character.
                                Overrides --delimiter-right, --delimiter-left
                                and --delimiter-output.
```
