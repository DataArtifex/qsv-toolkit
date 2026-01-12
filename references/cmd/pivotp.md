# qsv pivotp

```text
Pivots CSV data using the Polars engine.

The pivot operation consists of:
- One or more index columns (these will be the new rows)
- A column that will be pivoted (this will create the new columns)
- A values column that will be aggregated
- An aggregation function to apply. Features "smart" aggregation auto-selection.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_pivotp.rs.

Usage:
    qsv pivotp [options] <on-cols> <input>
    qsv pivotp --help

pivotp arguments:
    <on-cols>     The column(s) to pivot on (creates new columns).
    <input>       is the input CSV file. The file must have headers.
                  If the file has a pschema.json file, it will be used to
                  inform the pivot operation unless --infer-len is explicitly
                  set to a value other than the default of 10,000 rows.
                  Stdin is not supported.

pivotp options:
    -i, --index <cols>      The column(s) to use as the index (row labels).
                            Specify multiple columns by separating them with a comma.
                            The output will have one row for each unique combination of the index's values.
                            If None, all remaining columns not specified on --on and --values will be used.
                            At least one of --index and --values must be specified.
    -v, --values <cols>     The column(s) containing values to aggregate.
                            If an aggregation is specified, these are the values on which the aggregation
                            will be computed. If None, all remaining columns not specified on --on and --index
                            will be used. At least one of --index and --values must be specified.
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
                                      Will only work if there is one value column, otherwise
                                      it falls back to `first`
                            [default: smart]
    --sort-columns          Sort the transposed columns by name.
    --maintain-order        Maintain the order of the input columns.
    --col-separator <arg>   The separator in generated column names in case of multiple --values columns.
                            [default: _]
    --validate              Validate a pivot by checking the pivot column(s)' cardinality.
    --try-parsedates        When set, will attempt to parse columns as dates.
    --infer-len <arg>       Number of rows to scan when inferring schema.
                            Set to 0 to scan entire file. [default: 10000]
    --decimal-comma         Use comma as decimal separator when READING the input.
                            Note that you will need to specify an alternate --delimiter.
    --ignore-errors         Skip rows that can't be parsed.

Common options:
    -h, --help              Display this message
    -o, --output <file>     Write output to <file> instead of stdout.
    -d, --delimiter <arg>   The field delimiter for reading/writing CSV data.
                            Must be a single character. (default: ,)
    -q, --quiet             Do not return smart aggregation chosen nor pivot result shape to stderr.
```
