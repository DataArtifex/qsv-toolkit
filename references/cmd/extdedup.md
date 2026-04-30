# qsv extdedup

<small>19.1.0</small>
```text
Remove duplicate rows from an arbitrarily large CSV/text file using a memory-mapped,
on-disk hash table.

Unlike the 'dedup' command, this command does not load the entire file into memory
to sort the CSV first before deduping it.

This allows it to run in constant memory and the output will retain the input sort order.

This command has TWO modes of operation.

 * CSV MODE
   when --select is set, it dedupes based on the given column/s. See `qsv select --help`
   for select syntax details.
 * LINE MODE
   when --select is NOT set, it deduplicates any input text file (not just CSVs) on a
   line-by-line basis.

A duplicate count will be sent to <stderr>.

Usage:
    qsv extdedup [options] [<input>] [<output>]
    qsv extdedup --help

extdedup options:
    -s, --select <arg>         Select a subset of columns to dedup.
                               Note that the outputs will remain at the full width of the CSV.
                               If --select is NOT set, extdedup will work in LINE MODE, deduping
                               the input as a text file on a line-by-line basis.
    --no-output                Do not write deduplicated output to <output>.
                               Use this if you only want to know the duplicate count.
                               Applies to both CSV MODE and LINE MODE.
    -D, --dupes-output <file>  Write duplicates to <file>.
                               In CSV MODE, <file> is a valid CSV with the same columns as the
                               input plus a leading "dupe_rowno" column (1-based data row number).
                               In LINE MODE, <file> is NOT a valid CSV — each duplicate line is
                               prefixed by its 0-based file line index and a tab character.
    -H, --human-readable       Comma separate duplicate count.
    --memory-limit <arg>       The maximum amount of memory to buffer the on-disk hash table.
                               If less than 50, this is a percentage of total memory.
                               If more than 50, this is the memory in MB to allocate, capped
                               at 90 percent of total memory.
                               [default: 10]
    --temp-dir <arg>           Directory to store temporary hash table file.
                               If not specified, defaults to operating system temp directory.

Common options:
                               CSV MODE ONLY:
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. That is, it will be deduped with the rest
                               of the rows. Otherwise, the first row will always
                               appear as the header row in the output.
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character. (default: ,)

    -h, --help                 Display this message
    -q, --quiet                Do not print duplicate count to stderr.
```
