# qsv edit

```text
Replace the value of a cell specified by its row and column.

For example we have the following CSV file named items.csv:

item,color
shoes,blue
flashlight,gray

To output the data with the color of the shoes as green instead of blue, run:

  $ qsv edit items.csv color 0 green

The following is returned as output:

item,color
shoes,green
flashlight,gray

You may also choose to specify the column name by its index (in this case 1).
Specifying a column as a number is prioritized by index rather than name.
If there is no newline (\n) at the end of the input data, it may be added to the output.

Usage:
    qsv edit [options] <input> <column> <row> <value>
    qsv edit --help

edit arguments:
    input                  The file from which to edit a cell value. Use '-' for standard input.
                           Must be either CSV, TSV, TAB, or SSV data.
    column                 The cell's column name or index. Indices start from the first column as 0.
                           Providing a value of underscore (_) selects the last column.
    row                    The cell's row index. Indices start from the first non-header row as 0.
    value                  The new value to replace the old cell content with.

edit options:
    -i, --in-place         Overwrite the input file data with the output.
                           The input file is renamed to a .bak file in the same directory.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       Start row indices from the header row as 0 (allows editing the header row).
```
