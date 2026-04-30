# qsv dedup

<small>19.1.0</small>
```text
Deduplicates CSV rows.

This requires reading all of the CSV data into memory because because the rows need
to be sorted first.

That is, unless the --sorted option is used to indicate the CSV is already sorted -
typically, with the sort cmd for more sorting options or the extsort cmd for larger
than memory CSV files. This will make dedup run in streaming mode with constant memory.

Either way, the output will not only be deduplicated, it will also be sorted.

A duplicate count will also be sent to <stderr>.

Examples:

  # Deduplicate an unsorted CSV file:
  qsv dedup unsorted.csv -o deduped.csv

  # Deduplicate a sorted CSV file:
  qsv sort unsorted.csv | qsv dedup --sorted -o deduped.csv

  # Deduplicate based on specific columns:
  qsv dedup --select col1,col2 unsorted.csv -o deduped.csv

  # Deduplicate based on numeric comparison of col1 and col2 columns:
  qsv dedup -s col1,col2 --numeric unsorted.csv -o deduped.csv

  # Deduplicate ignoring case of col1 and col2 columns:
  qsv dedup -s col1,col2 --ignore-case unsorted.csv -o deduped.csv

  # Write duplicates to a separate file:
  qsv dedup -s col1,col2 --dupes-output dupes.csv unsorted.csv -o deduped.csv

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_dedup.rs.

Usage:
    qsv dedup [options] [<input>]
    qsv dedup --help

dedup options:
    -s, --select <arg>         Select a subset of columns to dedup.
                               Note that the outputs will remain at the full width
                               of the CSV.
                               See 'qsv select --help' for the format details.
    -N, --numeric              Compare according to string numerical value
    -i, --ignore-case          Compare strings disregarding case.
    --sorted                   The input is already sorted. Do not load the CSV into
                               memory to sort it first. Meant to be used in tandem and
                               after an extsort.
    -D, --dupes-output <file>  Write duplicates to <file>.
    -H, --human-readable       Comma separate duplicate count.
    -j, --jobs <arg>           The number of jobs to run in parallel when sorting
                               an unsorted CSV, before deduping.
                               When not set, the number of jobs is set to the
                               number of CPUs detected.
                               Does not work with --sorted option as its not
                               multithreaded.

Common options:
    -h, --help                 Display this message
    -o, --output <file>        Write output to <file> instead of stdout.
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. That is, it will be sorted with the rest
                               of the rows. Otherwise, the first row will always
                               appear as the header row in the output.
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character. (default: ,)
    -q, --quiet                Do not print duplicate count to stderr.
    --memcheck                 Check if there is enough memory to load the entire
                               CSV into memory using CONSERVATIVE heuristics.
                               Has no effect when --sorted is set, as that path
                               streams the input and never loads it into memory.
```
