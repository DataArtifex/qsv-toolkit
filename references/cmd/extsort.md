# qsv extsort

<small>v28.0.0</small>

```text
Sort an arbitrarily large CSV/text file using a multithreaded external sort algorithm.

This command has TWO modes of operation.

 * CSV MODE
   when --select is set, it sorts based on the given column/s. Requires an index.
   See `qsv select --help` for select syntax details.

   STATS-CACHE AWARE: in CSV MODE, when a single ASCII column is selected and a valid
   stats cache exists (see `qsv stats --stats-jsonl`), extsort uses the cached sort order
   to detect if the column is already in ascending order and, if so, streams the input
   through unchanged, skipping the external sort entirely. Not applied with --reverse or
   multi-column selections. Disable with QSV_STATSCACHE_MODE=none.
 * LINE MODE
   when --select is NOT set, it sorts any input text file (not just CSVs) on a
   line-by-line basis. If sorting a non-CSV file, be sure to set --no-headers,
   otherwise, the first line will not be included in the external sort.

See also https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#extsort

Usage:
    qsv extsort [options] [<input>] [<output>]
    qsv extsort --help

External sort option:
    -s, --select <arg>     Select a subset of columns to sort (CSV MODE).
                           Note that the outputs will remain at the full width of the CSV.
                           If --select is NOT set, extsort will work in LINE MODE, sorting
                           the input as a text file on a line-by-line basis.
    -R, --reverse          Reverse order
    --memory-limit <arg>   The memory budget for sorting each in-memory chunk. Input that
                           exceeds it is sorted in chunks spilled to the tmp-dir, then merged.
                           The budget is approximate - peak memory use is higher, as it
                           does not count sort scratch space, allocator overhead, or the
                           merge phase's read buffer (~1 MB per chunk).
                           If less than 50, this is a percentage of total memory.
                           If more than 50, this is the memory in MB to allocate, capped
                           at 90 percent of total memory.
                           [default: 20]
    --tmp-dir <arg>        The directory to use for externally sorting file segments.
                           [default: ./]
    -j, --jobs <arg>       The number of jobs to run in parallel.
                           When not set, the number of jobs is set to the
                           number of CPUs detected.

Common options:
                           CSV MODE ONLY:
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)

    -h, --help             Display this message
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers and will be sorted with the rest
                           of the rows. Otherwise, the first row will always
                           appear as the header row in the output.
```
