# qsv enum

```text
Add a new column enumerating the lines of a CSV file. This can be useful to keep
track of a specific line order, give a unique identifier to each line or even
make a copy of the contents of a column.

The enum function has four modes of operation:

  1. INCREMENT. Add an incremental identifier to each of the lines:
    $ qsv enum file.csv

  2. UUID4. Add a uuid v4 to each of the lines:
    $ qsv enum --uuid4 file.csv

  3. UUID7. Add a uuid v7 to each of the lines:
    $ qsv enum --uuid7 file.csv

  3. CONSTANT. Create a new column filled with a given value:
    $ qsv enum --constant 0

  4. COPY. Copy the contents of a column to a new one:
    $ qsv enum --copy names

  5. HASH. Create a new column with the deterministic hash of the given column/s.
     The hash uses the xxHash algorithm and is platform-agnostic.
     (see https://github.com/DoumanAsh/xxhash-rust for more information):
    $ qsv enum --hash 1- // hash all columns, auto-ignores existing "hash" column
    $ qsv enum --hash col2,col3,col4 // hash specific columns
    $ qsv enum --hash col2 // hash a single column
    $ qsv enum --hash /record_id|name|address/ // hash columns that match a regex
    $ qsv enum --hash !/record_id/ // hash all columns except the record_id column

  Finally, you should also be able to shuffle the lines of a CSV file by sorting
  on the generated uuid4s:
    $ qsv enum --uuid4 file.csv | qsv sort -s uuid4 > shuffled.csv

  This will shuffle the lines of the file.csv file as uuids generated using the v4
  specification are random and for practical purposes, are unique (1 in 2^122).
  See https://en.wikipedia.org/wiki/Universally_unique_identifier#Collisions

  However, sorting on uuid7 identifiers will not work as they are time-based
  and monotonically increasing, and will not shuffle the lines.

Usage:
    qsv enum [options] [<input>]
    qsv enum --help

enum options:
    -c, --new-column <name>  Name of the column to create.
                             Will default to "index".
    --start <value>          The value to start the enumeration from.
                             Only applies in Increment mode.
                             (default: 0)
    --increment <value>      The value to increment the enumeration by.
                             Only applies in Increment mode.
                             (default: 1)
    --constant <value>       Fill a new column with the given value.
                             Changes the default column name to "constant" unless
                             overridden by --new-column.
                             To specify a null value, pass the literal "<NULL>".
    --copy <column>          Name of a column to copy.
                             Changes the default column name to "{column}_copy"
                             unless overridden by --new-column.
    --uuid4                  When set, the column will be populated with
                             uuids (v4) instead of the incremental identifier.
                             Changes the default column name to "uuid4" unless
                             overridden by --new-column.
    --uuid7                  When set, the column will be populated with
                             uuids (v7) instead of the incremental identifier.
                             uuid v7 is a time-based uuid and is monotonically increasing.
                             See https://buildkite.com/blog/goodbye-integers-hello-uuids
                             Changes the default column name to "uuid7" unless
                             overridden by --new-column.
    --hash <columns>         Create a new column filled with the hash of the
                             given column/s. Use "1-" to hash all columns.
                             Changes the default column name to "hash" unless
                             overridden by --new-column.
                             Will remove an existing "hash" column if it exists.

                             The <columns> argument specify the columns to use
                             in the hash. Columns can be referenced by name or index,
                             starting at 1. Specify multiple columns by separating
                             them with a comma. Specify a range of columns with `-`.
                             (See 'qsv select --help' for the full syntax.)

Common options:
    -h, --help               Display this message
    -o, --output <file>      Write output to <file> instead of stdout.
    -n, --no-headers         When set, the first row will not be interpreted
                             as headers.
    -d, --delimiter <arg>    The field delimiter for reading CSV data.
                             Must be a single character. (default: ,)
```
