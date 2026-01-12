# qsv luau

```text
Create multiple new computed columns, filter rows or compute aggregations by
executing a Luau 0.702 script for every row (SEQUENTIAL MODE) or for
specified rows (RANDOM ACCESS MODE) of a CSV file.

Luau is not just another qsv command. It is qsv's Domain-Specific Language (DSL)
for data-wrangling. 👑

The executed Luau has 3 ways to reference row columns (as strings):
  1. Directly by using column name (e.g. Amount), can be disabled with --no-globals
  2. Indexing col variable by column name: col.Amount or col["Total Balance"]
  3. Indexing col variable by column 1-based index: col[1], col[2], etc.
     This is only available with the --colindex or --no-headers options.

Of course, if your input has no headers, then 3. will be the only available
option.

It has two subcommands:
  map     - Create new columns by mapping the result of a Luau script for each row.
  filter  - Filter rows by executing a Luau script for each row. Rows that return
            true are kept, the rest are filtered out.

Some examples:

  Sum numeric columns 'a' and 'b' and call new column 'c'
  $ qsv luau map c "a + b"
  $ qsv luau map c "col.a + col['b']"
  $ qsv luau map c --colindex "col[1] + col[2]"

  There is some magic in the previous example as 'a' and 'b' are passed in
  as strings (not numbers), but Luau still manages to add them up.
  A more explicit way of doing it, is by using the tonumber() function.
  See https://luau-lang.org/library for a list of built-in functions.
  $ qsv luau map c "tonumber(a) + tonumber(b)"

  Add running total column for Amount
  $ qsv luau map Total "tot = (tot or 0) + Amount; return tot"

  Or use the --begin and --end options to compute the running & grand totals
  $ qsv luau map Total --begin "tot = 0; gtotal = 0" \
        "tot = tot + Amount; gtotal = gtotal + tot; return tot" --end "return gtotal"

  Add running total column for Amount when previous balance was 900
  $ qsv luau map Total "tot = (tot or 900) + Amount; return tot"

  Use the qsv_cumsum() helper function to compute the running total.
  See https://github.com/dathere/qsv/wiki/Luau-Helper-Functions-Examples for more examples.

  $ qsv luau map Total "qsv_cumsum(Amount)"

  Convert Amount to always-positive AbsAmount and Type (debit/credit) columns
  $ qsv luau map Type \
        "if tonumber(Amount) < 0 then return 'debit' else return 'credit' end" | \
    qsv luau map AbsAmount "math.abs(tonumber(Amount))"

  Map multiple new columns in one pass
  $ qsv luau map newcol1,newcol2,newcol3 "{cola + 1, colb + 2, colc + 3}"

  Filter some rows based on numerical filtering
  $ qsv luau filter "tonumber(a) > 45"
  $ qsv luau filter "tonumber(a) >= tonumber(b)"

PATTERN MATCHING WITH string.find AND OTHER STRING FUNCTIONS:
  Lua/Luau string functions like string.find, string.match, string.gsub use 
  PATTERN MATCHING by default, where certain characters have special meanings:
    ( ) . % + - * ? [ ] ^ $

  If you need to search for these characters literally, you have two options:

  1. Escape special characters with % (percent sign):
     $ qsv luau filter "string.find(Name, 'John %(Jr%)')"
     $ qsv luau map dots "string.gsub(col.text, '%%.', '')"

  2. Use plain text mode (4th parameter = true):
     $ qsv luau filter "string.find(Name, 'John (Jr)', 1, true)"
     $ qsv luau map match "string.find(col.text, 'Mr.', 1, true)"

  Common gotchas:
  - Parentheses in names like "Jane (Smith)" need escaping or plain mode
  - Dots in email addresses, URLs, or decimal numbers
  - Hyphens in phone numbers or dates

  For more on Lua patterns: https://www.lua.org/manual/5.4/manual.html#6.4.1

  Typing long scripts on the command line gets tiresome rather quickly. Use the
  "file:" prefix or the ".lua/.luau" file extension to read non-trivial scripts
  from the filesystem.

  In the following example, both the BEGIN and END scripts have the lua/luau file
  extension so they are read from the filesystem.  With the debitcredit.script file,
  we use the "file:" prefix to read it from the filesystem.

  $ qsv luau map Type -B init.lua file:debitcredit.script -E end.luau

With "luau map", if the MAIN script is invalid for a row, "<ERROR>" followed by a
detailed error message is returned for that row.
With "luau filter", if the MAIN script is invalid for a row, that row is not filtered.

If any row has an invalid result, an exitcode of 1 is returned and an error count
is logged.

SPECIAL VARIABLES:
  "_IDX" - a READ-only variable that is zero during the BEGIN script and
       set to the current row number during the MAIN & END scripts.

       It is primarily used in SEQUENTIAL MODE when the CSV has no index or you
       wish to process the CSV sequentially.

  "_INDEX" - a READ/WRITE variable that enables RANDOM ACCESS MODE when used in
       a script. Using "_INDEX" in a script switches qsv to RANDOM ACCESS MODE
       where setting it to a row number will change the current row to the
       specified row number. It will only work, however, if the CSV has an index.

       When using _INDEX, the MAIN script will keep looping and evaluate the row
       specified by _INDEX until _INDEX is set to an invalid row number
       (e.g. <= zero or to a value greater than _ROWCOUNT).

       If the CSV has no index, qsv will abort with an error unless "qsv_autoindex()"
       is called in the BEGIN script to create an index.

  "_ROWCOUNT" - a READ-only variable which is zero during the BEGIN & MAIN scripts,
       and set to the rowcount during the END script when the CSV has no index
       (SEQUENTIAL MODE).

       When using _INDEX and the CSV has an index, _ROWCOUNT will be set to the
       rowcount of the CSV file, even from the BEGINning
       (RANDOM ACCESS MODE).

  "_LASTROW" - a READ-only variable that is set to the last row number of the CSV.
       Like _INDEX, it will also trigger RANDOM ACCESS MODE if used in a script.

       Similarly, if the CSV has no index, qsv will also abort with an error unless
       "qsv_autoindex()" is called in the BEGIN script to create an index.

For security and safety reasons as a purpose-built embeddable interpreter,
Luau's standard library is relatively minimal (https://luau-lang.org/library).
That's why qsv bundles & preloads LuaDate v2.2.1 as date manipulation is a common task.
See https://tieske.github.io/date/ on how to use the LuaDate library.

Additional libraries can be loaded using Luau's "require" function.
See https://github.com/LewisJEllis/awesome-lua for a list of other libraries.

With the judicious use of "require", the BEGIN script & special variables, one can
create variables, tables, arrays & functions that can be used for complex aggregation
operations in the END script.

SCRIPT DEVELOPMENT TIPS:
When developing Luau scripts, be sure to take advantage of the "qsv_log" function to
debug your script. It will log messages at the level (INFO, WARN, ERROR, DEBUG, TRACE)
specified by the QSV_LOG_LEVEL environment variable (see docs/Logging.md for details).

At the DEBUG level, the log messages will be more verbose to facilitate debugging.
It will also skip precompiling the MAIN script to bytecode so you can see more
detailed error messages with line numbers.

Bear in mind that qsv strips comments from Luau scripts before executing them.
This is done so qsv doesn't falsely trigger on special variables mentioned in comments.
When checking line numbers in DEBUG mode, be sure to refer to the comment-stripped
scripts in the log file, not the original commented scripts.

There are more Luau helper functions in addition to "qsv_log", notably the powerful
"qsv_register_lookup" which allows you to "lookup" values against other
CSVs on the filesystem, a URL, datHere's lookup repo or CKAN instances.

Detailed descriptions of these helpers can be found in the "setup_helpers" section at
the bottom of this file and on the Wiki (https://github.com/dathere/qsv/wiki)

For more detailed examples, see https://github.com/dathere/qsv/blob/master/tests/test_luau.rs.

Usage:
    qsv luau map [options] -n <main-script> [<input>]
    qsv luau map [options] <new-columns> <main-script> [<input>]
    qsv luau filter [options] <main-script> [<input>]
    qsv luau map --help
    qsv luau filter --help
    qsv luau --help

Luau arguments:

    All <script> arguments/options can either be the Luau code, or if it starts with
    "file:" or ends with ".luau/.lua" - the filepath from which to load the script.

    Instead of using the --begin and --end options, you can also embed BEGIN and END
    scripts in the MAIN script by using the "BEGIN { ... }!" and "END { ... }!" syntax.

    The BEGIN script is embedded in the MAIN script by adding a BEGIN block at the
    top of the script. The BEGIN block must start at the beginning of the line.
    It can contain multiple statements.

    The MAIN script is the main Luau script to execute. It is executed for EACH ROW of
    the input CSV. It can contain multiple statements and should end with a "return" stmt.
    In map mode, the return value is/are the new value/s of the mapped column/s.
    In filter mode, the return value is a boolean indicating if the row should be filtered.

    The END script is embedded in the MAIN script by adding an END block at the bottom
    of the script. The END block must start at the beginning of the line.
    It can contain multiple statements.

    <new-columns> is a comma-separated list of new computed columns to add to the CSV
    when using "luau map". The new columns are added to the CSV after the existing
    columns, unless the --remap option is used.

Luau options:
  -g, --no-globals        Don't create Luau global variables for each column,
                          only `col`. Useful when some column names mask standard
                          Luau globals and to increase PERFORMANCE.
                          Note: access to Luau globals thru _G remains even with -g.
  --colindex              Create a 1-based column index. Useful when some column names
                          mask standard Luau globals. Automatically enabled with --no-headers.
  -r, --remap             Only the listed new columns are written to the output CSV.
                          Only applies to "map" subcommand.
  -B, --begin <script>    Luau script/file to execute in the BEGINning, before
                          processing the CSV with the main-script.
                          Typically used to initialize global variables.
                          Takes precedence over an embedded BEGIN script.
                          If <script> begins with "file:" or ends with ".luau/.lua",
                          it's interpreted as a filepath from which to load the script.
  -E, --end <script>      Luau script/file to execute at the END, after processing the
                          CSV with the main-script.
                          Typically used for aggregations.
                          The output of the END script is sent to stderr.
                          Takes precedence over an embedded END script.
                          If <script> begins with "file:" or ends with ".luau/.lua",
                          it's interpreted as a filepath from which to load the script.
  --max-errors <count>    The maximum number of errors to tolerate before aborting.
                          Set to zero to disable error limit.
                          [default: 10]
  --timeout <seconds>     Timeout for downloading lookup_tables using
                          the qsv_register_lookup() helper function.
                          [default: 60]
  --ckan-api <url>        The URL of the CKAN API to use for downloading lookup_table
                          resources using the qsv_register_lookup() helper function
                          with the "ckan://" scheme.
                          If the QSV_CKAN_API envvar is set, it will be used instead.
                          [default: https://data.dathere.com/api/3/action]
  --ckan-token <token>    The CKAN API token to use. Only required if downloading
                          private resources.
                          If the QSV_CKAN_TOKEN envvar is set, it will be used instead.
  --cache-dir <dir>       The directory to use for caching downloaded lookup_table
                          resources using the qsv_register_lookup() helper function.
                          If the directory does not exist, qsv will attempt to create it.
                          If the QSV_CACHE_DIR envvar is set, it will be used instead.
                          [default: ~/.qsv-cache]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. Automatically enables --colindex option.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -p, --progressbar      Show progress bars. Not valid for stdin.
                           Ignored in qsvdp.
                           In SEQUENTIAL MODE, the progress bar will show the
                           number of rows processed.
                           In RANDOM ACCESS MODE, the progress bar will show
                           the position of the current row being processed.
                           Enabling this option will also suppress stderr output
                           from the END script.
```
