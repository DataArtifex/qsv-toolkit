# qsv pivotp

<small>v19.1.0</small>

```text
Pivots or groups CSV data using the Polars engine.

PIVOT MODE (with <on-cols>):
  The pivot operation consists of:
  - One or more index columns (these will be the new rows)
  - A column that will be pivoted (this will create the new columns)
  - A values column that will be aggregated
  - An aggregation function to apply. Features "smart" aggregation auto-selection.

GROUP-BY MODE (without <on-cols>):
  When <on-cols> is omitted, performs a group-by aggregation instead of a pivot.
  This is useful for simple aggregations like counting rows per group.
  In group-by mode, --index is required and --agg smart resolves to len (count).
  The none aggregation is not supported in group-by mode.
  If --values is omitted, a single "count" column is produced.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_pivotp.rs.

Usage:
    qsv pivotp [options] <on-cols> <input>
    qsv pivotp [options] <input>
    qsv pivotp --help

pivotp arguments:
    <on-cols>     The column(s) to pivot on (creates new columns).
                  When omitted, pivotp runs in group-by mode.
    <input>       The input CSV file. The file must have headers.
                  If the file has a pschema.json file, it will be used to
                  inform the pivot operation unless --infer-len is explicitly
                  set to a value other than the default of 10,000 rows.
                  Stdin is not supported.

pivotp options:
    -i, --index <cols>      The column(s) to use as the index (row labels).
                            Specify multiple columns by separating them with a comma.
                            The output will have one row for each unique combination of the index's values.
                            In pivot mode, if None, all remaining columns not specified on --on and --values
                            will be used; at least one of --index and --values must be specified.
                            Required in group-by mode.
    -v, --values <cols>     The column(s) containing values to aggregate.
                            If an aggregation is specified, these are the values on which the aggregation
                            will be computed.
                            In pivot mode, if None, all remaining columns not specified on --on and --index
                            will be used; at least one of --index and --values must be specified.
                            In group-by mode, if omitted, a single "count" column is produced.
    -a, --agg <func>        The aggregation function to use:
                              first - First value encountered
                              last - Last value encountered
                              sum - Sum of values
                              min - Minimum value
                              max - Maximum value
                              mean - Average value
                              median - Median value
                              len - Count of values
                              item - Get single value from group. Raises error if there are multiple values.
                              smart - use value column data type & statistics to pick an aggregation.
                                      Always uses type, cardinality, sparsity, CV, sign
                                      distribution (n_negative/n_positive), and sort_order
                                      from streaming stats.
                                      When the stats cache includes non-streaming stats (from a
                                      prior `stats --everything` or `stats --mode --quartiles`),
                                      also uses skewness and mode_count.
                                      When moarstats has been run, also leverages outlier profile,
                                      Pearson skewness, MAD/stddev ratio, median/mean ratio, and
                                      quartile coefficient of dispersion for smarter selection.
                                      With moarstats --advanced, also uses kurtosis, bimodality,
                                      entropy and Gini coefficient.
                                      For Date/DateTime values, checks sparsity and sort order.
                                      Will only work if there is one value column, otherwise
                                      it falls back to `first`
                            [default: smart]
    --sort-columns          Sort the transposed columns by name. (pivot mode only)
    --maintain-order        Maintain output order: preserve input column order in pivot mode,
                            and preserve group/row order in group-by mode.
    --col-separator <arg>   The separator in generated column names in case of multiple --values columns.
                            (pivot mode only; ignored in group-by mode) [default: _]
    --validate              Validate a pivot by checking the pivot column(s)' cardinality. (pivot mode only)
    --try-parsedates        When set, will attempt to parse columns as dates.
    --infer-len <arg>       Number of rows to scan when inferring schema.
                            Set to 0 to scan entire file. [default: 10000]
    --decimal-comma         Use comma as decimal separator when READING the input.
                            Note that you will need to specify an alternate --delimiter.
    --ignore-errors         Skip rows that can't be parsed.
    --grand-total           Append a grand total row summing all numeric non-index columns.
                            The first index column will contain "Grand <total-label>".
    --subtotal              Insert subtotal rows after each group in the first index column.
                            The second index column will contain the total label.
                            Requires 2+ index columns. (pivot mode only)
    --total-label <arg>     Custom label for total rows. [default: Total]

Common options:
    -h, --help              Display this message
    -o, --output <file>     Write output to <file> instead of stdout.
    -d, --delimiter <arg>   The field delimiter for reading/writing CSV data.
                            Must be a single character. (default: ,)
    -q, --quiet             Do not return smart aggregation chosen nor pivot result shape to stderr.
```
