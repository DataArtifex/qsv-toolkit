# flatten

```text
Prints flattened records such that fields are labeled separated by a new line.
This mode is particularly useful for viewing one record at a time. Each
record is separated by a special '#' character (on a line by itself), which
can be changed with the --separator flag.

There is also a condensed view (-c or --condense) that will shorten the
contents of each field to provide a summary view.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_flatten.rs.

Usage:
    qsv flatten [options] [<input>]
    qsv flatten --help

flatten options:
    -c, --condense <arg>          Limits the length of each field to the value
                                  specified. If the field is UTF-8 encoded, then
                                  <arg> refers to the number of code points.
                                  Otherwise, it refers to the number of bytes.
    -f, --field-separator <arg>   A string of character to write between a column name
                                  and its value.
    -s, --separator <arg>         A string of characters to write after each record.
                                  When non-empty, a new line is automatically
                                  appended to the separator.
                                  [default: #]

Common options:
    -h, --help             Display this message
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. When set, the name of each field
                           will be its index.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
