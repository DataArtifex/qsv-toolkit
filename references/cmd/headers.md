# headers

```text
Prints the fields of the first row in the CSV data.

These names can be used in commands like 'select' to refer to columns in the
CSV data.

Note that multiple CSV files may be given to this command. This is useful with
the --intersect flag.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_headers.rs.

Usage:
    qsv headers [options] [<input>...]
    qsv headers --help

headers arguments:
    <input>...             The CSV file(s) to read. Use '-' for standard input.
                           If input is a directory, all files in the directory will
                           be read as input.
                           If the input is a file with a '.infile-list' extension,
                           the file will be read as a list of input files.
                           If the input are snappy-compressed files(s), it will be
                           decompressed automatically.

headers options:
    -j, --just-names       Only show the header names (hide column index).
                           This is automatically enabled if more than one
                           input is given.
    -J, --just-count       Only show the number of headers.
    --intersect            Shows the intersection of all headers in all of
                           the inputs given.
    --trim                 Trim space & quote characters from header name.

Common options:
    -h, --help             Display this message
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
