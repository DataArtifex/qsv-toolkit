# qsv to

<small>v19.1.0</small>

```text
Convert CSV files to Parquet, PostgreSQL, SQLite, Excel XLSX, ODS and Data Package.

PARQUET
=======
Convert CSV files to Parquet format. Each input CSV produces a separate .parquet file
in the specified output directory. The output directory will be created if it does not exist.

Requires the `polars` feature to be enabled.

Compression can be specified with --compression (default: zstd).
Supported values: zstd, gzip, snappy, lz4raw, uncompressed.
Use --compress-level to set the compression level for gzip (default: 6) or zstd (default: 3).

Examples:

Convert `file1.csv` and `file2.csv` to parquet files in output_dir/

  $ qsv to parquet output_dir file1.csv file2.csv

Convert all CSVs in a directory to parquet.

  $ qsv to parquet output_dir dir1

Convert files listed in the 'input.infile-list' to parquet.

  $ qsv to parquet output_dir input.infile-list

Convert with snappy compression.

  $ qsv to parquet output_dir --compression snappy file1.csv

Convert with zstd compression at level 10.

  $ qsv to parquet output_dir --compression zstd --compress-level 10 file1.csv

Convert from stdin with a custom filename.

  $ cat data.csv | qsv to parquet output_dir --table mydata -

POSTGRESQL
==========
To convert to postgres you need to supply connection string.
The format is described here - https://docs.rs/postgres/latest/postgres/config/struct.Config.html#examples-1.
Additionally you can use `env=MY_ENV_VAR` and qsv will get the connection string from the
environment variable `MY_ENV_VAR`.

If using the `--dump` option instead of a connection string put a name of a file or `-` for stdout.

Examples:

Load `file1.csv` and `file2.csv' file to local database `test`, with user `testuser`, and password `pass`.

  $ qsv to postgres 'postgres://testuser:pass@localhost/test' file1.csv file2.csv

Load same files into a new/existing postgres schema `myschema`

  $ qsv to postgres 'postgres://testuser:pass@localhost/test' --schema=myschema file1.csv file2.csv

Load same files into a new/existing postgres database whose connection string is in the
`DATABASE_URL` environment variable.

  $ qsv to postgres 'env=DATABASE_URL' file1.csv file2.csv

Load files inside a directory to a local database 'test' with user `testuser`, password `pass`.

  $ qsv to postgres 'postgres://testuser:pass@localhost/test' dir1

Load files listed in the 'input.infile-list' to a local database 'test' with user `testuser`, password `pass`.

  $ qsv to postgres 'postgres://testuser:pass@localhost/test' input.infile-list

Drop tables if they exist before loading.

  $ qsv to postgres 'postgres://testuser:pass@localhost/test' --drop file1.csv file2.csv

Evolve tables if they exist before loading. Read http://datapackage_convert.opendata.coop/evolve.html
to explain how evolving works.

  $ qsv to postgres 'postgres://testuser:pass@localhost/test' --evolve file1.csv file2.csv

Create dump file.

  $ qsv to postgres --dump dumpfile.sql file1.csv file2.csv

Print dump to stdout.

  $ qsv to postgres --dump - file1.csv file2.csv


SQLITE
======
Convert to sqlite db file. Will be created if it does not exist.

If using the `--dump` option, instead of a sqlite database file, put the name of the dump file or `-` for stdout.

Examples:

Load `file1.csv` and `file2.csv' files to sqlite database `test.db`

  $ qsv to sqlite test.db file1.csv file2.csv

Load all files in dir1 to sqlite database `test.db`

  $ qsv to sqlite test.db dir

Load files listed in the 'mydata.infile-list' to sqlite database `test.db`

  $ qsv to sqlite test.db mydata.infile-list

Drop tables if they exist before loading.

  $ qsv to sqlite test.db --drop file1.csv file2.csv

Evolve tables if they exist. Read http://datapackage_convert.opendata.coop/evolve.html
to explain how evolving is done.

  $ qsv to sqlite test.db --evolve file1.csv file2.csv

Create dump file .

  $ qsv to sqlite --dump dumpfile.sql file1.csv file2.csv

Print dump to stdout.

  $ qsv to sqlite --dump - file1.csv file2.csv


EXCEL XLSX
==========
Convert to new xlsx file.

Examples:

Load `file1.csv` and `file2.csv' into xlsx file.
Will create `output.xlsx`, creating new sheets for each file, with the sheet name being the
filename without the extension. Note the `output.xlsx` will be overwritten if it exists.

  $ qsv to xlsx output.xlsx file1.csv file2.csv

Load all files in dir1 into xlsx file.

  $ qsv to xlsx output.xlsx dir1

Load files listed in the 'ourdata.infile-list' into xlsx file.

  $ qsv to xlsx output.xlsx ourdata.infile-list

Load a single CSV into xlsx with a custom sheet name.

  $ qsv to xlsx output.xlsx --table "Sales Data" file1.csv

Load from stdin with a custom sheet name.

  $ cat data.csv | qsv to xlsx output.xlsx --table "Monthly Report" -

ODS
===
Convert to new ODS (Open Document Spreadsheet) file.

Examples:

Load `file1.csv` and `file2.csv' into ODS file.
Will create `output.ods`, creating new sheets for each file, with the sheet name being the
filename without the extension. Note the `output.ods` will be overwritten if it exists.

  $ qsv to ods output.ods file1.csv file2.csv

Load all files in dir1 into ODS file.

  $ qsv to ods output.ods dir1

Load files listed in the 'ourdata.infile-list' into ODS file.

  $ qsv to ods output.ods ourdata.infile-list

Load a single CSV into ODS with a custom sheet name.

  $ qsv to ods output.ods --table "Sales Data" file1.csv

Load from stdin with a custom sheet name.

  $ cat data.csv | qsv to ods output.ods --table "Monthly Report" -

DATA PACKAGE
============
Generate a datapackage, which contains stats and information about what is in the CSV files.

Examples:

Generate a `datapackage.json` file from `file1.csv` and `file2.csv' files.

  $ qsv to datapackage datapackage.json file1.csv file2.csv

Add more stats to datapackage.

  $ qsv to datapackage datapackage.json --stats file1.csv file2.csv

Generate a `datapackage.json` file from all the files in dir1

  $ qsv to datapackage datapackage.json dir1

Generate a `datapackage.json` file from all the files listed in the 'data.infile-list'

  $ qsv to datapackage datapackage.json data.infile-list

For all other conversions you can output the datapackage created by specifying `--print-package`.

  $ qsv to xlsx datapackage.xlsx --stats --print-package file1.csv file2.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_to.rs.

Usage:
    qsv to parquet [options] <destination> [<input>...]
    qsv to postgres [options] <destination> [<input>...]
    qsv to sqlite [options] <destination> [<input>...]
    qsv to xlsx [options] <destination> [<input>...]
    qsv to ods [options] <destination> [<input>...]
    qsv to datapackage [options] <destination> [<input>...]
    qsv to --help

To arguments:
    <destination>           The output target, which varies by subcommand:
                            * parquet: output directory (created if needed)
                            * postgres: connection string or env=VAR_NAME (with --dump: dump file path or - for stdout)
                            * sqlite: database file path (with --dump: dump file path or - for stdout)
                            * xlsx: output .xlsx file path
                            * ods: output .ods file path
                            * datapackage: output .json file path
    <input>...              Input CSV file(s) to convert. Can be file path(s), a directory,
                            an .infile-list file, or `-` for stdin (not supported by
                            parquet subcommand).

To options:
  -k, --print-package     Print statistics as datapackage, by default will print field summary.
  -u, --dump              Create database dump file for use with `psql` or `sqlite3` command line tools
                          (postgres/sqlite only).
  -a, --stats             Produce extra statistics about the data beyond just type guessing.
  -c, --stats-csv <path>  Output stats as CSV to specified file.
  -q, --quiet             Do not print out field summary.
  -s, --schema <arg>      The schema to load the data into. (postgres only).
  --infer-len <rows>      The number of rows to use for schema inference (parquet only).
                          Note that even if a pschema.json file exists for an input file,
                          explicitly specifying infer-len will cause qsv to ignore the pschema.json and
                          infer the schema from the CSV data instead, including when set to 0.
                          Set to 0 to infer from all rows (not recommended for large files).
  --try-parse-dates       Attempt to parse date/datetime columns with polars' date inference logic.
                          This may result in more accurate date parsing, but can be slower on large files.
                          (parquet only).
  -d, --drop              Drop tables before loading new data into them (postgres/sqlite only).
  -e, --evolve            If loading into existing db, alter existing tables so that new data will load.
                          (postgres/sqlite only).
  -i, --pipe              Adjust output format for piped data (omits row counts and field format columns).
  -t, --table <name>      Use this as the table/sheet/file name (postgres/sqlite/xlsx/ods/parquet).
                          Overrides the default name derived from the input filename.
                          When reading from stdin, the default table name is "stdin".
                          Only valid with a single input file.
                          For postgres/sqlite: must start with a letter or underscore,
                          contain only alphanumeric characters and underscores (max 63).
                          For xlsx/ods: used as sheet name (max 31 chars,
                          cannot contain \ / * [ ] : ?).
  -p, --separator <arg>   For xlsx, use this character to help truncate xlsx sheet names.
                          Defaults to space.
      --compression <arg>  Parquet compression codec (parquet only).
                           Valid values: zstd (default), gzip, snappy, lz4raw, uncompressed.
      --compress-level <arg>  Compression level (parquet only).
                              For gzip: 1-9 (default: 6). For zstd: -7 to 22 (default: 3).
                              Ignored for other codecs.
  -A, --all-strings       Convert all fields to strings.
  -j, --jobs <arg>        The number of jobs to run in parallel.
                          When not set, the number of jobs is set to the number of CPUs detected.

Common options:
    -h, --help             Display this message
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
