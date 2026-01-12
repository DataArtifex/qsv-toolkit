# qsv to

```text
Convert CSV files to PostgreSQL, SQLite, Excel XLSX, ODS, Parquet and Data Package.

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

Example:

Load `file1.csv` and `file2.csv' into xlsx file.
Will create `output.xlsx`, creating new sheets for each file, with the sheet name being the
filename without the extension. Note the `output.xlsx` will be overwritten if it exists.

  $ qsv to xlsx output.xlsx file1.csv file2.csv

Load all files in dir1 into xlsx file.

  $ qsv to xlsx output.xlsx dir1

Load files listed in the 'ourdata.infile-list' into xlsx file.

  $ qsv to xlsx output.xlsx ourdata.infile-list

ODS
===
Convert to new ODS (Open Document Spreadsheet) file.

Example:

Load `file1.csv` and `file2.csv' into ODS file.
Will create `output.ods`, creating new sheets for each file, with the sheet name being the
filename without the extension. Note the `output.ods` will be overwritten if it exists.

  $ qsv to ods output.ods file1.csv file2.csv

Load all files in dir1 into ODS file.

  $ qsv to ods output.ods dir1

Load files listed in the 'ourdata.infile-list' into ODS file.

  $ qsv to ods output.ods ourdata.infile-list

PARQUET
=======
Convert to directory of parquet files.  Need to select a directory, it will be created if it does not exists.
If the `to_parquet` feature is not enabled, a simpler parquet conversion is available using the `sqlp`
subcommand with the `--format parquet` option.

To stream the data use the `pipe` option.  To pipe from stdin use `-` for the filename or use named pipe.
Type guessing is more limited with this option.

Examples:

Convert `file1.csv` and `file2.csv' into `mydir/file1.parquet` and `mydir/file2.parquet` files.

  $ qsv to parquet mydir file1.csv file2.csv

Convert from stdin.

  $ qsv to parquet --pipe mydir -

Convert all files in dir1 into parquet files in myparquetdir.

  $ qsv to parquet myparquetdir dir1

Convert files listed in the 'data.infile-list' into parquet files in myparquetdir.

  $ qsv to parquet myparquetdir data.infile-list

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
    qsv to postgres [options] <postgres> [<input>...]
    qsv to sqlite [options] <sqlite> [<input>...]
    qsv to xlsx [options] <xlsx> [<input>...]
    qsv to ods [options] <ods> [<input>...]
    qsv to parquet [options] <parquet> [<input>...]
    qsv to datapackage [options] <datapackage> [<input>...]
    qsv to --help

To options:
    -k --print-package     Print statistics as datapackage, by default will print field summary.
    -u --dump              Create database dump file for use with `psql` or `sqlite3` command line tools (postgres/sqlite only).
    -a --stats             Produce extra statistics about the data beyond just type guessing.
    -c --stats-csv <path>  Output stats as CSV to specified file.
    -q --quiet             Do not print out field summary.
    -s --schema <arg>      The schema to load the data into. (postgres only).
    -d --drop              Drop tables before loading new data into them (postgres/sqlite only).
    -e --evolve            If loading into existing db, alter existing tables so that new data will load. (postgres/sqlite only).
    -i --pipe              For parquet, allow piping from stdin (using `-`) or from a named pipe.
    -p --separator <arg>   For xlsx, use this character to help truncate xlsx sheet names.
                           Defaults to space.
    -A --all-strings       Convert all fields to strings.
    -j, --jobs <arg>       The number of jobs to run in parallel.
                           When not set, the number of jobs is set to the number of CPUs detected.

Common options:
    -h, --help             Display this message
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
