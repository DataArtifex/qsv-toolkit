# sqlp

```text
Run blazing-fast Polars SQL queries against several CSVs - replete with joins, aggregations,
grouping, table functions, sorting, and more - working on larger than memory CSV files directly,
without having to load it first into a database.

Polars SQL is a PostgreSQL dialect (https://docs.pola.rs/user-guide/sql/intro/), converting SQL
queries to ultra-fast Polars LazyFrame expressions (https://docs.pola.rs/user-guide/lazy/).

For a list of SQL functions and keywords supported by Polars SQL, see
https://docs.pola.rs/py-polars/html/reference/sql/index.html though be aware that it's for
the Python version of Polars, so there will be some minor syntax differences.

Returns the shape of the query result (number of rows, number of columns) to stderr.

Example queries:

  $ qsv sqlp data.csv 'select * from data where col1 > 10 order by all desc limit 20'

  $ qsv sqlp data.csv 'select col1, col2 as friendlyname from data' --format parquet --output data.parquet

  # enclose column names with spaces in double quotes
  $ qsv sqlp data.csv 'select "col 1", "col 2" from data'

  $ qsv sqlp data.csv data2.csv 'select * from data join data2 on data.colname = data2.colname'

  $ qsv sqlp data.csv data2.csv 'SELECT col1 FROM data WHERE col1 IN (SELECT col2 FROM data2)'

  # Use dollar-quoting to avoid escaping reserved characters in literals.
  https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-DOLLAR-QUOTING
  $ qsv sqlp data.csv "SELECT * FROM data WHERE col1 = $$O'Reilly$$"
  $ qsv sqlp data.csv 'SELECT * FROM data WHERE col1 = $SomeTag$Diane's horse "Twinkle"$SomeTag$'

  # Unions and Joins are supported.
  $ qsv sqlp data1.csv data2.csv 'SELECT * FROM data1 UNION ALL BY NAME SELECT * FROM data2'

  $ qsv sqlp tbl_a.csv tbl_b.csv tbl_c.csv "SELECT * FROM tbl_a \
     RIGHT ANTI JOIN tbl_b USING (b) \
     LEFT SEMI JOIN tbl_c USING (c)"

  # use "_t_N" aliases to refer to input files, where N is the 1-based index
  # of the input file/s. For example, _t_1 refers to the first input file, _t_2
  # refers to the second input file, and so on.
  $ qsv sqlp data.csv data2.csv 'select * from _t_1 join _t_2 on _t_1.colname = _t_2.colname'

  $ qsv sqlp data.csv 'SELECT col1, count(*) AS cnt FROM data GROUP BY col1 ORDER BY cnt DESC, col1 ASC'

  $ qsv sqlp data.csv "select lower(col1), substr(col2, 2, 4) from data WHERE starts_with(col1, 'foo')"

  $ qsv sqlp data.csv "select COALESCE(NULLIF(col2, ''), 'foo') from data"

  $ qsv sqlp tbl1.csv "SELECT x FROM tbl1 WHERE x IN (SELECT y FROM tbl1)"

  # Natural Joins are supported too! (https://www.w3resource.com/sql/joins/natural-join.php)
  $ qsv sqlp data1.csv data2.csv data3.csv \
    "SELECT COLUMNS('^[^:]+$') FROM data1 NATURAL JOIN data2 NATURAL JOIN data3 ORDER BY COMPANY_ID",

  # Use a SQL script to run a long, complex SQL query or to run SEVERAL SQL queries.
  # When running several queries, each query needs to be separated by a semicolon,
  # the last query will be returned as the result.
  # Typically, earlier queries are used to create tables that can be used in later queries.
  # Note that scripts support single-line comments starting with '--' so feel free to
  # add comments to your script.
  # In long, complex scripts that produce multiple temporary tables, note that you can use
  # `truncate table <table_name>;` to free up memory used by temporary tables. Otherwise,
  # the memory used by the temporary tables won't be freed until the script finishes.
  # See test_sqlp/sqlp_boston311_sql_script() for an example.
  $ qsv sqlp data.csv data2.csv data3.csv data4.csv script.sql --format json --output data.json

  # use Common Table Expressions (CTEs) using WITH to simplify complex queries
  $ qsv sqlp people.csv "WITH millennials AS (SELECT * FROM people WHERE age >= 25 and age <= 40) \
     SELECT * FROM millennials WHERE STARTS_WITH(name,'C')"

  # CASE statement
  $ qsv sqlp data.csv "select CASE WHEN col1 > 10 THEN 'foo' WHEN col1 > 5 THEN 'bar' ELSE 'baz' END from data"
  $ qsv sqlp data.csv "select CASE col*5 WHEN 10 THEN 'foo' WHEN 5 THEN 'bar' ELSE 'baz' END from _t_1"

  # spaceship operator: "<=>" (three-way comparison operator)
  #  returns -1 if left < right, 0 if left == right, 1 if left > right
  # https://en.wikipedia.org/wiki/Three-way_comparison#Spaceship_operator
  $ qsv sqlp data.csv data2.csv "select data.c2 <=> data2.c2 from data join data2 on data.c1 = data2.c1"

  # support ^@ ("starts with"), and ~~ (like) ,~~* (ilike),!~~ (not like),!~~* (not ilike) operators
  $ qsv sqlp data.csv "select * from data WHERE col1 ^@ 'foo'"
  $ qsv sqlp data.csv "select c1 ^@ 'a' AS c1_starts_with_a from data"
  $ qsv sqlp data.csv "select c1 ~~* '%B' AS c1_ends_with_b_caseinsensitive from data"

  # support SELECT * ILIKE wildcard syntax
  # select all columns from customers where the column contains 'a' followed by an 'e'
  # with any characters (or no characters), in between, case-insensitive
  # if customers.csv has columns LastName, FirstName, Address, City, State, Zip
  # this query will return all columns for all rows except the columns that don't
  # contain 'a' followed by an 'e' - i.e. except City and Zip
  $ qsv sqlp customers.csv "SELECT * ILIKE '%a%e%' FROM customers ORDER BY LastName, FirstName"

  # regex operators: "~" (contains pattern, case-sensitive); "~*" (contains pattern, case-insensitive)
  #   "!~" (does not contain pattern, case-sensitive); "!~*" (does not contain pattern, case-insensitive)
  $ qsv sqlp data.csv "select * from data WHERE col1 ~ '^foo' AND col2 > 10"
  $ qsv sqlp data.csv "select * from data WHERE col1 !~* 'bar$' AND col2 > 10"

  # regexp_like function: regexp_like(<string>, <pattern>, <optional flags>)
  # returns true if <string> matches <pattern>, false otherwise
  #   <optional flags> can be one or more of the following:
  #   'c' (case-sensitive - default), 'i' (case-insensitive), 'm' (multiline)
  $ qsv sqlp data.csv "select * from data WHERE regexp_like(col1, '^foo') AND col2 > 10"
  # case-insensitive regexp_like
  $ qsv sqlp data.csv "select * from data WHERE regexp_like(col1, '^foo', 'i') AND col2 > 10"

  # regexp match using a literal pattern
  $ qsv sqlp data.csv "select idx,val from data WHERE val regexp '^foo'"

  # regexp match using patterns from another column
  $ qsv sqlp data.csv "select idx,val from data WHERE val regexp pattern_col"

  # use Parquet, JSONL and Arrow files in SQL queries
  $ qsv sqlp data.csv "select * from data join read_parquet('data2.parquet') as t2 ON data.c1 = t2.c1"
  $ qsv sqlp data.csv "select * from data join read_ndjson('data2.jsonl') as t2 on data.c1 = t2.c1"
  $ qsv sqlp data.csv "select * from data join read_ipc('data2.arrow') as t2 ON data.c1 = t2.c1"
  $ qsv sqlp SKIP_INPUT "select * from read_parquet('data.parquet') order by col1 desc limit 100"
  $ qsv sqlp SKIP_INPUT "select * from read_ndjson('data.jsonl') as t1 join read_ipc('data.arrow') as t2 on t1.c1 = t2.c1"

  # you can also directly load CSVs using the Polars read_csv() SQL function. This is useful when
  # you want to bypass the regular CSV parser (with SKIP_INPUT) and use Polars' multithreaded,
  # mem-mapped CSV parser instead - making for dramatically faster queries at the cost of CSV parser
  # configurability (i.e. limited to comma delimiter, no CSV comments, etc.).
  $ qsv sqlp SKIP_INPUT "select * from read_csv('data.csv') order by col1 desc limit 100"

  # note that you can also use read_csv() to read compressed files directly
  # gzip, zstd and zlib automatic decompression are supported
  $ qsv sqlp SKIP_INPUT "select * from read_csv('data.csv.gz')"
  $ qsv sqlp SKIP_INPUT "select * from read_csv('data.csv.zst')"
  $ qsv sqlp SKIP_INPUT "select * from read_csv('data.csv.zlib')"

  # apart from using Polar's table functions, you can also use SKIP_INPUT when the SELECT
  # statement doesn't require an input file
  $ qsv sqlp SKIP_INPUT "SELECT 1 AS one, '2' AS two, 3.0 AS three"

  # use stdin as input
  $ cat data.csv | qsv sqlp - 'select * from stdin'
  $ cat data.csv | qsv sqlp - data2.csv 'select * from stdin join data2 on stdin.col1 = data2.col1'

  # automatic snappy decompression/compression
  $ qsv sqlp data.csv.sz 'select * from data where col1 > 10' --output result.csv.sz

  # explain query plan
  $ qsv sqlp data.csv 'explain select * from data where col1 > 10 order by col2 desc limit 20'

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_sqlp.rs.

Usage:
    qsv sqlp [options] <input>... <sql>
    qsv sqlp --help

sqlp arguments:
    input                  The CSV file/s to query. Use '-' for standard input.
                           If input is a directory, all files in the directory will be read as input.
                           If the input is a file with a '.infile-list' extension, the
                           file will be read as a list of files to use as input.
                           If the input are snappy compressed file(s), it will be
                           decompressed automatically.
                           Column headers are required. Use 'qsv rename _all_generic --no-headers'
                           to add generic column names (_col_N) to a CSV with no headers.
                           If you are using Polars SQL's table functions like read_csv() & read_parquet()
                           to read input files directly in the SQL statement, you can use the sentinel value
                           'SKIP_INPUT' to skip input preprocessing.
                           If pschema.json file/s exists for the input file/s, they will automatically be
                           used to optimize the query even if --cache-schema is not set.

    sql                    The SQL query/ies to run. Each input file will be available as a table
                           named after the file name (without the extension), or as "_t_N"
                           where N is the 1-based index.
                           If the query ends with ".sql", it will be read as a SQL script file,
                           with each SQL query separated by a semicolon. It will execute the queries
                           in order, and the result of the LAST query will be returned as the result.
                           SQL scripts support single-line comments starting with '--'.

sqlp options:
    --format <arg>            The output format to use. Valid values are:
                                csv      Comma-separated values
                                json     JSON
                                jsonl    JSONL (JSON Lines)
                                parquet  Apache Parquet
                                arrow    Apache Arrow IPC
                                avro     Apache Avro
                              [default: csv]

                              POLARS CSV INPUT PARSING OPTIONS:
    --try-parsedates          Automatically try to parse dates/datetimes and time.
                              If parsing fails, columns remain as strings.
                              Note that if dates are not well-formatted in your CSV,
                              that you may want to try to set `--ignore-errors` to relax
                              the CSV parsing of dates.
    --infer-len <arg>         The number of rows to scan when inferring the schema of the CSV.
                              Set to 0 to do a full table scan (warning: can be slow).
                              [default: 10000]
    --cache-schema            Create and cache Polars schema JSON files.
                              If the schema file/s exists, it will load the schema instead of inferring
                              it (ignoring --infer-len) and attempt to use it for each corresponding
                              Polars "table" with the same file stem.
                              If specified and the schema file/s do not exist, it will check if a
                              stats cache is available. If so, it will use it to derive a Polars schema
                              and save it. If there's no stats cache, it will infer the schema
                              using --infer-len and save the inferred schemas.
                              Each schema file will have the same file stem as the corresponding
                              input file, with the extension ".pschema.json"
                              (data.csv's Polars schema file will be data.pschema.json)
                              NOTE: You can edit the generated schema files to change the Polars schema
                              and cast columns to the desired data type. For example, you can force
                              a Float32 column to be a Float64 column by changing the "Float32" type
                              to "Float64" in the schema file.
                              You can also cast a Float to a Decimal with a desired precision and scale.
                              (e.g. instead of "Float32", use "{Decimal" : [10, 3]}")
                              The valid types are: `Boolean`, `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`,
                              `Int16`, `Int32`, `Int64`, `Float32`, `Float64`, `String`, `Date`, `Datetime`,
                              `Duration`, `Time`, `Null`, `Categorical`, `Decimal` and `Enum`.

    --streaming               Use streaming mode when parsing CSVs. This will use less memory
                              but will be slower. Only use this when you get out of memory errors.
    --low-memory              Use low memory mode when parsing CSVs. This will use less memory
                              but will be slower. Only use this when you get out of memory errors.
    --no-optimizations        Disable non-default query optimizations. This will make queries slower.
                              Use this when you get query errors or to force CSV parsing when there
                              is only one input file, no CSV parsing options are used and its not
                              a SQL script.
    --truncate-ragged-lines   Truncate ragged lines when parsing CSVs. If set, rows with more
                              columns than the header will be truncated. If not set, the query
                              will fail. Use this only when you get an error about ragged lines.
    --ignore-errors           Ignore errors when parsing CSVs. If set, rows with errors
                              will be skipped. If not set, the query will fail.
                              Only use this when debugging queries, as Polars does batched
                              parsing and will skip the entire batch where the error occurred.
                              To get more detailed error messages, set the environment variable
                              POLARS_BACKTRACE_IN_ERR=1 before running the query.
    --rnull-values <arg>      The comma-delimited list of case-sensitive strings to consider as
                              null values when READING CSV files (e.g. NULL, NONE, <empty string>).
                              Use "<empty string>" to consider an empty string a null value.
                              [default: <empty string>]
    --decimal-comma           Use comma as the decimal separator when parsing & writing CSVs.
                              Otherwise, use period as the decimal separator.
                              Note that you'll need to set --delimiter to an alternate delimiter
                              other than the default comma if you are using this option.

                              CSV OUTPUT FORMAT ONLY:
    --datetime-format <fmt>   The datetime format to use writing datetimes.
                              See https://docs.rs/chrono/latest/chrono/format/strftime/index.html
                              for the list of valid format specifiers.
    --date-format <fmt>       The date format to use writing dates.
    --time-format <fmt>       The time format to use writing times.
    --float-precision <arg>   The number of digits of precision to use when writing floats.
    --wnull-value <arg>       The string to use when WRITING null values.
                              [default: <empty string>]

                              ARROW/AVRO/PARQUET OUTPUT FORMATS ONLY:
    --compression <arg>       The compression codec to use when writing arrow or parquet files.
                                For Arrow, valid values are: zstd, lz4, uncompressed
                                For Avro, valid values are: deflate, snappy, uncompressed (default)
                                For Parquet, valid values are: zstd, lz4raw, gzip, snappy, uncompressed
                              [default: zstd]

                              PARQUET OUTPUT FORMAT ONLY:
    --compress-level <arg>    The compression level to use when using zstd or gzip compression.
                              When using zstd, valid values are -7 to 22, with -7 being the
                              lowest compression level and 22 being the highest compression level.
                              When using gzip, valid values are 1-9, with 1 being the lowest
                              compression level and 9 being the highest compression level.
                              Higher compression levels are slower.
                              The zstd default is 3, and the gzip default is 6.
    --statistics              Compute column statistics when writing parquet files.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading and writing CSV data.
                           Must be a single character. [default: ,]
    -q, --quiet            Do not return result shape to stderr.
```
