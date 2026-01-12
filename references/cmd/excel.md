# qsv excel

```text
Exports a specified Excel/ODS sheet to a CSV file.
The first non-empty row of a sheet is assumed to be the header row.

Examples:

Export the first sheet of an Excel file to a CSV file:
  $ qsv excel input.xlsx > output.csv
  $ qsv excel input.xlsx --output output.csv

Export the first sheet of an ODS file to a CSV file:
  $ qsv excel input.ods > output.csv
  $ qsv excel input.ods -o output.csv

Export the first sheet of an Excel file to a CSV file with different delimiters:
  # semicolon
  $ qsv excel input.xlsx -d ";" > output.csv
  # tab
  $ qsv excel input.xlsx -d "\t" > output.tsv

Export a sheet by name (case-insensitive):
  $ qsv excel --sheet "Sheet 3" input.xlsx

Export a sheet by index:
  # this exports the 3nd sheet (0-based index)
  $ qsv excel -s 2 input.xlsx

Export the last sheet (negative index)):
  $ qsv excel -s -1 input.xlsx

Export the second to last sheet:
  $ qsv excel -s -2 input.xls

Export a table named "Table1" in an XLSX file. Note that --sheet is not required
as the table definition includes the sheet.
  $ qsv excel --table "Table1" input.xlsx

Export a range of cells in the first sheet:
  $ qsv excel --range C3:T25 input.xlsx

Export a named range in the workbook. Note that --sheet is not required
as named ranges include the sheet.
  $ qsv excel --range MyRange input.xlsx

Export a range of cells in the second sheet:
  $ qsv excel --range C3:T25 -s 1 input.xlsx

Export a range of cells in a sheet by name.
Note the range name must be enclosed in single quotes in certain shells
as it may contain special characters like ! and $:
  $ qsv excel --range 'Sheet2!C3:T25' input.xlsx
  $ qsv excel --range 'Sheet2!$C$3:$T$25' input.xlsx

Export the cell C3 in the first sheet:
  $ qsv excel --cell C3 input.xlsx

Export a single cell from a specific sheet:
  $ qsv excel --cell 'Sheet2!C3' input.xlsx

Export metadata for all sheets in CSV format:
  $ qsv excel --metadata csv input.xlsx
  $ qsv excel --metadata c input.xlsx
  # short CSV mode is much faster, but doesn't contain as much metadata
  $ qsv excel --metadata short input.xlsx
  $ qsv excel --metadata s input.xlsx

Export metadata for all sheets in JSON format:
  $ qsv excel --metadata json input.xlsx
  $ qsv excel --metadata j input.xlsx
  # pretty-printed JSON - first letter is capital J
  $ qsv excel --metadata J input.xlsx
  # short, minified JSON mode - first letter is capital S
  $ qsv excel --metadata Short input.xlsx
  $ qsv excel --metadata S input.xlsx

Prompt for spreadsheets to export and then prompt where to save the CSV:
  $ qsv prompt -d ~/Documents -m 'Select a spreadsheet to export to CSV' -F xlsx,xls,ods | \
      qsv excel - | qsv prompt -m 'Save exported CSV to...' --fd-output

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_excel.rs.

Usage:
    qsv excel [options] [<input>]
    qsv excel --help

Excel argument:
    <input>                   The spreadsheet file to read. Use "-" to read from stdin.
                              Supported formats: xls, xlsx, xlsm, xlsb, ods.

Excel options:
    -s, --sheet <name/index>   Name (case-insensitive) or zero-based index of sheet to export.
                               Negative indices start from the end (-1 = last sheet).
                               If the sheet cannot be found, qsv will read the first sheet.
                               [default: 0]
    --header-row <row>         The header row. Set if other than the first non-empty row of the sheet.
    --metadata <c|s|j|J|S>     Outputs workbook metadata in CSV or JSON format:
                                 index, sheet_name, headers, type, visible, column_count, row_count,
                                 safe_headers, safe_headers_count, unsafe_headers, unsafe_headers_count
                                 and duplicate_headers_count, names, name_count, tables, table_count.
                               headers is a list of the first row which is presumed to be the header row.
                               type is the sheet type (WorkSheet, DialogSheet, MacroSheet, ChartSheet, Vba).
                               visible is the sheet visibility (Visible, Hidden, VeryHidden).
                               row_count includes all rows, including the first row.
                               safe_headers is a list of headers with "safe"(PostgreSQL-ready) names.
                               unsafe_headers is a list of headers with "unsafe" names.
                               duplicate_headers_count is a count of duplicate header names.
                               names is a list of defined names in the workbook, with the associated formula.
                               name_count is the number of defined names in the workbook.
                               tables is a list of tables in the workbook, along with the sheet where
                                the table is found, the columns and the column_count.  (XLSX only)
                               table_count is the number of tables in the workbook.  (XLSX only)

                               In CSV(c) mode, the output is in CSV format.
                               In short(s) CSV mode, the output is in CSV format with only the
                                index, sheet_name, type and visible fields.

                               In JSON(j) mode, the output is minified JSON.
                               In Pretty JSON(J) mode, the output is pretty-printed JSON.
                               In Short(S) JSON mode, the output is minified JSON with only the
                                 index, sheet_name, type and visible fields.
                               For all JSON modes, the filename, the full file path, the workbook format
                                and the number of sheets are also included.
                               If metadata retrieval performance is a concern, use the short modes
                               as they return instantaneously as they don't need to process the sheet data.

                               If this option is used, all other Excel options are ignored.
                               [default: none]

    --table <table>            An Excel table (case-insensitive) to extract to a CSV.
                               Only valid for XLSX files. The --sheet option is ignored as a table could
                               be in any sheet. Overrides --range option.
    --range <range>            An Excel format range - like RangeName, C:T, C3:T25 or 'Sheet1!C3:T25' to
                               extract to the CSV. If the specified range contains the required sheet,
                               the --sheet option is ignored.
                               If the range is not found, qsv will exit with an error.
    --cell <cell>              A single cell reference - like C3 or 'Sheet1!C3' to extract.
                               This is a convenience option equivalent to --range C3:C3.
                               If both --cell and --range are specified, --cell takes precedence.

    --error-format <format>    The format to use when formatting error cells.
                               There are 3 formats:
                                 - "code": return the error code.
                                    (#DIV/0!; #N/A; #NAME?; #NULL!; #NUM!; #REF!; #VALUE!; #DATA!)
                                 - "formula": return the formula, prefixed with '#'.
                                    (e.g. #=A1/B1 where B1 is 0; #=100/0)
                                 - "both": return both error code and the formula.
                                    (e.g. #DIV/0!: =A1/B1)
                               [default: code]
    --flexible                 Continue even if the number of columns is different from row to row.
    --trim                     Trim all fields so that leading & trailing whitespaces are removed.
                               Also removes embedded linebreaks.
    --date-format <format>     Optional date format to use when formatting dates.
                               See https://docs.rs/chrono/latest/chrono/format/strftime/index.html
                               for the full list of supported format specifiers.
                               Note that if a date format is invalid, qsv will fall back and
                               return the date as if no date-format was specified.
     --keep-zero-time          Keep the time part of a date-time field if it is 00:00:00.
                               By default, qsv will remove the time part if it is 00:00:00.
     -j, --jobs <arg>          The number of jobs to run in parallel.
                               When not set, the number of jobs is set to the number of CPUs detected.

Common options:
    -h, --help                 Display this message
    -o, --output <file>        Write output to <file> instead of stdout.
    -d, --delimiter <arg>      The delimiter to use when writing CSV data.
                               Must be a single character. [default: ,]
    -q, --quiet                Do not display export summary message.
```
