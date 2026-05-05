# qsv search

<small>v19.1.0</small>

```text
Filters CSV data by whether the given regex matches a row.

The regex is applied to selected field in each row, and if any field matches,
then the row is written to the output, and the number of matches to stderr.

The columns to search can be limited with the '--select' flag (but the full row
is still written to the output if there is a match).

Returns exitcode 0 when matches are found.
Returns exitcode 1 when no match is found, unless the '--not-one' flag is used.
Use --count to also write the number of matches to stderr (suppressed by --quiet and --json).

When --quick is enabled, no output is produced and exitcode 0 is returned on
the first match.

When the CSV is indexed, a faster parallel search is used.

Examples:

  # Search for rows where any field contains the regex 'foo.*bar' (case sensitive)
  qsv search 'foo.*bar' data.csv

  # Case insensitive search for 'error' in the 'message' column
  qsv search -i 'error' -s message data.csv

  # Search for exact matches of 'completed' in the 'status' column
  qsv search --exact 'completed' -s status data.csv

  # Search for literal string 'a.b*c' in all columns
  qsv search --literal 'a.b*c' data.csv

  # Invert match: select rows that do NOT match the regex 'test'
  qsv search --invert-match 'test' data.csv

  # Flag matched rows in a new column named 'match_flag'
  qsv search --flag match_flag 'pattern' data.csv

  # Quick search: return on first match of 'urgent' in the 'subject' column
  qsv search --quick 'urgent' -s subject data.csv

  # Preview the first 5 matches of 'warning' in all columns
  qsv search --preview-match 5 'warning' data.csv

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_search.rs.

Usage:
    qsv search [options] <regex> [<input>]
    qsv search --help

search arguments:
    <regex>                Regular expression to match. Uses Rust regex syntax.
                           See https://docs.rs/regex/latest/regex/index.html#syntax
                           or https://regex101.com with the Rust flavor for more info.
    <input>                The CSV file to read. If not given, reads from stdin.

search options:
    -i, --ignore-case      Case insensitive search. This is equivalent to
                           prefixing the regex with '(?i)'.
    --literal              Treat the regex as a literal string. This allows you to
                           search for matches that contain regex special characters.
    --exact                Match the ENTIRE field exactly. Treats the pattern
                           as a literal string (like --literal) and automatically
                           anchors it to match the complete field value (^pattern$).
    -s, --select <arg>     Select the columns to search. See 'qsv select -h'
                           for the full syntax.
    -v, --invert-match     Select only rows that did not match
    -u, --unicode          Enable unicode support. When enabled, character classes
                           will match all unicode word characters instead of only
                           ASCII word characters. Decreases performance.
    -f, --flag <column>    If given, the command will not filter rows
                           but will instead flag every row in a new column
                           named <column>, set to the row number for matched
                           rows and "0" for non-matched rows.
                           SPECIAL: if <column> is exactly "M", only matched
                           rows are returned AND only the M column is written
                           (all other columns are dropped). To use a literal
                           column name "M" without this behavior, rename it
                           afterward (e.g., with `qsv rename`).
    -Q, --quick            Return on first match with an exitcode of 0, returning
                           the row number of the first match to stderr.
                           Return exit code 1 if no match is found.
                           No output is produced.
    --preview-match <arg>  Preview the first N matches OR all matches found
                           within N milliseconds, whichever occurs first.
                           NOTE: the same numeric value is used for BOTH the
                           match count AND the millisecond timeout - choose a
                           value where one bound effectively dominates (e.g.,
                           a small count for "first N" preview, or a large
                           count for "all within N ms").
                           Returns the preview to stderr; output is still
                           written to stdout or --output as usual.
                           Forces a sequential search, even if the CSV is indexed.
    -c, --count            Write the number of matches to stderr.
                           Suppressed by --quiet and --json.
    --size-limit <mb>      Set the approximate size limit (MB) of the compiled
                           regular expression. If the compiled expression exceeds this
                           number, then a compilation error is returned.
                           Modify this only if you're getting regular expression
                           compilation errors. [default: 50]
    --dfa-size-limit <mb>  Set the approximate size of the cache (MB) used by the regular
                           expression engine's Discrete Finite Automata.
                           Modify this only if you're getting regular expression
                           compilation errors. [default: 10]
    --json                 Output the result as JSON. Fields are written
                           as key-value pairs. The key is the column name.
                           The value is the field value. The output is a
                           JSON array. If --no-headers is set, then
                           the keys are the column indices (zero-based).
                           Automatically sets --quiet (also suppresses --count).
    --not-one              Use exit code 0 instead of 1 for no match found.
    -j, --jobs <arg>       The number of jobs to run in parallel when the given CSV data has
                           an index. Note that a file handle is opened for each job.
                           When not set, defaults to the number of CPUs detected.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -p, --progressbar      Show progress bars. Not valid for stdin.
                           Disabled when running parallel search (i.e., when
                           the CSV is indexed and --jobs > 1). Sequential
                           search on an indexed CSV (--jobs 1) still shows
                           the progress bar.
    -q, --quiet            Do not write the match count (--count) or the
                           first match row number reported by --quick to stderr.
```
