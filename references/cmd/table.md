# qsv table

```text
Outputs CSV data as a table with columns in alignment.

Though this command is primarily designed for DISPLAYING CSV data using
"elastic tabstops" so its more human-readable, it can also be used to convert
CSV data to other special machine-readable formats:
 -  a more human-readable TSV format with the "leftendtab" alignment option
 -  Fixed-Width format with the "leftfwf" alignment option - similar to "left",
    but with the first line being a comment (prefixed with "#") that enumerates
    the position (1-based, comma-separated) of each column (e.g. "#1,10,15").

This will not work well if the CSV data contains large fields.

Note that formatting a table requires buffering all CSV data into memory.
Therefore, you should use the 'sample' or 'slice' command to trim down large
CSV data before formatting it with this command.

Usage:
    qsv table [options] [<input>]
    qsv table --help

table options:
    -w, --width <arg>      The minimum width of each column.
                           [default: 2]
    -p, --pad <arg>        The minimum number of spaces between each column.
                           [default: 2]
    -a, --align <arg>      How entries should be aligned in a column.
                           Options: "left", "right", "center". "leftendtab" & "leftfwf"
                           "leftendtab" is a special alignment that similar to "left"
                           but with whitespace padding ending with a tab character.
                           The resulting output still validates as a valid TSV file,
                           while also being more human-readable (aka "aligned" TSV).
                           "leftfwf" is similar to "left" with Fixed Width Format allgnment.
                           The first line is a comment (prefixed with "#") that enumerates
                           the position (1-based, comma-separated) of each column.
                           [default: left]
    -c, --condense <arg>   Limits the length of each field to the value
                           specified. If the field is UTF-8 encoded, then
                           <arg> refers to the number of code points.
                           Otherwise, it refers to the number of bytes.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
```
