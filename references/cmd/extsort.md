# qsv extsort

```text
Sort an arbitrarily large CSV/text file using a multithreaded external sort algorithm.

This command has TWO modes of operation.

 * CSV MODE
   when --select is set, it sorts based on the given column/s. Requires an index.
   See `qsv select --help` for select syntax details.
 * LINE MODE
   when --select is NOT set, it sorts any input text file (not just CSVs) on a
   line-by-line basis. If sorting a non-CSV file, be sure to set --no-headers, 
   otherwise, the first line will not be included in the external sort.

Usage:
    qsv extsort [options] [<input>] [<output>]
    qsv extsort --help

External sort option:
    -s, --select <arg>     Select a subset of columns to sort (CSV MODE).
                           Note that the outputs will remain at the full width of the CSV.
                           If --select is NOT set, extsort will work in LINE MODE, sorting
                           the input as a text file on a line-by-line basis.
    -R, --reverse          Reverse order
    --memory-limit <arg>   The maximum amount of memory to buffer the external merge sort.
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
