# qsv pragmastat

<small>v19.1.0</small>

```text
Pragmatic statistical toolkit.

Compute robust, median-of-pairwise statistics from the Pragmastat library.
Designed for messy, heavy-tailed, or outlier-prone data where mean/stddev can mislead.

This is a "smart" command that uses the stats cache to work smarter & faster.
When a stats cache is available, non-numeric columns are automatically filtered out
(unless --select is explicitly provided) and Date/DateTime columns are supported.

By default, one-sample mode appends 7 ps_* columns to the .stats.csv cache file
(like moarstats). Use --standalone for the old standalone CSV output. Two-sample,
compare1, and compare2 modes always produce standalone output.

Input handling
  * Only finite numeric values are used; non-numeric/NaN/Inf are ignored.
  * Date/DateTime columns are supported when a stats cache is available
    (run "qsv stats -E --infer-dates --stats-jsonl" first). Dates are converted to epoch
    milliseconds for analysis, then center/bounds are formatted as dates and spread/shift
    as days.
  * Each column is treated as its own sample (two-sample compares columns, not rows).
  * Non-numeric columns appear with n=0 and empty estimator cells.
  * NOTE: This command loads all numeric values into memory.

ONE-SAMPLE OUTPUT (default, per selected column)
  field, n, center, spread, center_lower, center_upper, spread_lower, spread_upper

  center             Robust location; median of pairwise averages (Hodges-Lehmann).
                     Like the mean but stable with outliers; tolerates up to 29% corrupted data.
  spread             Robust dispersion; median of pairwise absolute differences (Shamos).
                     Same units as data; also tolerates up to 29% corrupted data.
  center_lower/upper Bounds for center with error rate = misrate (exact under weak symmetry).
                     Use 1e-3 for everyday analysis or 1e-6 for critical decisions.
  spread_lower/upper Bounds for spread with error rate = misrate (randomized).

TWO-SAMPLE OUTPUT (--twosample, per unordered column pair)
  field_x, field_y, n_x, n_y, shift, ratio, disparity,
  shift_lower, shift_upper, ratio_lower, ratio_upper, disparity_lower, disparity_upper

  shift                 Robust difference in location; median of pairwise differences.
                        Negative => first column tends to be lower.
  ratio                 Robust multiplicative ratio; exp(shift(log x, log y)).
                        Use for positive-valued quantities (latency, price, concentration).
  disparity             Robust effect size = shift / (average spread of x and y).
  shift_lower/upper     Bounds for shift (exact; ties may be conservative).
                        If bounds exclude 0, the shift is reliable.
  ratio_lower/upper     Bounds for ratio (exact; requires all values > 0).
                        If bounds exclude 1, the ratio is reliable.
  disparity_lower/upper Bounds for disparity (randomized, Bonferroni combination).
                        If bounds exclude 0, the disparity is reliable.

When values are blank
  * Column has no numeric data (n=0).
  * Positivity required: ratio, ratio_* need all values > 0.
  * Sparity required: spread/spread_*/disparity/disparity_* need real variability (not tie-dominant).
  * Bounds require enough data for requested misrate; try higher misrate or more data.

MISRATE PARAMETER
  misrate is the probability that bounds miss the true value (lower => wider bounds).
    1e-3    Everyday analysis [default]
    1e-6    Critical decisions

COMPARE1 OUTPUT (--compare1, one-sample confirmatory analysis)
  field, n, metric, threshold, estimate, lower, upper, verdict

  Tests one-sample estimates (center/spread) against user-defined thresholds.
  Each threshold produces one row per column with a verdict:
    less          Estimate is statistically less than the threshold.
    greater       Estimate is statistically greater than the threshold.
    inconclusive  Not enough evidence to decide (interval contains threshold).

COMPARE2 OUTPUT (--compare2, two-sample confirmatory analysis)
  field_x, field_y, n_x, n_y, metric, threshold, estimate, lower, upper, verdict

  Tests two-sample estimates (shift/ratio/disparity) against user-defined thresholds.
  Each threshold produces one row per column pair with the same verdict semantics.

THRESHOLD FORMAT
  Both compare flags accept a comma-separated list of metric:value pairs.
    compare1 center:42.0             Single threshold
    compare1 center:42.0,spread:0.5  Multiple thresholds
    compare2 shift:0,disparity:0.8   Two-sample thresholds

  Valid metrics for compare1: center, spread
  Valid metrics for compare2: shift, ratio, disparity

Examples:
  # Append pragmastat columns to stats cache (default one-sample behavior)
  qsv pragmastat data.csv

  # Standalone one-sample output (old behavior)
  qsv pragmastat --standalone data.csv

  # One-sample statistics with selected columns
  qsv pragmastat --select latency_ms,price data.csv

  # Two-sample statistics with selected columns
  qsv pragmastat --twosample --select latency_ms,price data.csv

  # One-sample statistics with very tight bounds (lower misrate)
  qsv pragmastat --misrate 1e-6 data.csv

  # Compare one-sample center against a threshold
  qsv pragmastat --compare1 center:42.0 --select latitude data.csv

  # Compare one-sample center and spread against thresholds
  qsv pragmastat --compare1 center:42.0,spread:0.5 --select latitude data.csv

  # Compare two-sample shift and disparity against thresholds
  qsv pragmastat --compare2 shift:0,disparity:0.8 --select latency_ms,price data.csv

  # Fast exploratory analysis with subsampling (~100x speedup on large datasets)
  qsv pragmastat --standalone --subsample 10000 data.csv

  # Reproducible subsampling with a specific seed
  qsv pragmastat --standalone --subsample 10000 --seed 123 data.csv

  # Skip confidence bounds for ~2x speedup
  qsv pragmastat --standalone --no-bounds data.csv

  # Combined: ~200x speedup for large datasets
  qsv pragmastat --standalone --subsample 10000 --no-bounds data.csv

Full Pragmastat manual:
  https://github.com/AndreyAkinshin/pragmastat/releases/download/v12.0.0/pragmastat-v12.0.0.pdf
  https://pragmastat.dev/ (latest version)

Usage:
    qsv pragmastat [options] [<input>]
    qsv pragmastat --help

pragmastat options:
    -t, --twosample        Compute two-sample estimators for all column pairs.
        --compare1 <spec>  One-sample confirmatory analysis. Test center/spread against
                           thresholds. Format: metric:value[,metric:value,...].
                           Mutually exclusive with --twosample and --compare2.
        --compare2 <spec>  Two-sample confirmatory analysis. Test shift/ratio/disparity
                           against thresholds. Format: metric:value[,metric:value,...].
                           Mutually exclusive with --twosample and --compare1.
    -s, --select <cols>    Select columns for analysis. Uses qsv's column selection
                           syntax. Non-numeric columns appear with n=0.
                           In two-sample mode, all pairs of selected columns are computed.
    -m, --misrate <n>      Probability that bounds fail to contain the true parameter.
                           Lower values produce wider bounds.
                           Must be achievable for the given sample size.
                           [default: 0.001]
        --standalone       Output one-sample results as standalone CSV instead of
                           appending to the stats cache.
        --stats-options <arg>  Options to pass to the stats command if baseline stats need
                           to be generated. The options are passed as a single string
                           that will be split by whitespace.
                           [default: --infer-dates --infer-boolean --mad --quartiles --force --stats-jsonl]
        --round <n>        Round statistics to <n> decimal places. Rounding follows
                           Midpoint Nearest Even (Bankers Rounding) rule.
                           [default: 4]
        --force            Force recomputing ps_* columns even if they already exist
                           in the stats cache.
        --subsample <N>    Randomly subsample N values per column before computing.
                           Speeds up large datasets while maintaining statistical
                           robustness. Recommended: 10000-50000 for exploratory analysis.
        --seed <N>         Seed for reproducible subsampling.
                           If not specified, defaults to 42 when --subsample is used.
        --no-bounds        Skip confidence bounds computation (~2x faster).
                           Incompatible with --compare1/--compare2.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <c>    The field delimiter for reading/writing CSV data.
                           Must be a single character. (default: ,)
    -n, --no-headers       When set, the first row will not be treated as headers.
    -j, --jobs <arg>       The number of jobs to run in parallel.
                           When not set, the number of jobs is set to the
                           number of CPUs detected.
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics. Not valid for stdin.
```
