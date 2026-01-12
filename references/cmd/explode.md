# qsv explode

```text
Explodes a row into multiple ones by splitting a column value based on the
given separator.

For instance the following CSV:

name,colors
John,blue|yellow
Mary,red

Can be exploded on the "colors" <column> based on the "|" <separator> to:

name,colors
John,blue
John,yellow
Mary,red

Usage:
    qsv explode [options] <column> <separator> [<input>]
    qsv explode --help

explode options:
    -r, --rename <name>    New name for the exploded column.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
