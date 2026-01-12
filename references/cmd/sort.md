# qsv sort

```text
Sorts CSV data in lexicographical, natural, numerical, reverse, unique or random order.

Note that this requires reading all of the CSV data into memory. If
you need to sort a large file that may not fit into memory, use the
extsort command instead.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_sort.rs.

Usage:
    qsv sort [options] [<input>]
    qsv sort --help

sort options:
    -s, --select <arg>      Select a subset of columns to sort.
                            See 'qsv select --help' for the format details.
    -N, --numeric           Compare according to string numerical value
    --natural               Compare strings using natural sort order
                            (treats numbers within strings as actual numbers, e.g.
                            "data1.txt", "data2.txt", "data10.txt", as opposed to
                            "data1.txt", "data10.txt", "data2.txt" when sorting
                            lexicographically)
                            https://en.wikipedia.org/wiki/Natural_sort_order
    -R, --reverse           Reverse order
    -i, --ignore-case       Compare strings disregarding case
    -u, --unique            When set, identical consecutive lines will be dropped
                            to keep only one line per sorted value.

                            RANDOM SORTING OPTIONS:
    --random                Randomize (scramble) the data by row
    --seed <number>         Random Number Generator (RNG) seed to use if --random is set
    --rng <kind>            The RNG algorithm to use if --random is set.
                            Three RNGs are supported:
                            - standard: Use the standard RNG.
                              1.5 GB/s throughput.
                            - faster: Use faster RNG using the Xoshiro256Plus algorithm.
                              8 GB/s throughput.
                            - cryptosecure: Use cryptographically secure HC128 algorithm.
                              Recommended by eSTREAM (https://www.ecrypt.eu.org/stream/).
                              2.1 GB/s throughput though slow initialization.
                            [default: standard]
    

    -j, --jobs <arg>        The number of jobs to run in parallel.
                            When not set, the number of jobs is set to the
                            number of CPUs detected.
    --faster                When set, the sort will be faster. This is done by
                            using a faster sorting algorithm that is not "stable"
                            (i.e. the order of identical values is not guaranteed
                            to be preserved). It has the added side benefit that the
                            sort will also be in-place (i.e. does not allocate),
                            which is useful for sorting large files that will 
                            otherwise NOT fit in memory using the default allocating
                            stable sort.

Common options:
    -h, --help              Display this message
    -o, --output <file>     Write output to <file> instead of stdout.
    -n, --no-headers        When set, the first row will not be interpreted
                            as headers. Namely, it will be sorted with the rest
                            of the rows. Otherwise, the first row will always
                            appear as the header row in the output.
    -d, --delimiter <arg>   The field delimiter for reading CSV data.
                            Must be a single character. (default: ,)
    --memcheck              Check if there is enough memory to load the entire
                            CSV into memory using CONSERVATIVE heuristics.
                            Ignored if --random or --faster is set.
```
