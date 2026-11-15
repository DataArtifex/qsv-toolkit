# qsv denull

<small>v28.0.0</small>

```text
Detect null sentinels - literal text like "NULL" or "N/A" standing in for a missing
value - that stop a numeric column from being recognized as numeric.

A cell holding the text "NULL" is a VALUE, not a null. `qsv stats` therefore types
the whole column as String, its nullcount stays 0, and no quartiles are computed.
Everything downstream degrades quietly: `viz smart` drops the column, `schema`
declares it a string, and `describegpt` describes a category that isn't one.

denull scans each column ONCE, with bounded memory, and partitions its values into
those that parse as a finite number and those that don't. A column is CONFIRMED when
every non-numeric value it holds is a known null sentinel and at least two distinct
numeric values remain.

A column is REJECTED - with the reason - when it cannot be promoted anyway: another
value is not a sentinel ("OK"), its numbers carry leading zeros and are really codes
("007"), or it buries the sentinel under more than --max-distinct other non-numeric
values.

Only columns worth acting on are listed: those holding a known sentinel, and those
that are predominantly numeric, whose few odd values are candidates for a sentinel
denull does not know yet - name them with --add-vocab. An ordinary categorical is
not a near miss and is not reported; nor is a free-text column that merely happens
to be unpromotable. Use --all-columns to see everything scanned.

The scan is exhaustive, not sampled: a column is never confirmed on the strength of
the values that happen to sort first. A genuine free-text column disqualifies itself
as soon as it accumulates --max-distinct different non-numeric values, so memory
stays flat. A 434 MB, 86-column file peaks at ~40 MB - the same as a type-inference
pass, and ~19x less than an exhaustive frequency table of every distinct value.

By default denull only REPORTS; it never rewrites your data. Pass --apply to
rewrite it, blanking sentinels ONLY in the columns denull CONFIRMED. A column it
REJECTED is copied through untouched, as is every column it did not scan:

  $ qsv denull --apply data.csv -o clean.csv
  $ qsv stats clean.csv --everything

Cleaning is per-column, which is what a single `qsv replace` pass cannot do: it
takes one regex across all selected columns, so it cannot blank "NULL" in one
column and "-" in another while leaving a literal "-" alone in a third.

Once blanked, `qsv stats` treats those cells as MISSING: it excludes them from mean,
stddev and the quartiles, and counts them in `nullcount` and `sparsity`. Do not reach
for the `--nulls` option of `qsv stats` to "restore" them. That option puts the blanks
back into the denominator while they contribute nothing to the sum, which is the same
as imputing zero. On a column that is 54% sentinel, that pulls the mean from 271 down
to 123 and SHRINKS the reported standard error - more confidence in a worse number.
A well with no recorded casing depth does not have a casing depth of zero.

Note also that `--nulls` reaches only the moment-based statistics - mean, stddev,
variance, cv, sem, geometric_mean, harmonic_mean and n_zero. The order statistics
(median, quartiles, iqr, mad, skewness) ALWAYS ignore blanks, whether or not the flag
is set, so a `--nulls` summary does not agree with itself: on that same column the mean
drops to 123 while the median stays at 200. And because one zero annihilates a product,
geometric_mean collapses to 0 and harmonic_mean to nothing at all.

So `--nulls` is not a general "treat blanks as zero" switch, even for data where an
empty cell genuinely MEANS zero (no events, no charge). If that is your data, and you
want every statistic to see those zeroes, materialize them first and leave the flag
alone:

  $ qsv fill --default 0 -s events data.csv | qsv stats --everything

Statistics over the cleaned column are still complete-case: they describe the rows
that HAVE a value. If a value is missing for a reason correlated with the value
itself, the estimate is biased. denull does not create that bias - before it ran, the
column was a String with no statistics at all - but it does not remove it either. It
makes the missingness visible so you can reason about it.

Numeric sentinels (-999, -9999, 9999) are deliberately NOT detected. They parse as
valid numbers, so no scan can distinguish them from real data - a depth-to-water
reading of -140 ft is an artesian well, not a missing value. Only a human or a
domain-aware model can propose those, and only a human should apply them.

The `sentinels` column lists the sentinel tokens OBSERVED in that column. They are
only safe to remove when the verdict is `confirmed`.

Examples:

  Report every column holding a null sentinel:
    $ qsv denull data.csv

  Restrict to a few columns, and emit JSON for a script to consume:
    $ qsv denull -s HoleDepth,WellDepth,CasingDepth --json data.csv

  Treat the site-specific "no reading" marker as a sentinel too:
    $ qsv denull --add-vocab "no reading,not recorded" data.csv

  Show every scanned column, including those with nothing to report:
    $ qsv denull --all-columns data.csv

  Blank the sentinels in every confirmed column; the report goes to stderr:
    $ qsv denull --apply data.csv -o clean.csv

For the tests, see https://github.com/dathere/qsv/blob/master/tests/test_denull.rs.

Usage:
    qsv denull [options] [<input>]
    qsv denull --help

denull options:
    -s, --select <arg>     Select the columns to scan. See `qsv select --help`
                           for the full selection syntax.
    --vocab <list>         Comma-separated null sentinel vocabulary, REPLACING
                           the built-in list. Matched case-insensitively after
                           trimming surrounding whitespace.
    --add-vocab <list>     Comma-separated tokens to ADD to the built-in list.
                           Use this for site-specific markers.
    --max-distinct <n>     Abandon a column once it holds this many distinct
                           non-numeric values. Guards memory on free-text
                           columns and bounds the report.
                           [default: 16]
    --all-columns          Also report columns with nothing to flag. By default
                           only columns with a verdict are listed.
    --apply                Rewrite the data instead of only reporting it. Blanks
                           the sentinels in every CONFIRMED column and writes the
                           CSV to <output> (or stdout), sending the report to
                           stderr. Rejected and unscanned columns pass through
                           untouched. Needs a file input, and <output> must not
                           be the input file.
    --json                 Emit the report as a JSON array instead of CSV.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write the report here instead of stdout.
    -n, --no-headers       When set, the first row will NOT be interpreted as
                           column names. Columns are named col_1, col_2, etc.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
