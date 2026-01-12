# qsv stats

```text
Compute summary statistics & infers data types for each column in a CSV.

> IMPORTANT: `stats` is heavily optimized for speed. It ASSUMES the CSV is well-formed & UTF-8 encoded.
> This allows it to employ numerous performance optimizations (skip repetitive UTF-8 validation, skip
> bounds checks, cache results, etc.) that may result in undefined behavior if the CSV is not well-formed.
> All these optimizations are GUARANTEED to work with well-formed CSVs.
> If you encounter problems generating stats, use `qsv validate` FIRST to confirm the CSV is valid.

> For MAXIMUM PERFORMANCE, create an index for the CSV first with 'qsv index' to enable multithreading,
> or set --cache-threshold option or set the QSV_AUTOINDEX_SIZE environment variable to automatically
> create an index when the file size is greater than the specified size (in bytes).

Summary stats include sum, min/max/range, sort order/sortiness, min/max/sum/avg/stddev/variance/cv length,
mean, standard error of the mean (SEM), geometric mean, harmonic mean, stddev, variance, coefficient of
variation (CV), nullcount, n_negative, n_zero, n_positive, max_precision, sparsity,
Median Absolute Deviation (MAD), quartiles, lower/upper inner/outer fences, skewness, median,
cardinality/uniqueness ratio, mode/s & "antimode/s" & percentiles.

Note that some stats require loading the entire file into memory, so they must be enabled explicitly.

By default, the following "streaming" statistics are reported for *every* column:
  sum, min/max/range values, sort order/"sortiness", min/max/sum/avg/stddev/variance/cv length, mean, sem,
  geometric_mean, harmonic_mean,stddev, variance, cv, nullcount, n_negative, n_zero, n_positive,
  max_precision & sparsity.

The default set of statistics corresponds to ones that can be computed efficiently on a stream of data
(i.e., constant memory) and works with arbitrarily large CSVs.

The following additional "non-streaming, advanced" statistics require loading the entire file into memory:
cardinality/uniqueness ratio, modes/antimodes, median, MAD, quartiles and its related measures
(q1, q2, q3, IQR, lower/upper fences & skewness) and percentiles.

When computing "non-streaming" statistics, a memory-aware chunking algorithm is used to dynamically
calculate chunk size based on available memory & record sampling. This SHOULD help process arbitrarily
large "real-world" files by creating smaller chunks that fit in available memory.
However, there is still a chance that the command will run out of memory if the cardinality of
several columns is very high.

Chunk size is dynamically calculated based on the number of logical CPUs detected.
You can override this behavior by setting the QSV_STATS_CHUNK_MEMORY_MB environment variable
(set to 0 for dynamic sizing, or a positive number for a fixed memory limit per chunk,
or -1 for CPU-based chunking (1 chunk = records/number of CPUs)).

"Antimode" is the least frequently occurring non-zero value and is the opposite of mode.
It returns "*ALL" if all the values are unique, and only returns a preview of the first
10 antimodes, truncating after 100 characters (configurable with QSV_ANTIMODES_LEN).

If you need all the antimode values of a column, run the `frequency` command with --limit set
to zero. The resulting frequency table will have all the "antimode" values.

Summary statistics for dates are also computed when --infer-dates is enabled, with DateTime
results in rfc3339 format and Date results in "yyyy-mm-dd" format in the UTC timezone.
Date range, stddev, variance, MAD & IQR are returned in days, not timestamp milliseconds.

Each column's data type is also inferred (NULL, Integer, String, Float, Date, DateTime and
Boolean with --infer-boolean option).
For String data types, it also determines if the column is all ASCII characters.
Unlike the sniff command, stats' data type inferences are GUARANTEED, as the entire file
is scanned, and not just sampled.

Note that the Date and DateTime data types are only inferred with the --infer-dates option
as its an expensive operation to match a date candidate against 19 possible date formats,
with each format, having several variants.

The date formats recognized and its sub-variants along with examples can be found at
https://github.com/dathere/qsv-dateparser?tab=readme-ov-file#accepted-date-formats.

Computing statistics on a large file can be made MUCH faster if you create an index for it
first with 'qsv index' to enable multithreading. With an index, the file is split into chunks
and each chunk is processed in parallel.

As stats is a central command in qsv, and can be expensive to compute, `stats` caches results
in <FILESTEM>.stats.csv & if the --stats-json option is used, <FILESTEM>.stats.csv.data.jsonl
(e.g., qsv stats nyc311.csv will create nyc311.stats.csv & nyc311.stats.csv.data.jsonl).
The arguments used to generate the cached stats are saved in <FILESTEM>.stats.csv.jsonl.

If stats have already been computed for the input file with similar arguments and the file
hasn't changed, the stats will be loaded from the cache instead of recomputing it.

These cached stats are also used by other qsv commands (currently `describegpt`, `frequency`,
`joinp`, `pivotp`, `schema`, `sqlp` & `tojsonl`) to work smarter & faster.
If the cached stats are not current (i.e., the input file is newer than the cached stats),
the cached stats will be ignored and recomputed. For example, see the "boston311" test files in
https://github.com/dathere/qsv/blob/4529d51273218347fef6aca15ac24e22b85b2ec4/tests/test_stats.rs#L608.

Examples:

Compute "streaming" statistics for the "nyc311.csv" file:
  $ qsv stats nyc311.csv

Compute all statistics for the "nyc311.csv" file:
  $ qsv stats --everything nyc311.csv
  $ qsv stats -E nyc311.csv
  $ qsv stats -E nyc311.tsv // Tab-separated
  $ qsv stats -E nyc311.tab // Tab-separated
  $ qsv stats -E nyc311.ssv // Semicolon-separated
  $ qsv stats -E nyc311.csv.sz // Snappy-compressed CSV
  $ qsv stats -E nyc311.tsv.sz // Snappy-compressed Tab-separated
  $ qsv stats -E nyc311.ssv.sz // Snappy-compressed Semicolon-separated

Compute all statistics for "nyc311.tsv", inferring dates using default date column name patterns:
  $ qsv stats -E --infer-dates nyc311.tsv

Compute all statistics for "nyc311.tab", inferring dates only for columns with "_date" & "_dte"
in the column names:
  $ qsv stats -E --infer-dates --dates-whitelist _date,_dte nyc311.tab

In addition, also infer boolean data types for "nyc311.ssv" file:
  $ qsv stats -E --infer-dates --dates-whitelist _date --infer-boolean nyc311.ssv

In addition to basic "streaming" stats, also compute cardinality for the "nyc311.csv" file:
  $ qsv stats --cardinality nyc311.csv

Prefer DMY format when inferring dates for the "nyc311.csv" file:
  $ qsv stats -E --infer-dates --prefer-dmy nyc311.csv

Infer data types only for the "nyc311.csv" file:
  $ qsv stats --typesonly nyc311.csv

Infer data types only, including boolean and date types for the "nyc311.csv" file:
  $ qsv stats --typesonly --infer-boolean --infer-dates nyc311.csv

If the polars feature is enabled, support additional tabular file formats and
compression formats:
  $ qsv stats data.parquet // Parquet
  $ qsv stats data.avro // Avro
  $ qsv stats data.jsonl // JSON Lines
  $ qsv stats data.json (will only work with a JSON Array)
  $ qsv stats data.csv.gz // Gzipped CSV
  $ qsv stats data.tab.zlib // Zlib-compressed Tab-separated
  $ qsv stats data.ssv.zst // Zstd-compressed Semicolon-separated

Automatically create an index for the "nyc311.csv" file to enable multithreading
if it's larger than 5MB and there is no existing index file:
  $ qsv stats -E --cache-threshold -5000000 nyc311.csv

Auto-create a TEMPORARY index for the "nyc311.csv" file to enable multithreading
if it's larger than 5MB and delete the index and the stats cache file after the stats run:
  $ qsv stats -E --cache-threshold -5000005 nyc311.csv

Prompt for CSV/TSV/TAB file to compute stats for:
  $ qsv prompt -F tsv,csv,tab | qsv stats -E | qsv table

Prompt for a file to save the stats to in the ~/Documents directory:
  $ qsv stats -E nyc311.csv | qsv prompt -d ~/Documents --fd-output

Prompt for both INPUT and OUTPUT files in the ~/Documents dir with custom prompts:
  $ qsv prompt -m 'Select a CSV file to summarize' -d ~/Documents -F csv | \
      qsv stats -E --infer-dates | \
      qsv prompt -m 'Save summary to...' -d ~/Documents --fd-output --save-fname summarystats.csv

For more examples, see https://github.com/dathere/qsv/tree/master/resources/test
For more info, see https://github.com/dathere/qsv/wiki/Supplemental#stats-command-output-explanation

Usage:
    qsv stats [options] [<input>]
    qsv stats --help

stats options:
    -s, --select <arg>        Select a subset of columns to compute stats for.
                              See 'qsv select --help' for the format details.
                              This is provided here because piping 'qsv select'
                              into 'qsv stats' will prevent the use of indexing.
    -E, --everything          Compute all statistics available EXCEPT --dataset-stats.
    --typesonly               Infer data types only and do not compute statistics.
                              Note that if you want to infer dates and boolean types, you'll
                              still need to use the --infer-dates & --infer-boolean options.

                              BOOLEAN INFERENCING:
    --infer-boolean           Infer boolean data type. This automatically enables
                              the --cardinality option. When a column's cardinality is 2,
                              and the 2 values' are in the true/false patterns specified
                              by --boolean-patterns, the data type is inferred as boolean.
    --boolean-patterns <arg>  Comma-separated list of boolean pattern pairs in the format
                              "true_pattern:false_pattern". Each pattern can be a string
                              of any length. The patterns are case-insensitive. If a pattern
                              ends with a "*", it is treated as a prefix. For example,
                              "t*:f*,y*:n*" will match "true", "truthy", "Truth" as boolean true
                              values so long as the corresponding false pattern (e.g. False, f, etc.)
                              is also matched & cardinality is 2. Ignored if --infer-boolean is false.
                              [default: 1:0,t*:f*,y*:n*]

    --mode                    Compute the mode/s & antimode/s. Multimodal-aware.
                              If there are multiple modes/antimodes, they are separated by the
                              QSV_STATS_SEPARATOR environment variable. If not set, the default
                              separator is "|".
                              Uses memory proportional to the cardinality of each column.
    --cardinality             Compute the cardinality and the uniqueness ratio.
                              This is automatically enabled if --infer-boolean is enabled.
                              https://en.wikipedia.org/wiki/Cardinality_(SQL_statements)
                              Uses memory proportional to the number of unique values in each column.

                              NUMERIC & DATE/DATETIME STATS THAT REQUIRE IN-MEMORY SORTING:
                              The following statistics are only computed for numeric & date/datetime
                              columns & require loading & sorting ALL the selected columns' data
                              in memory FIRST before computing the statistics.

    --median                  Compute the median.
                              Loads & sorts all the selected columns' data in memory.
                              https://en.wikipedia.org/wiki/Median
    --mad                     Compute the median absolute deviation (MAD).
                              https://en.wikipedia.org/wiki/Median_absolute_deviation
    --quartiles               Compute the quartiles (using method 3), the IQR, the lower/upper,
                              inner/outer fences and skewness.
                              https://en.wikipedia.org/wiki/Quartile#Method_3
    --percentiles             Compute custom percentiles using the nearest rank method.
                              https://en.wikipedia.org/wiki/Percentile#The_nearest-rank_method
    --percentile-list <arg>   Comma-separated list of percentiles to compute.
                              For example, "5,10,40,60,90,95" will compute percentiles
                              5th, 10th, 40th, 60th, 90th, and 95th.
                              Multiple percentiles are separated by the QSV_STATS_SEPARATOR
                              environment variable. If not set, the default separator is "|".
                              It is ignored if --percentiles is not set.
                              Special values "deciles" and "quintiles" are automatically expanded
                              to "10,20,30,40,50,60,70,80,90" and "20,40,60,80" respectively.
                              [default: 5,10,40,60,90,95]

    --round <decimal_places>  Round statistics to <decimal_places>. Rounding is done following
                              Midpoint Nearest Even (aka "Bankers Rounding") rule.
                              https://docs.rs/rust_decimal/latest/rust_decimal/enum.RoundingStrategy.html
                              If set to the sentinel value 9999, no rounding is done.
                              For dates - range, stddev & IQR are always at least 5 decimal places as
                              they are reported in days, and 5 places gives us millisecond precision.
                              [default: 4]
    --nulls                   Include NULLs in the population size for computing
                              mean and standard deviation.
    --weight <column>         Compute weighted statistics using the specified column as weights.
                              The weight column must be numeric. When specified, all statistics
                              (mean, stddev, variance, median, quartiles, mode, etc.) will be
                              computed using weighted algorithms. The weight column is automatically
                              excluded from statistics computation. Missing or non-numeric weights
                              default to 1.0. Zero and negative weights are ignored and do not
                              contribute to the statistics. The output filename will be
                              <FILESTEM>.stats.weighted.csv to distinguish from unweighted statistics.

                              DATE INFERENCING:
    --infer-dates             Infer date/datetime data types. This is an expensive
                              option and should only be used when you know there
                              are date/datetime fields.
                              Also, if timezone is not specified in the data, it'll
                              be set to UTC.
    --dates-whitelist <list>  The comma-separated, case-insensitive patterns to look for when
                              shortlisting fields for date inferencing.
                              i.e. if the field's name has any of these patterns,
                              it is shortlisted for date inferencing.
                              Set to "all" to inspect ALL fields for
                              date/datetime types. Ignored if --infer-dates is false.

                              Note that false positive date matches WILL most likely occur
                              when using "all" as unix epoch timestamps are just numbers.
                              Be sure to only use "all" if you know ALL the columns you're
                              inspecting are dates, boolean or string fields.

                              To avoid false positives, preprocess the file first
                              with the `datefmt` command to convert unix epoch timestamp
                              columns to RFC3339 format.
                              [default: date,time,due,open,close,created]
    --prefer-dmy              Parse dates in dmy format. Otherwise, use mdy format.
                              Ignored if --infer-dates is false.

    --force                   Force recomputing stats even if valid precomputed stats
                              cache exists.
    -j, --jobs <arg>          The number of jobs to run in parallel.
                              This works only when the given CSV has an index.
                              Note that a file handle is opened for each job.
                              When not set, the number of jobs is set to the
                              number of CPUs detected.
    --stats-jsonl             Also write the stats in JSONL format.
                              If set, the stats will be written to <FILESTEM>.stats.csv.data.jsonl.
                              Note that this option used internally by other qsv "smart" commands (see
                              https://github.com/dathere/qsv/blob/master/docs/PERFORMANCE.md#stats-cache)
                              to load cached stats to make them work smarter & faster.
                              You can preemptively create the stats-jsonl file by using this option
                              BEFORE running "smart" commands and they will automatically use it.
 -c, --cache-threshold <arg>  Controls the creation of stats cache files.
                                - when greater than 1, the threshold in milliseconds before caching
                                  stats results. If a stats run takes longer than this threshold,
                                  the stats results will be cached.
                                - 0 to suppress caching.
                                - 1 to force caching.
                                - a negative number to automatically create an index when
                                  the input file size is greater than abs(arg) in bytes.
                                  If the negative number ends with 5, it will delete the index
                                  file and the stats cache file after the stats run. Otherwise,
                                  the index file and the cache files are kept.
                              [default: 5000]
    --vis-whitespace          Visualize whitespace characters in the output.
                              See https://github.com/dathere/qsv/wiki/Supplemental#whitespace-markers
                              for the list of whitespace markers.
    --dataset-stats           Compute dataset statistics (e.g. row count, column count, file size and
                              fingerprint hash) and add them as additional rows to the output, with
                              the qsv__ prefix and an additional qsv__value column.
                              The --everything option DOES NOT enable this option.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will NOT be interpreted
                           as column names. i.e., They will be included
                           in statistics.
    -d, --delimiter <arg>  The field delimiter for READING CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
                           This option is ignored when computing default, streaming
                           statistics, as it is not needed.
```
