# qsv schema

<small>v28.0.0</small>

```text
Generate JSON Schema or Polars Schema (with the `--polars` option) from CSV data.

JSON Schema Validation:
=======================
This command derives a JSON Schema Validation (Draft 2020-12) file from CSV data,
including validation rules based on data type and input data domain/range.
https://json-schema.org/draft/2020-12/json-schema-validation.html

Running `validate` command on original input CSV with generated schema
should not flag any invalid records.

The intended workflow is to use the `schema` command to generate a JSON schema file
from representative CSV data, fine-tune the JSON schema file as needed, and then use
the `validate` command to validate other CSV data with the same structure using the
generated JSON schema.

After manually fine-tuning the JSON schema file, note that you can also use the
`validate` command to validate the JSON Schema file as well:

  $ qsv validate schema manually-tuned-jsonschema.json

The generated JSON schema file has `.schema.json` suffix appended. For example,
for input `mydata.csv`, the generated JSON schema is `mydata.csv.schema.json`.

If piped from stdin, the schema file will be `stdin.csv.schema.json` and
a `stdin.csv` file will be created with stdin's contents as well.

Note that `stdin.csv` will be overwritten if it already exists.

Schema generation can be a compute-intensive process, especially for large CSV files.
To speed up generation, the `schema` command will reuse a `stats.csv.data.jsonl` file if it
exists and is current (i.e. stats generated with --cardinality and --infer-dates options).
Otherwise, it will run the `stats` command to generate the `stats.csv.data.jsonl` file first,
and then use that to generate the schema file.

Polars Schema:
==============
When the "polars" feature is enabled, the `--polars` option will generate a Polars schema
instead of a JSON Schema. The generated Polars schema will be written to a file with the
`.pschema.json` suffix appended to the input file stem.

The Polars schema is a JSON object that describes the schema of a CSV file. When present,
the `sqlp`, `joinp`, and `pivotp` commands will use the Polars schema to read the CSV file
instead of inferring the schema from the CSV data. Not only does this allow these commands to
skip schema inferencing which may fail when the inferencing sample is too low, it also allows
Polars to optimize the query and gives the user the option to tailor the schema to their specific
query needs (e.g. using a Decimal type with explicit precision and scale instead of a Float type).

Date and datetime columns are only given a Polars Date/Datetime type if Polars can read their
values as qsv does. Columns in formats Polars can't parse (e.g. "04/18/2019 09:55:45 PM") are
typed String instead, so the schema doesn't make later reads fail. So are day-first dates when
neither --prefer-dmy nor QSV_PREFER_DMY is set, as Polars reads "04/05/2019" as 4 May.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_schema.rs.
See also https://github.com/dathere/qsv/wiki/Validation-and-Schema#schema

Usage:
    qsv schema [options] [<input>]
    qsv schema --help

Schema options:
    --enum-threshold <num>     Cardinality threshold for adding enum constraints.
                               Enum constraints are compiled for String & Integer types.
                               [default: 50]
    -i, --ignore-case          Ignore case when compiling unique values for enum constraints.
                               String columns are then checked against the enum threshold
                               by their case-insensitive cardinality.
                               As the `validate` command is case-sensitive, the
                               enum & const constraints of String columns are written
                               as equivalent case-insensitive regex patterns instead
                               (e.g. "^(?i:false|true)$"). These use the inline `(?i:...)`
                               modifier, which other JSON Schema validators may not
                               support, e.g. on older JavaScript engines.
    --strict-dates             Enforce Internet Datetime format (RFC-3339) for
                               detected date/datetime columns. Otherwise, even if
                               columns are inferred as date/datetime, they are set
                               to type "string" in the schema instead of
                               "date" or "date-time".
    --strict-formats           Enforce JSON Schema format constraints for
                               detected email, hostname, and IP address columns.
                               When enabled, String fields are checked against
                               email, hostname, IPv4, and IPv6 formats. Format
                               constraints are only added if ALL unique values
                               in the field match the detected format. Hostnames
                               must contain a dot (e.g. "example.com"), so columns
                               of single words are not mistaken for hostnames.
    --pattern-columns <args>   Select columns to derive regex pattern constraints.
                               That is, this will create a regular expression
                               that matches all values for each specified column.
                               Columns are selected using `select` syntax
                               (see `qsv select --help` for details).
    --dates-whitelist <list>   The case-insensitive patterns to look for when
                               shortlisting fields for date inference.
                               i.e. if the field's name has any of these patterns,
                               it is shortlisted for date inferencing.
                               Set to "all" to inspect ALL fields for
                               date/datetime types.
                               [default: date,time,due,open,close,created]
    --prefer-dmy               Prefer to parse dates in dmy format.
                               Otherwise, use mdy format.
    --force                    Force recomputing cardinality and unique values
                               even if stats cache file exists and is current.
    --stdout                   Send generated JSON schema file to stdout instead.
    -j, --jobs <arg>           The number of jobs to run in parallel.
                               When not set, the number of jobs is set to the
                               number of CPUs detected.
    -o, --output <file>        Write output to <file> instead of using the default
                               filename. For JSON Schema, the default is
                               <input>.schema.json. For Polars schema, the default
                               is <input>.pschema.json.

    --polars                   Infer a Polars schema instead of a JSON Schema.
                               This option is only available if the `polars` feature is enabled.
                               The generated Polars schema will be written to a file with the
                               `.pschema.json` suffix appended to the input filename.
                               Requires an input file (stdin is not supported), and
                               cannot be combined with the --stdout option.

Common options:
    -h, --help                 Display this message
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. Namely, it will be processed with the rest
                               of the rows. Otherwise, the first row will always
                               appear as the header row in the output.
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character.
    --memcheck                 Check if there is enough memory to load the entire
                               CSV into memory using CONSERVATIVE heuristics.
```
