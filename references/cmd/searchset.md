# qsv searchset

```text
Filters CSV data by whether the given regex set matches a row.

Unlike the search operation, this allows regex matching of multiple regexes 
in a single pass.

The regexset-file is a plain text file with multiple regexes, with a regex on 
each line.

The regex set is applied to each field in each row, and if any field matches,
then the row is written to the output, and the number of matches to stderr.

The columns to search can be limited with the '--select' flag (but the full row
is still written to the output if there is a match).

Returns exitcode 0 when matches are found, returning number of matches to stderr.
Returns exitcode 1 when no match is found, unless the '--not-one' flag is used.

When --quick is enabled, no output is produced and exitcode 0 is returned on 
the first match.

When the CSV is indexed, a faster parallel search is used.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_searchset.rs.

Usage:
    qsv searchset [options] (<regexset-file>) [<input>]
    qsv searchset --help

searchset arguments:
    <regexset-file>            The file containing regular expressions to match, with a 
                               regular expression on each line.
                               See https://docs.rs/regex/latest/regex/index.html#syntax
                               or https://regex101.com with the Rust flavor for regex syntax.
    <input>                    The CSV file to read. If not given, reads from stdin.

searchset options:
    -i, --ignore-case          Case insensitive search. This is equivalent to
                               prefixing the regex with '(?i)'.
    --literal                  Treat the regex as a literal string. This allows you to
                               search for matches that contain regex special characters.
    --exact                    Match the ENTIRE field exactly. Treats the pattern
                               as a literal string (like --literal) and automatically
                               anchors it to match the complete field value (^pattern$).
    -s, --select <arg>         Select the columns to search. See 'qsv select -h'
                               for the full syntax.
    -v, --invert-match         Select only rows that did not match
    -u, --unicode              Enable unicode support. When enabled, character classes
                               will match all unicode word characters instead of only
                               ASCII word characters. Decreases performance.

    -f, --flag <column>        If given, the command will not filter rows
                               but will instead flag the found rows in a new
                               column named <column>. For each found row, <column>
                               is set to the row number of the row, followed by a
                               semicolon, then a list of the matching regexes.
    --flag-matches-only        When --flag is enabled, only rows that match are
                               sent to output. Rows that do not match are filtered.
    --unmatched-output <file>  When --flag-matches-only is enabled, output the rows
                               that did not match to <file>.

    -Q, --quick                Return on first match with an exitcode of 0, returning
                               the row number of the first match to stderr.
                               Return exit code 1 if no match is found.
                               No output is produced. Ignored if --json is enabled.
    -c, --count                Return number of matches to stderr.
                               Ignored if --json is enabled.
    -j, --json                 Return number of matches, number of rows with matches,
                               and number of rows to stderr in JSON format.
    --size-limit <mb>          Set the approximate size limit (MB) of the compiled
                               regular expression. If the compiled expression exceeds this 
                               number, then a compilation error is returned.
                               Modify this only if you're getting regular expression
                               compilation errors. [default: 50]
    --dfa-size-limit <mb>      Set the approximate size of the cache (MB) used by the regular
                               expression engine's Discrete Finite Automata.
                               Modify this only if you're getting regular expression
                               compilation errors. [default: 10]
    --not-one                  Use exit code 0 instead of 1 for no match found.
    --jobs <arg>               The number of jobs to run in parallel when the given CSV data has
                               an index. Note that a file handle is opened for each job.
                               When not set, defaults to the number of CPUs detected.

Common options:
    -h, --help                 Display this message
    -o, --output <file>        Write output to <file> instead of stdout.
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. (i.e., They are not searched, analyzed,
                               sliced, etc.)
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character. (default: ,)
    -p, --progressbar          Show progress bars. Not valid for stdin.
    -q, --quiet                Do not return number of matches to stderr.
```
