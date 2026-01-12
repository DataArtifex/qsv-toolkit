# qsv rename

```text
Rename the columns of a CSV efficiently. It has two modes of operation:

Positional mode (default):
The new column names are given as a comma-separated list of names.
The number of column names given MUST match the number of columns in the
CSV unless "_all_generic" is used.

Pairwise mode:
The new column names are given as a comma-separated list of pairs of old and new
column names. The format is "old1,new1,old2,new2,...".

Examples:
  Change the column names of a CSV with three columns:
  $ qsv rename id,name,title

  Rename only specific columns using pairs:
  $ qsv rename --pairwise oldname,newname,oldcol,newcol

  Replace the column names with generic ones (_col_N):
  $ qsv rename _all_generic

  Add generic column names to a CSV with no headers:
  $ qsv rename _all_generic --no-headers

  Use column names that contains commas and conflict with the separator:
  $ qsv rename '"Date - Opening","Date - Actual Closing"'

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_rename.rs.

Usage:
    qsv rename [options] [--] <headers> [<input>]
    qsv rename --help

rename arguments:
    <headers>              The new headers to use for the CSV.
                           Separate multiple headers with a comma.
                           If "_all_generic" is given, the headers will be renamed
                           to generic column names, where the column name uses
                           the format "_col_N" where N is the 1-based column index.
                           Alternatively, specify pairs of old,new column names
                           to rename only specific columns.
    --pairwise             Invoke pairwise renaming.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the header will be inserted on top.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
