# qsv fmt

```text
Formats CSV data with a custom delimiter or CRLF line endings.

Generally, all commands in qsv output CSV data in a default format, which is
the same as the default format for reading CSV data. This makes it easy to
pipe multiple qsv commands together. However, you may want the final result to
have a specific delimiter or record separator, and this is where 'qsv fmt' is
useful.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_fmt.rs.

Usage:
    qsv fmt [options] [<input>]
    qsv fmt --help

fmt options:
    -t, --out-delimiter <arg>  The field delimiter for writing CSV data.
                               Must be a single character.
                               If set to "T", uses tab as the delimiter.
                               [default: ,]
    --crlf                     Use '\r\n' line endings in the output.
    --ascii                    Use ASCII field and record separators.
                               Use Substitute (U+00A1) as the quote character.
    --quote <arg>              The quote character to use. [default: "]
    --quote-always             Put quotes around every value.
    --quote-never              Never put quotes around any value.
    --escape <arg>             The escape character to use. When not specified,
                               quotes are escaped by doubling them.
    --no-final-newline         Do not write a newline at the end of the output.
                               This makes it easier to paste the output into Excel. 

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
