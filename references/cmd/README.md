# QSV Commands Reference

This directory contains documentation for each `qsv` command, specifically the output of their help options.

## Available Commands

| Command | Description |
|---------|-------------|
| [apply](apply.md) | Apply a series of transformation functions to given CSV column/s. This can be used to |
| [behead](behead.md) | Drop a CSV file's header. |
| [cat](cat.md) | Concatenate CSV files by row or by column. |
| [clipboard](clipboard.md) | Provide input from the clipboard or save output to the clipboard. |
| [count](count.md) | Returns a count of the number of records in the CSV data. |
| [datefmt](datefmt.md) | Formats recognized date fields (19 formats recognized) to a specified date format |
| [dedup](dedup.md) | Deduplicates CSV rows. |
| [describegpt](describegpt.md) | Create a "neuro-procedural" Data Dictionary and/or infer Description & Tags about a Dataset |
| [diff](diff.md) | Find the difference between two CSVs with ludicrous speed. |
| [edit](edit.md) | Replace the value of a cell specified by its row and column. |
| [enum](enum.md) | Add a new column enumerating the lines of a CSV file. This can be useful to keep |
| [excel](excel.md) | Exports a specified Excel/ODS sheet to a CSV file. |
| [exclude](exclude.md) | Removes a set of CSV data from another set based on the specified columns. |
| [explode](explode.md) | Explodes a row into multiple ones by splitting a column value based on the |
| [extdedup](extdedup.md) | Remove duplicate rows from an arbitrarily large CSV/text file using a memory-mapped, |
| [extsort](extsort.md) | Sort an arbitrarily large CSV/text file using a multithreaded external sort algorithm. |
| [fetch](fetch.md) | Send/Fetch data to/from web services for every row using HTTP Get. |
| [fetchpost](fetchpost.md) | Fetchpost sends/fetches data to/from web services for every row using HTTP Post. |
| [fill](fill.md) | Fill empty fields in selected columns of a CSV. |
| [fixlengths](fixlengths.md) | Transforms CSV data so that all records have the same length. The length is |
| [flatten](flatten.md) | Prints flattened records such that fields are labeled separated by a new line. |
| [fmt](fmt.md) | Formats CSV data with a custom delimiter or CRLF line endings. |
| [foreach](foreach.md) | Execute a shell command once per record in a given CSV file. |
| [frequency](frequency.md) | Compute a frequency distribution table on input data. It has CSV and JSON output modes. |
| [geocode](geocode.md) | Geocodes a location in CSV data against an updatable local copy of the Geonames cities index |
| [geoconvert](geoconvert.md) | Convert between various spatial formats and CSV/SVG including GeoJSON, SHP, and more. |
| [headers](headers.md) | Prints the fields of the first row in the CSV data. |
| [index](index.md) | Creates an index of the given CSV data, which can make other operations like |
| [input](input.md) | Read CSV data with special commenting, quoting, trimming, line-skipping & |
| [join](join.md) | Joins two sets of CSV data on the specified columns. |
| [joinp](joinp.md) | Joins two sets of CSV data on the specified columns using the Polars engine. |
| [json](json.md) | Convert JSON to CSV. |
| [jsonl](jsonl.md) | Convert newline-delimited JSON (JSONL/NDJSON) to CSV. |
| [lens](lens.md) | Explore tabular data files interactively using the csvlens (https://github.com/YS-L/csvlens) engine. |
| [luau](luau.md) | Create multiple new computed columns, filter rows or compute aggregations by |
| [moarstats](moarstats.md) | Add dozens of additional statistics, including extended outlier & robust statistics |
| [partition](partition.md) | Partitions the given CSV data into chunks based on the value of a column. |
| [pivotp](pivotp.md) | Pivots CSV data using the Polars engine. |
| [pro](pro.md) | Interact with qsv pro API. Learn more about qsv pro at: https://qsvpro.dathere.com. |
| [prompt](prompt.md) | Open a file dialog to pick a file as input or save to an output file. |
| [pseudo](pseudo.md) | Pseudonymise the value of a given column by replacing it with an |
| [py](py.md) | Create a new computed column or filter rows by evaluating a Python expression on |
| [rename](rename.md) | Rename the columns of a CSV efficiently. It has two modes of operation: |
| [replace](replace.md) | Replace occurrences of a pattern across a CSV file. |
| [reverse](reverse.md) | Reverses rows of CSV data. |
| [safenames](safenames.md) | Modify headers of a CSV to only have "safe" names - guaranteed "database-ready" names |
| [sample](sample.md) | Randomly samples CSV data. |
| [schema](schema.md) | Generate JSON Schema or Polars Schema (with the `--polars` option) from CSV data. |
| [search](search.md) | Filters CSV data by whether the given regex matches a row. |
| [searchset](searchset.md) | Filters CSV data by whether the given regex set matches a row. |
| [select](select.md) | Select columns from CSV data efficiently. |
| [slice](slice.md) | Returns the rows in the range specified (starting at 0, half-open interval). |
| [snappy](snappy.md) | Does streaming compression/decompression of the input using the Snappy framing format. |
| [sniff](sniff.md) | Quickly sniff the first n rows and infer CSV metadata (delimiter, header row, number of |
| [sort](sort.md) | Sorts CSV data in lexicographical, natural, numerical, reverse, unique or random order. |
| [sortcheck](sortcheck.md) | Check if a CSV is sorted. The check is done on a streaming basis (i.e. constant memory). |
| [split](split.md) | Splits the given CSV data into chunks. It has three modes: by size (rowcount), |
| [sqlp](sqlp.md) | Run blazing-fast Polars SQL queries against several CSVs - replete with joins, aggregations, |
| [stats](stats.md) | Compute summary statistics & infers data types for each column in a CSV. |
| [table](table.md) | Outputs CSV data as a table with columns in alignment. |
| [template](template.md) | Renders a template using CSV data with the MiniJinja template engine. |
| [to](to.md) | Convert CSV files to PostgreSQL, SQLite, Excel XLSX, ODS, Parquet and Data Package. |
| [tojsonl](tojsonl.md) | Smartly converts CSV to a newline-delimited JSON (JSONL/NDJSON). |
| [transpose](transpose.md) | Transpose the rows/columns of CSV data. |
| [validate](validate.md) | Validates CSV data using two main modes: |
