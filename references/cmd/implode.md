# qsv implode

<small>19.1.0</small>
```text
Implodes multiple rows into one by grouping on key column(s) and joining the
values of another column with the given separator. The inverse of `explode`.

Examples:

```csv
name,color
John,blue
John,yellow
John,light red
Mary,red
```

# Can be imploded by key column "name", joining the "color" column with "; "
$ qsv implode -k name -v color "; " data.csv

```csv
name,color
John,blue; yellow; light red
Mary,red
```

# With `-r colors` the value column is renamed
$ qsv implode -k name -v color -r colors "; " data.csv

```csv
name,colors
John,blue; yellow; light red
Mary,red
```

Only the key column(s) and the value column appear in the output; any other
columns are dropped.

By default, all input rows are buffered in memory and groups are emitted in the
order keys are first seen. If the input is already sorted by the key column(s),
use --sorted to stream groups as they are seen (memory proportional to the
largest group, not the whole input).

Usage:
    qsv implode [options] -k <keys> -v <value> <separator> [<input>]
    qsv implode --help

implode options:
    -k, --keys <keys>      Key column(s) to group by. Supports the usual
                           selector syntax (e.g. "name", "1", "1-3", "a,c").
    -v, --value <value>    The column whose values will be joined per group.
                           Must resolve to exactly one column.
    -r, --rename <name>    New name for the imploded value column.
    --sorted               Assume input is pre-sorted by the key column(s).
                           Streams groups as they are seen; memory is bounded
                           by the size of the largest group.
    --skip-empty           Skip empty values when joining. By default, empty
                           values are included as empty tokens so that
                           round-tripping with `explode` is lossless.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
