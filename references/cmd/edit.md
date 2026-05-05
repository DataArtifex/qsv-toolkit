# qsv edit

<small>v19.1.0</small>

```text
Replace the value of a cell specified by its row and column.

Example:

items.csv
```csv
item,color
shoes,blue
flashlight,gray
```

# To output the data with the color of the shoes as green instead of blue
$ qsv edit items.csv color 0 green

```csv
item,color
shoes,green
flashlight,gray
```

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

If <row> is out of range:
  - in stdout/--output mode, the input is passed through unchanged with a warning on stderr.
  - in --in-place mode, the command errors and the input file is left untouched.

edit options:
    -i, --in-place         Overwrite the input file data with the output.
                           The input file is renamed to a .bak file in the same directory.
                           If the .bak file already exists, the command errors instead of overwriting it.
                           Symbolic links are rejected; pass the resolved path instead.
                           (Other Windows reparse points such as junction points are not detected.)

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       Start row indices from the header row as 0 (allows editing the header row).
```
