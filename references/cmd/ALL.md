# QSV Commands

<small>v28.0.0</small>

## qsv apply

```text
Apply a series of transformation functions to given CSV column/s. This can be used to
perform typical data-wrangling tasks and/or to harmonize some values, etc.

It has five subcommands:
 1. operations*   - 40 string, format, currency, regex & NLP operators.
 2. emptyreplace* - replace empty cells with <--replacement> string.
 3. dynfmt        - Dynamically constructs a new column from other columns using
                    the <--formatstr> template.
 4. calcconv      - parse and evaluate math expressions, with support for units
                    and conversions.
 5. summarize*    - summarize a column or group of columns using an OpenAI
                    API-compatible LLM (local or commercial), with customizable,
                    MiniJinja-templated per-record prompts.
    * subcommand is multi-column capable.

OPERATIONS (multi-column capable)
Multiple operations can be applied, with the comma-delimited operation series
applied in order:

  trim => Trim the cell
  trim,upper => Trim the cell, then transform to uppercase
  lower,simdln => Lowercase the cell, then compute the normalized
      Damerau-Levenshtein similarity to --comparand

Operations support multi-column transformations. Just make sure the
number of transformed columns with the --rename option is the same.
For example, to trim and fold to uppercase the col1,col2 and col3 columns &
rename them to newcol1,newcol2 and newcol3:

  qsv apply operations trim,upper col1,col2,col3 -r newcol1,newcol2,newcol3 file.csv

It has 40 supported operations:

  * len: Return string length
  * lower: Transform to lowercase
  * upper: Transform to uppercase
  * squeeze: Compress consecutive whitespaces
  * squeeze0: Remove whitespace
  * trim: Trim (drop whitespace left & right of the string)
  * ltrim: Left trim whitespace
  * rtrim: Right trim whitespace
  * mtrim: Trims --comparand matches left & right of the string (Rust trim_matches)
  * mltrim: Left trim --comparand matches (Rust trim_start_matches)
  * mrtrim: Right trim --comparand matches (Rust trim_end_matches)
  * strip_prefix: Removes specified prefix in --comparand
  * strip_suffix: Remove specified suffix in --comparand
  * escape - escape (Rust escape_default)
  * encode62: base62 encode
  * decode62: base62 decode
  * encode64: base64 encode
  * decode64: base64 decode
  * crc32: crc32 checksum
  * replace: Replace all matches of a pattern (using --comparand)
      with a string (using --replacement) (Rust replace)
  * regex_replace: Replace all regex matches in --comparand w/ --replacement.
      Specify <NULL> as --replacement to remove matches.
  * titlecase - capitalizes English text using Daring Fireball titlecase style
      https://daringfireball.net/2008/05/title_case
  * censor: profanity filter. Add additional comma-delimited profanities with --comparand.
  * censor_check: check if profanity is detected (boolean).
      Add additional comma-delimited profanities with -comparand.
  * censor_count: count of profanities detected.
      Add additional comma-delimited profanities with -comparand.
  * round: Round numeric values to the specified number of decimal places using
      Midpoint Nearest Even Rounding Strategy AKA "Bankers Rounding."
      Specify the number of decimal places with --formatstr (default: 3).
  * thousands: Add thousands separators to numeric values.
      Specify the separator policy with --formatstr (default: comma). The valid policies are:
      comma, dot, space, underscore, hexfour (place a space every four hex digits) and
      indiancomma (place a comma every two digits, except the last three digits).
      The decimal separator can be specified with --replacement (default: '.')
  * currencytonum: Gets the numeric value of a currency. Supports currency symbols
      (e.g. $,¥,£,€,֏,₱,₽,₪,₩,ƒ,฿,₫) and strings (e.g. USD, EUR, RMB, JPY, etc.).
      Recognizes point, comma and space separators. Is "permissive" by default, meaning it
      will allow no or non-ISO currency symbols. To enforce strict parsing, which will require
      a valid ISO currency symbol, set the --formatstr to "strict".
  * numtocurrency: Convert a numeric value to a currency. Specify the currency symbol
      with --comparand. Automatically rounds values to two decimal places. Specify
      "euro" formatting (e.g. 1.000,00 instead of 1,000.00 ) by setting --formatstr to "euro".
      Specify conversion rate by setting --replacement to a number.
  * gender_guess: Guess the gender of a name.
  * copy: Mark a column for copying
  * simdl: Damerau-Levenshtein similarity to --comparand
  * simdln: Normalized Damerau-Levenshtein similarity to --comparand (between 0.0 & 1.0)
  * simjw: Jaro-Winkler similarity to --comparand (between 0.0 & 1.0)
  * simsd: Sørensen-Dice similarity to --comparand (between 0.0 & 1.0)
  * simhm: Hamming distance to --comparand. Num of positions characters differ.
  * simod: Optimal String Alignment (OSA) Distance to --comparand.
  * eudex: Multi-lingual sounds like --comparand (boolean)
       Tested on English, Catalan, German, Spanish, Swedish and Italian dictionaries.
       It supports all C1 letters (e.g. ü, ö, æ, ß, é, etc.) and takes their sound into account.
       It should work on other European languages that use the Latin alphabet.
  * sentiment: Normalized VADER sentiment score (English only - between -1.0 to 1.0).
  * whatlang: Language Detection for 87 supported languages, with default confidence threshold
       of 0.9, which can be overridden by assigning 0.0 to 1.0 to --comparand.
       If language detection confidence is below the threshold, it will still show the best language
       guess, followed by the confidence score, ending with a question mark.
       If you want to always displays the confidence score, end the --comparand value with a
       question mark (e.g. 0.9?)
       https://github.com/greyblake/whatlang-rs/blob/master/SUPPORTED_LANGUAGES.md


EMPTYREPLACE (multi-column capable)
Replace empty cells with <--replacement> string.
Non-empty cells are not modified. See the `fill` command for more complex empty field operations.


DYNFMT
Dynamically constructs a new column from other columns using the <--formatstr> template.
The template can contain arbitrary characters. To insert a column value, enclose the
column name in curly braces, replacing all non-alphanumeric characters with underscores.

If you need to dynamically construct a column with more complex formatting requirements and
computed values, check out the py command to take advantage of Python's f-string formatting.


CALCCONV
Parse and evaluate math expressions into a new column, with support for units and conversions.
The math expression is built dynamically using the <--formatstr> template, similar to the DYNFMT
subcommand, with the addition that if the literal '<UNIT>' is found at the end of the template, the
inferred unit will be appended to the result.

For a complete list of supported units, constants, operators and functions, see https://docs.rs/cpc

Examples:

== OPERATIONS ==

  # Trim, then transform to uppercase the surname field.
  qsv apply operations trim,upper surname file.csv

  # Trim, then transform to uppercase the surname field and rename the column uppercase_clean_surname.
  qsv apply operations trim,upper surname -r uppercase_clean_surname file.csv

  # Trim, then transform to uppercase the surname field and
  # save it to a new column named uppercase_clean_surname.
  qsv apply operations trim,upper surname -c uppercase_clean_surname file.csv

  # Trim, then transform to uppercase the firstname and surname fields and
  # rename the columns ufirstname and usurname.
  qsv apply operations trim,upper firstname,surname -r ufirstname,usurname file.csv

  # Trim parentheses & brackets from the description field.
  qsv apply operations mtrim description --comparand '()<>' file.csv

  # Replace ' and ' with ' & ' in the description field.
  qsv apply operations replace description --comparand ' and ' --replacement ' & ' file.csv

  # Extract the numeric value of the Salary column in a new column named Salary_num.
  qsv apply operations currencytonum Salary -c Salary_num file.csv

  # Convert the USD_Price to PHP_Price using the currency symbol "PHP" with a conversion rate of 60.
  qsv apply operations numtocurrency USD_Price -C PHP -R 60 -c PHP_Price file.csv

  # Base64 encode the text_col column & save the encoded value into new column named encoded & decode it.
  qsv apply operations encode64 text_col -c encoded file.csv | qsv apply operations decode64 encoded

  # Compute the Normalized Damerau-Levenshtein similarity of the neighborhood column to
  # the string 'Roxbury' and save it to a new column named dln_roxbury_score.
  qsv apply operations lower,simdln neighborhood --comparand roxbury -c dln_roxbury_score boston311.csv

  # You can also use this subcommand command to make a copy of a column:
  qsv apply operations copy col_to_copy -c col_copy file.csv

== EMPTYREPLACE ==

  # Replace empty cells in file.csv Measurement column with 'None'.
  qsv apply emptyreplace Measurement --replacement None file.csv

  # Replace empty cells in file.csv Measurement column with 'Unknown Measurement'.
  qsv apply emptyreplace Measurement --replacement 'Unknown Measurement' file.csv

  # Replace empty cells in file.csv M1,M2 and M3 columns with 'None'.
  qsv apply emptyreplace M1,M2,M3 --replacement None file.csv

  # Replace all empty cells in file.csv for columns that start with 'Measurement' with 'None'.
  qsv apply emptyreplace '/^Measurement/' --replacement None file.csv

  # Replace all empty cells in file.csv for columns that start with 'observation'
  # case insensitive with 'None'.
  qsv apply emptyreplace --replacement None '/(?i)^observation/' file.csv

== DYNFMT ==

  # Create a new column 'mailing address' from 'house number', 'street', 'city'
  # and 'zip-code' columns:
  qsv apply dynfmt --formatstr '{house_number} {street}, {city} {zip_code} USA' -c 'mailing address' file.csv

  # Create a new column 'FullName' from 'FirstName', 'MI', and 'LastName' columns:
  qsv apply dynfmt --formatstr 'Sir/Madam {FirstName} {MI}. {LastName}' -c FullName file.csv

== CALCCONV ==

  # Do simple arithmetic:
  qsv apply calcconv --formatstr '{col1} + {col2} * {col3}' --new-column result file.csv

  # Arithmetic with support for operators like % and ^:
  qsv apply calcconv --formatstr '{col1} % 3' --new-column remainder file.csv

  # Convert from one unit to another:
  qsv apply calcconv --formatstr '{col1} Fahrenheit in Celsius' -c metric_temperature file.csv

  # Mix units and conversions are automatically done for you:
  qsv apply calcconv --formatstr '{col1}km + {col2}mi in meters' -c meters file.csv

  # You can append the inferred unit at the end of the result by ending the expression with '<UNIT>':
  qsv apply calcconv --formatstr '({col1} + {col2})km to light years <UNIT>' -c light_years file.csv

  # You can even do complex temporal unit conversions:
  qsv apply calcconv --formatstr '{col1}m/s + {col2}mi/h in kilometers per h' -c kms_per_h file.csv

  # Use math functions - see https://docs.rs/cpc/latest/cpc/enum.FunctionIdentifier.html for list of functions:
  qsv apply calcconv --formatstr 'round(sqrt{col1}^4)! liters' -c liters file.csv

  # Use percentages:
  qsv apply calcconv --formatstr '10% of abs(sin(pi)) horsepower to watts' -c watts file.csv

  # Use very large numbers:
  qsv apply calcconv --formatstr '{col1} Billion Trillion * {col2} quadrillion vigintillion' -c num_atoms file.csv

== SUMMARIZE ==

The summarize subcommand sends each record to an OpenAI API-compatible LLM and stores the
returned summary in a new column. The prompt is a MiniJinja template (like `qsv template`)
rendered per record - reference any column by its "safe" name (non-alphanumeric chars become
'_'); the 1-based row number is available as {{QSV_ROWNO}}.

If no --prompt/--prompt-file is given, a default prompt that summarizes the selected column/s
is used. The LLM endpoint, model & API key are resolved with this precedence:
  CLI flag > env var (QSV_LLM_BASE_URL / QSV_LLM_MODEL / QSV_LLM_APIKEY) > built-in default
(default base-url: http://localhost:1234/v1 ; default model: openai/gpt-oss-20b).

An API key is required when the base URL is not a localhost endpoint (set --api-key to "NONE"
to suppress sending a key). One HTTP call is made per uncached row, so summarizing large files
can be slow & costly. Results are cached on disk (keyed by base-url, model, max-tokens,
addl-props & the rendered prompt) so repeated rows & re-runs don't re-pay for inference;
use --no-cache to disable & --fresh to force fresh calls that refresh the cache.

  # Summarize the support_ticket column into a new "summary" column using a local LLM:
  qsv apply summarize support_ticket -c summary file.csv

  # Use a custom prompt referencing multiple columns against a cloud provider:
  qsv apply summarize subject,body -c summary --prompt 'Summarize: {{subject}} - {{body}}' -u https://api.openai.com/v1 -m gpt-4o-mini -k $OPENAI_API_KEY file.csv

  # Also capture per-row inference time & token usage in extra columns:
  qsv apply summarize notes -c summary --stats file.csv

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_apply.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#apply

Usage:
qsv apply operations <operations> [options] <column> [<input>]
qsv apply emptyreplace --replacement=<string> [options] <column> [<input>]
qsv apply dynfmt --formatstr=<string> [options] --new-column=<name> [<input>]
qsv apply calcconv --formatstr=<string> [options] --new-column=<name> [<input>]
qsv apply summarize [options] --new-column=<name> <column> [<input>]
qsv apply --help

apply arguments:
    <column>                        The column/s to apply the transformation to.
                                    Note that the <column> argument supports multiple columns
                                    for the operations & emptyreplace subcommands.
                                    See 'qsv select --help' for the format details.

    OPERATIONS subcommand:
        <operations>                The operation/s to apply.
        <column>                    The column/s to apply the operations to.

    EMPTYREPLACE subcommand:
        --replacement=<string>      The string to use to replace empty values.
        <column>                    The column/s to check for emptiness.

    DYNFMT subcommand:
        --formatstr=<string>        The template to use for the dynfmt operation.
                                    See DYNFMT example above for more details.
        --new-column=<name>         Put the generated values in a new column.

    CALCCONV subcommand:
        --formatstr=<string>        The calculation/conversion expression to use.
        --new-column=<name>         Put the calculated/converted values in a new column.

    SUMMARIZE subcommand:
        <column>                    The column/s whose values are summarized by the LLM.
                                    Used to build the default prompt. With a custom prompt
                                    (via the --prompt/--prompt-file options), any column
                                    can be referenced.
        --new-column=<name>         Put the generated summaries in a new column (required).

    <input>                     The input file to read from. If not specified, reads from stdin.

apply options:
    -c, --new-column <name>     Put the transformed values in a new column instead.
    -r, --rename <name>         New name for the transformed column.
    -C, --comparand=<string>    The string to compare against for replace & similarity operations.
                                Also used with numtocurrency operation to specify currency symbol.
    -R, --replacement=<string>  The string to use for the replace & emptyreplace operations.
                                Also used with numtocurrency operation to conversion rate.
    -f, --formatstr=<string>    This option is used by several subcommands:

                                OPERATIONS:
                                  currencytonum
                                    If set to "strict", will require a valid ISO currency symbol,
                                    with the currency symbol at the beginning of the string.
                                    Otherwise, only parse the numeric part of the string and ignore
                                    the currency symbol altogether.
                                    (default: permissive)

                                  numtocurrency
                                    If set to "euro", will format the currency to use "." instead of ","
                                    as separators (e.g. 1.000,00 instead of 1,000.00 )

                                  thousands
                                    The thousands separator policy to use. The available policies are:
                                    comma, dot, space, underscore, hexfour (place a space every four
                                    hex digits) and indiancomma (place a comma every two digits,
                                    except the last three digits). (default: comma)

                                  round
                                    The number of decimal places to round to (default: 3)

                                DYNFMT: the template to use to construct a new column.

    -j, --jobs <arg>            The number of jobs to run in parallel.
                                When not set, the number of jobs is set to the number of CPUs detected.
    -b, --batch <size>          The number of rows per batch to load into memory, before running in parallel.
                                Automatically determined for CSV files with more than 50000 rows.
                                Set to 0 to load all rows in one batch. Set to 1 to force batch optimization
                                even for files with less than 50000 rows.
                                [default: 50000]

SUMMARIZE options:
    -u, --base-url <url>        Base URL of the OpenAI API-compatible endpoint.
                                Precedence: this flag > QSV_LLM_BASE_URL env var > http://localhost:1234/v1
    -m, --model <model>         Model name compatible with the OpenAI API spec.
                                Precedence: this flag > QSV_LLM_MODEL env var > openai/gpt-oss-20b
    -k, --api-key <key>         API key for Bearer token authentication.
                                Precedence: this flag > QSV_LLM_APIKEY env var.
                                Set to "NONE" to suppress sending a key. Required for non-localhost URLs.
    -t, --max-tokens <n>        Maximum number of tokens in the LLM output. Set to 0 to not send a
                                max_tokens limit (automatically used for localhost endpoints).
                                [default: 10000]
    --timeout <secs>            Timeout for each LLM request in seconds (0 = no timeout).
                                [default: 300]
    --addl-props <json>         Additional model properties as a JSON object, e.g.
                                '{"reasoning_effort": "high", "temperature": 0.2}'
    --prompt <template>         MiniJinja prompt template rendered per record. Overrides the
                                default prompt. Reference columns by their safe name.
    --prompt-file <file>        Read the prompt template from a file. Ignored if --prompt is set.
    --rate-limit <secs>         Seconds to sleep between LLM requests to avoid provider rate limits.
                                Accepts fractional seconds (e.g. 0.5). [default: 0]
    --on-error <mode>           What to do when an LLM request fails: "fail" aborts; "skip" writes
                                an "<ERROR: ...>" cell and continues. [default: fail]
    --user-agent <agent>        Custom user agent for LLM requests. Supports variables like $QSV_VERSION.
    --cache-dir <dir>           Directory for the disk cache. [default: ~/.qsv-cache/apply-summarize]
                                The cache TTL defaults to 28 days; set the QSV_DISKCACHE_TTL_SECS env
                                var to change it. A value of 0 disables time-based expiration
                                (entries are cached indefinitely). Use --no-cache to disable caching.
    --no-cache                  Disable the disk cache (one LLM call per row, always).
    --fresh                     Force fresh LLM calls, refreshing any cached values.
    --stats                     Append two extra columns per row alongside --new-column:
                                "<new-column>_elapsed_ms" (inference time in milliseconds) and
                                "<new-column>_tokens" (total tokens used). For cached rows, these
                                report the values captured when the summary was first computed.

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout.
    -n, --no-headers            When set, the first row will not be interpreted
                                as headers.
    -d, --delimiter <arg>       The field delimiter for reading CSV data.
                                Must be a single character. (default: ,)
    -p, --progressbar           Show progress bars. Not valid for stdin.
```
## qsv behead

```text
Drop a CSV file's header.

See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#behead

Usage:
    qsv behead [options] [<input>]
    qsv behead --help

Common options:
    -h, --help             Display this message
    -f, --flexible         Do not validate if the CSV has different number of
                           fields per record, increasing performance.
    -o, --output <file>    Write output to <file> instead of stdout.
```
## qsv blake3

```text
Compute cryptographic hashes of files using blake3.

This command is functionally similar to b3sum, providing fast, parallel blake3 hashing
of one or more files. It supports keyed hashing, key derivation, variable-length output,
and checksum verification. When no file is given, or when "-" is given, reads stdin.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_blake3.rs.
See also https://github.com/dathere/qsv/wiki/Indexing-Compression-Diff#blake3

Usage:
    qsv blake3 [options] [<input>...]
    qsv blake3 --help

blake3 options:
    --keyed              Use the keyed mode, reading the 32-byte key from stdin.
                         When using --keyed, file arguments are required (cannot
                         also read data from stdin).
    --derive-key <CTX>   Use the key derivation mode, with the given context string.
                         Cannot be used with --keyed.
    -l, --length <LEN>   The number of output bytes, before hex encoding.
                         [default: 32]
    --no-mmap            Disable memory mapping. Also disables multithreading.
    --no-names           Omit filenames in the output.
    --raw                Write raw output bytes to stdout, rather than hex.
                         Only a single input is allowed. --no-names is implied.
    --tag                Output checksums in tagged format.
    -c, --check          Read blake3 sums from the input files and check them.
    -j, --jobs <arg>     The number of jobs to run in parallel for hashing.
                         When not set, uses the number of CPUs detected.
                         Set to 1 to disable multithreading.

Common options:
    -h, --help           Display this message
    -o, --output <file>  Write output to <file> instead of stdout.
    -q, --quiet          Skip printing OK for each checked file.
                         Must be used with --check.
```
## qsv cat

```text
Concatenate CSV files by row or by column.

When concatenating by column, the columns will be written in the same order as
the inputs given. The number of rows in the result is always equivalent to
the minimum number of rows across all given CSV data. (This behavior can be
reversed with the '--pad' flag.)

Concatenating by rows can be done in two ways:

'rows' subcommand:
   All CSV data must have the same number of columns (unless --flexible is enabled)
   and in the same order.
   If you need to rearrange the columns or fix the lengths of records, use the
   'select' or 'fixlengths' commands. Also, only the headers of the *first* CSV
   data given are used. Headers in subsequent inputs are ignored. (This behavior
   can be disabled with --no-headers.)

'rowskey' subcommand:
   CSV data can have different numbers of columns and in different orders. All
   columns are written in insertion order. If a column is missing in a row, an
   empty field is written. If a column is missing in the header, an empty field
   is written for all rows.

Examples:

  # Concatenate CSV files by rows:
  qsv cat rows file1.csv file2.csv -o combined.csv

  # Concatenate CSV files by rows, adding a grouping column with the filename:
  qsv cat rowskey --group fname --group-name source_file file1.csv file2.csv -o combined_with_keys.csv

  # Concatenate CSV files by columns:
  qsv cat columns file1.csv file2.csv -o combined_columns.csv

  # Concatenate all CSV files in a directory by rows:
  qsv cat rows path/to/csv_directory -o combined.csv

  # Concatenate all CSV files listed in a .infile-list file by rows:
  qsv cat rows path/to/files_to_combine.infile-list -o combined.csv

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_cat.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#cat

Usage:
    qsv cat rows    [options] [<input>...]
    qsv cat rowskey [options] [<input>...]
    qsv cat columns [options] [<input>...]
    qsv cat --help

cat arguments:
    <input>...              The CSV file(s) to read. Use '-' for standard input.
                            If input is a directory, all files in the directory will
                            be read as input.
                            If the input is a file with a '.infile-list' extension,
                            the file will be read as a list of input files.
                            If the input are snappy-compressed files(s), it will be
                            decompressed automatically.

cat options:
                             COLUMNS OPTION:
    -p, --pad                When concatenating columns, this flag will cause
                             all records to appear. It will pad each row if
                             other CSV data isn't long enough.

                             ROWS OPTION:
    --flexible               When concatenating rows, this flag turns off validation
                             that the input and output CSVs have the same number of columns.
                             This is faster, but may result in invalid CSV data.

                             ROWSKEY OPTIONS:
    -g, --group <grpkind>    When concatenating with rowskey, you can specify a grouping value
                             which will be used as the first column in the output. This is useful
                             when you want to know which file a row came from. Valid values are
                             'fullpath', 'parentdirfname', 'parentdirfstem', 'fname', 'fstem' and 'none'.
                             For a file at /data/2024/jan/sales.csv, 'fullpath' gives
                             '/data/2024/jan/sales.csv', 'parentdirfname' gives 'jan/sales.csv',
                             'parentdirfstem' gives 'jan/sales', 'fname' gives 'sales.csv' and
                             'fstem' gives 'sales'.
                             'fullpath' and the parentdir kinds use the file's real location
                             (symlinks and relative paths resolved), so the result does not
                             depend on how the path was typed. Use a parentdir kind to tell
                             apart same-named files in different directories.
                             For a compressed input, 'fullpath' names the real file
                             (/data/jan/sales.csv.sz, or /data/jan/2024.zip/sales.csv for an entry
                             sales.csv in a zip archive). The other kinds treat it as if unpacked
                             in place, so 'parentdirfname' gives jan/sales.csv and 2024/sales.csv.
                             Piped stdin is named 'stdin.csv' ('<stdin>' for 'fullpath').
                             A new column will be added to the beginning of each row using --group-name.
                             If 'none' is specified, no grouping column will be added.
                             [default: none]
    -N, --group-name <arg>   When concatenating with rowskey, this flag provides the name
                             for the new grouping column. [default: file]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will NOT be interpreted
                           as column names. Note that this has no effect when
                           concatenating columns.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv clean

```text
Removes qsv-generated cache files to reduce clutter and simplify data packaging.

By default, clean removes the three auto-regenerable CACHES qsv writes next to a
source file:

  * <file>.idx                                              (index)
  * <stem>.stats.csv / .stats.weighted.csv / .stats.csv.json
    / .stats.csv.data.jsonl                                 (stats cache)
  * <stem>.freq.csv.data.jsonl                              (frequency cache)

Only files that are VERIFIABLY generated by qsv are removed, so a user file that
merely happens to be named e.g. report.stats.csv is never touched (qsv stats
caches are only removed when their companion .stats.csv.json sidecar is present).

clean is, by default, a DRY-RUN: it only lists what it WOULD remove (and the
bytes that would be reclaimed). Pass --force to actually delete.

User OUTPUTS from schema, validate and moarstats are NOT caches and are only
removed when you ask for them explicitly with --schema / --validate / --moarstats
(or --all).

Examples:
  Preview the caches qsv would remove from the current directory:
    $ qsv clean

  Actually remove them:
    $ qsv clean --force

  Remove only STALE or orphaned caches (source changed, or source is gone),
  recursively, from a specific directory:
    $ qsv clean --stale --recursive --force ./data

  Remove just the caches & outputs associated with one file:
    $ qsv clean --all --force data.csv

For the tests, see https://github.com/dathere/qsv/blob/master/tests/test_clean.rs.

Usage:
    qsv clean [options] [<input>]
    qsv clean --help

clean options:
    --stale            Only remove STALE or ORPHANED caches: a cache whose
                       source file is newer than the cache, or whose source
                       file no longer exists.
    -r, --recursive    Recurse into subdirectories when <input> is a directory.
    -n, --dry-run      Preview only; never delete. Wins over --force if both
                       are given (this is also the default when neither is set).
    -f, --force        Actually delete the files.

  Category selection. When no category flag is given, the three default caches
  (index, stats & frequency) are cleaned:
    --index            Index (.idx) caches. [default category]
    --stats            Stats caches. [default category]
    --frequency        Frequency caches. [default category]
    --schema           schema .schema.json / .pschema.json outputs.
    --validate         validate .valid / .invalid / .validation-errors.tsv outputs.
    --moarstats        moarstats .stats.bivariate[.joined].csv outputs.
    --all              Select every category above.

Common options:
    -h, --help         Display this message
    -q, --quiet        Do not print the per-file / summary report.
```
## qsv clipboard

```text
Provide input from the clipboard or save output to the clipboard.

Note when saving to clipboard on Windows, line breaks may be represented as \r\n (CRLF).
Meanwhile on Linux and macOS, they may be represented as \n (LF).

Examples:
Pipe into qsv stats using qsv clipboard and render it as a table:

  $ qsv clipboard | qsv stats | qsv table

If you want to save the output of a command to the clipboard,
pipe into qsv clipboard using the --save or -s flag:

  $ qsv clipboard | qsv stats | qsv clipboard -s

See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#clipboard

Usage:
    qsv clipboard [options]
    qsv clipboard --help

clip options:
    -s, --save             Save output to clipboard.
Common options:
    -h, --help             Display this message
```
## qsv color

```text
Outputs tabular data as a pretty, colorized table that always fits into the
terminal.

Tabular data formats include CSV and its dialects, Arrow, Avro/IPC, Parquet,
JSON Array & JSONL. Note that non-CSV formats require the "polars" feature.

Requires buffering all tabular data into memory. Therefore, you should use the
'sample' or 'slice' command to trim down large CSV data before formatting
it with this command.

Color is turned off when redirecting or running CI. Set QSV_FORCE_COLOR=1
to override this behavior.

The color theme is detected based on the current terminal background color
if possible. Set QSV_THEME to DARK or LIGHT to skip detection. QSV_TERMWIDTH
can be used to override terminal size.

See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#color

Usage:
    qsv color [options] [<input>]
    qsv color --help

color options:
    -C, --color            Force color on, even in situations where colors
                           would normally be disabled.
    -n, --row-numbers      Show row numbers.
    -t, --title <str>      Add a title row above the headers.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
```
## qsv count

```text
Returns a count of the number of records in the CSV data.

It has three modes of operation:
 1. If a valid index is present, it will use it to lookup the count and
    return instantaneously. (fastest)

 If no index is present, it will read the CSV and count the number
 of records by scanning the file.

   2. If the polars feature is enabled, it will use the multithreaded,
      mem-mapped Polars CSV reader. (faster - not available on qsvlite)

   3. If the polars feature is not enabled, it will use the "regular",
      single-threaded CSV reader.

Note that the count will not include the header row (unless --no-headers is
given).

Examples:

  # Basic count of records in data.csv:
  qsv count data.csv

  # Count records in data.csv without headers:
  qsv count --no-headers data.csv

  # Count records in data.csv with human-readable output:
  qsv count --human-readable data.csv

  # Count records in data.csv with width statistics:
  qsv count --width data.csv

  # Count records in data.csv with width statistics (excluding delimiters):
  qsv count --width-no-delims data.csv

  # Count records in data.csv with width statistics in JSON format:
  qsv count --width --json data.csv

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_count.rs.
See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#count

Usage:
    qsv count [options] [<input>]
    qsv count --help

count options:
    -H, --human-readable   Comma separate counts.

WIDTH OPTIONS:
    --width                Also return the estimated widths of each record.
                           Its an estimate as it doesn't count quotes, and will be an
                           undercount if the record has quoted fields.
                           The count and width are separated by a semicolon. It will
                           return the max, avg, median, min, variance, stddev & MAD widths,
                           separated by hyphens. If --human-readable is set, the widths will
                           be labeled as "max", "avg", "median", "min", "stddev" & "mad"
                           respectively, separated by spaces.
                           Note that this option will require scanning the entire file
                           using the "regular", single-threaded, streaming CSV reader,
                           using the index if available for the count.
                           If the file is very large, it may not be able to compile some
                           stats - particularly avg, variance, stddev & MAD. In this case,
                           it will return 0.0 for those stats.
    --width-no-delims      Same as --width but does not count the delimiters in the width.
    --json                 Output the width stats in JSON format.

WHEN THE POLARS FEATURE IS ENABLED:
    --no-polars            Use the "regular", single-threaded, streaming CSV reader instead
                           of the much faster multithreaded, mem-mapped Polars CSV reader.
                           Use this when you encounter memory issues when counting with the
                           Polars CSV reader. The streaming reader is slower but can read
                           any valid CSV file of any size.


Common options:
    -h, --help             Display this message
    -f, --flexible         Do not validate if the CSV has different number of
                           fields per record, increasing performance when counting
                           without an index.
    -n, --no-headers       When set, the first row will be included in
                           the count.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv datefmt

```text
Formats recognized date fields (19 formats recognized) to a specified date format
using strftime date format specifiers.

For recognized date formats, see
https://github.com/dathere/qsv-dateparser?tab=readme-ov-file#accepted-date-formats

See https://docs.rs/chrono/latest/chrono/format/strftime/ for
accepted date format specifiers for --formatstr.
Defaults to ISO 8601/RFC 3339 format when --formatstr is not specified.
( "%Y-%m-%dT%H:%M:%S%z" - e.g. 2001-07-08T00:34:60.026490+09:30 )

Examples:

  # Format dates in Open Date column to ISO 8601/RFC 3339 format:
  qsv datefmt 'Open Date' file.csv

  # Format multiple date columns in file.csv to ISO 8601/RFC 3339 format:
  qsv datefmt 'Open Date,Modified Date,Closed Date' file.csv

  # Format all columns that end with "_date" case-insensitive in file.csv to ISO 8601/RFC 3339 format:
  qsv datefmt '/(?i)_date$/' file.csv

  # Format dates in OpenDate column using '%Y-%m-%d' format:
  qsv datefmt OpenDate --formatstr '%Y-%m-%d' file.csv

  # Format multiple date columns using '%Y-%m-%d' format:
  qsv datefmt OpenDate,CloseDate,ReopenDate --formatstr '%Y-%m-%d' file.csv

  # Get the week number for OpenDate and store it in the week_number column:
  qsv datefmt OpenDate --formatstr '%V' --new-column week_number file.csv

  # Get the day of the week for several date columns and store it in the corresponding weekday columns:
  qsv datefmt OpenDate,CloseDate --formatstr '%u' --rename Open_weekday,Close_weekday file.csv

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_datefmt.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#datefmt

Usage:
qsv datefmt [--formatstr=<string>] [options] <column> [<input>]
qsv datefmt --help

datefmt arguments:
    <column>                    The column/s to apply the date formats to.
                                Note that the <column> argument supports multiple columns.
                                See 'qsv select --help' for the format details.

    --formatstr=<string>        The date format to use for the datefmt operation.
                                For formats, see
                                https://docs.rs/chrono/latest/chrono/format/strftime/
                                Default to ISO 8601 / RFC 3339 date & time format -
                                "%Y-%m-%dT%H:%M:%S%z" - e.g. 2001-07-08T00:34:60.026490+09:30
                                [default: %+]

    <input>                     The input file to read from. If not specified, reads from stdin.

datefmt options:
    -c, --new-column <name>     Put the transformed values in new column(s) instead of replacing
                                the source column(s). When the selection has multiple columns,
                                pass a comma-separated list of new column names that match the
                                selection count (e.g. --new-column 'open_iso,close_iso' for
                                'OpenDate,CloseDate'). To rename in place instead, use --rename.
    -r, --rename <name>         New name for the transformed column.
    --prefer-dmy                Prefer to parse dates in dmy format. Otherwise, use mdy format.
    --keep-zero-time            If a formatted date ends with "T00:00:00+00:00", keep the time
                                instead of removing it.
    --input-tz=<string>         The timezone to use for the input date if the date does not have
                                timezone specified. The timezone must be a valid IANA timezone name or
                                the string "local" for the local timezone.
                                See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
                                for a list of valid timezone names.
                                [default: UTC]
    --output-tz=<string>        The timezone to use for the output date.
                                The timezone must be a valid IANA timezone name or the string "local".
                                [default: UTC]
    --default-tz=<string>       Fallback timezone consulted only when --input-tz or --output-tz
                                is set to "local" but local-timezone detection fails. Defaults
                                to UTC. Does NOT override the --input-tz / --output-tz defaults —
                                use --utc to force both input and output to UTC.
                                The timezone must be a valid IANA timezone name or the string "local".
    --utc                       Shortcut for --input-tz and --output-tz set to UTC.
    --zulu                      Shortcut for --output-tz set to UTC and --formatstr set to "%Y-%m-%dT%H:%M:%SZ".
    -R, --ts-resolution <res>   The resolution to use when parsing Unix timestamps.
                                Valid values are "sec", "milli", "micro", "nano".
                                [default: sec]
    -j, --jobs <arg>            The number of jobs to run in parallel.
                                When not set, the number of jobs is set to the number of CPUs detected.
    -b, --batch <size>          The number of rows per batch to load into memory, before running in parallel.
                                Automatically determined for CSV files with more than 50000 rows.
                                Set to 0 to load all rows in one batch. Set to 1 to force batch optimization
                                even for files with less than 50000 rows.
                                [default: 50000]

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout.
    -n, --no-headers            When set, the first row will not be interpreted
                                as headers.
    -d, --delimiter <arg>       The field delimiter for reading CSV data.
                                Must be a single character. (default: ,)
    -p, --progressbar           Show progress bars. Not valid for stdin.
```
## qsv dedup

```text
Deduplicates CSV rows.

This requires reading all of the CSV data into memory because because the rows need
to be sorted first.

That is, unless the --sorted option is used to indicate the CSV is already sorted -
typically, with the sort cmd for more sorting options or the extsort cmd for larger
than memory CSV files. This will make dedup run in streaming mode with constant memory.

Either way, the output will not only be deduplicated, it will also be sorted.

A duplicate count will also be sent to <stderr>.

Examples:

  # Deduplicate an unsorted CSV file:
  qsv dedup unsorted.csv -o deduped.csv

  # Deduplicate a sorted CSV file:
  qsv sort unsorted.csv | qsv dedup --sorted -o deduped.csv

  # Deduplicate based on specific columns:
  qsv dedup --select col1,col2 unsorted.csv -o deduped.csv

  # Deduplicate based on numeric comparison of col1 and col2 columns:
  qsv dedup -s col1,col2 --numeric unsorted.csv -o deduped.csv

  # Deduplicate ignoring case of col1 and col2 columns:
  qsv dedup -s col1,col2 --ignore-case unsorted.csv -o deduped.csv

  # Write duplicates to a separate file:
  qsv dedup -s col1,col2 --dupes-output dupes.csv unsorted.csv -o deduped.csv

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_dedup.rs.
See also https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#dedup

Usage:
    qsv dedup [options] [<input>]
    qsv dedup --help

dedup options:
    -s, --select <arg>         Select a subset of columns to dedup.
                               Note that the outputs will remain at the full width
                               of the CSV.
                               See 'qsv select --help' for the format details.
    -N, --numeric              Compare according to string numerical value
    -i, --ignore-case          Compare strings disregarding case.
    --sorted                   The input is already sorted. Do not load the CSV into
                               memory to sort it first. Meant to be used in tandem and
                               after an extsort.
    -D, --dupes-output <file>  Write duplicates to <file>.
    -H, --human-readable       Comma separate duplicate count.
    -j, --jobs <arg>           The number of jobs to run in parallel when sorting
                               an unsorted CSV, before deduping.
                               When not set, the number of jobs is set to the
                               number of CPUs detected.
                               Does not work with --sorted option as its not
                               multithreaded.

Common options:
    -h, --help                 Display this message
    -o, --output <file>        Write output to <file> instead of stdout.
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. That is, it will be sorted with the rest
                               of the rows. Otherwise, the first row will always
                               appear as the header row in the output.
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character. (default: ,)
    -q, --quiet                Do not print duplicate count to stderr.
    --memcheck                 Check if there is enough memory to load the entire
                               CSV into memory using CONSERVATIVE heuristics.
                               Has no effect when --sorted is set, as that path
                               streams the input and never loads it into memory.
```
## qsv denull

```text
Detect null sentinels - literal text like "NULL" or "N/A" standing in for a missing
value - that stop a numeric column from being recognized as numeric.

A cell holding the text "NULL" is a VALUE, not a null. `qsv stats` therefore types
the whole column as String, its nullcount stays 0, and no quartiles are computed.
Everything downstream degrades quietly: `viz smart` drops the column, `schema`
declares it a string, and `describegpt` describes a category that isn't one.

denull scans each column ONCE, with bounded memory, and partitions its values into
those that parse as a finite number and those that don't. A column is CONFIRMED when
every non-numeric value it holds is a known null sentinel and at least two distinct
numeric values remain.

A column is REJECTED - with the reason - when it cannot be promoted anyway: another
value is not a sentinel ("OK"), its numbers carry leading zeros and are really codes
("007"), or it buries the sentinel under more than --max-distinct other non-numeric
values.

Only columns worth acting on are listed: those holding a known sentinel, and those
that are predominantly numeric, whose few odd values are candidates for a sentinel
denull does not know yet - name them with --add-vocab. An ordinary categorical is
not a near miss and is not reported; nor is a free-text column that merely happens
to be unpromotable. Use --all-columns to see everything scanned.

The scan is exhaustive, not sampled: a column is never confirmed on the strength of
the values that happen to sort first. A genuine free-text column disqualifies itself
as soon as it accumulates --max-distinct different non-numeric values, so memory
stays flat. A 434 MB, 86-column file peaks at ~40 MB - the same as a type-inference
pass, and ~19x less than an exhaustive frequency table of every distinct value.

By default denull only REPORTS; it never rewrites your data. Pass --apply to
rewrite it, blanking sentinels ONLY in the columns denull CONFIRMED. A column it
REJECTED is copied through untouched, as is every column it did not scan:

  $ qsv denull --apply data.csv -o clean.csv
  $ qsv stats clean.csv --everything

Cleaning is per-column, which is what a single `qsv replace` pass cannot do: it
takes one regex across all selected columns, so it cannot blank "NULL" in one
column and "-" in another while leaving a literal "-" alone in a third.

Once blanked, `qsv stats` treats those cells as MISSING: it excludes them from mean,
stddev and the quartiles, and counts them in `nullcount` and `sparsity`. Do not reach
for the `--nulls` option of `qsv stats` to "restore" them. That option puts the blanks
back into the denominator while they contribute nothing to the sum, which is the same
as imputing zero. On a column that is 54% sentinel, that pulls the mean from 271 down
to 123 and SHRINKS the reported standard error - more confidence in a worse number.
A well with no recorded casing depth does not have a casing depth of zero.

Note also that `--nulls` reaches only the moment-based statistics - mean, stddev,
variance, cv, sem, geometric_mean, harmonic_mean and n_zero. The order statistics
(median, quartiles, iqr, mad, skewness) ALWAYS ignore blanks, whether or not the flag
is set, so a `--nulls` summary does not agree with itself: on that same column the mean
drops to 123 while the median stays at 200. And because one zero annihilates a product,
geometric_mean collapses to 0 and harmonic_mean to nothing at all.

So `--nulls` is not a general "treat blanks as zero" switch, even for data where an
empty cell genuinely MEANS zero (no events, no charge). If that is your data, and you
want every statistic to see those zeroes, materialize them first and leave the flag
alone:

  $ qsv fill --default 0 -s events data.csv | qsv stats --everything

Statistics over the cleaned column are still complete-case: they describe the rows
that HAVE a value. If a value is missing for a reason correlated with the value
itself, the estimate is biased. denull does not create that bias - before it ran, the
column was a String with no statistics at all - but it does not remove it either. It
makes the missingness visible so you can reason about it.

Numeric sentinels (-999, -9999, 9999) are deliberately NOT detected. They parse as
valid numbers, so no scan can distinguish them from real data - a depth-to-water
reading of -140 ft is an artesian well, not a missing value. Only a human or a
domain-aware model can propose those, and only a human should apply them.

The `sentinels` column lists the sentinel tokens OBSERVED in that column. They are
only safe to remove when the verdict is `confirmed`.

Examples:

  Report every column holding a null sentinel:
    $ qsv denull data.csv

  Restrict to a few columns, and emit JSON for a script to consume:
    $ qsv denull -s HoleDepth,WellDepth,CasingDepth --json data.csv

  Treat the site-specific "no reading" marker as a sentinel too:
    $ qsv denull --add-vocab "no reading,not recorded" data.csv

  Show every scanned column, including those with nothing to report:
    $ qsv denull --all-columns data.csv

  Blank the sentinels in every confirmed column; the report goes to stderr:
    $ qsv denull --apply data.csv -o clean.csv

For the tests, see https://github.com/dathere/qsv/blob/master/tests/test_denull.rs.

Usage:
    qsv denull [options] [<input>]
    qsv denull --help

denull options:
    -s, --select <arg>     Select the columns to scan. See `qsv select --help`
                           for the full selection syntax.
    --vocab <list>         Comma-separated null sentinel vocabulary, REPLACING
                           the built-in list. Matched case-insensitively after
                           trimming surrounding whitespace.
    --add-vocab <list>     Comma-separated tokens to ADD to the built-in list.
                           Use this for site-specific markers.
    --max-distinct <n>     Abandon a column once it holds this many distinct
                           non-numeric values. Guards memory on free-text
                           columns and bounds the report.
                           [default: 16]
    --all-columns          Also report columns with nothing to flag. By default
                           only columns with a verdict are listed.
    --apply                Rewrite the data instead of only reporting it. Blanks
                           the sentinels in every CONFIRMED column and writes the
                           CSV to <output> (or stdout), sending the report to
                           stderr. Rejected and unscanned columns pass through
                           untouched. Needs a file input, and <output> must not
                           be the input file.
    --json                 Emit the report as a JSON array instead of CSV.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write the report here instead of stdout.
    -n, --no-headers       When set, the first row will NOT be interpreted as
                           column names. Columns are named col_1, col_2, etc.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv describegpt

```text
Create a "neuro-symbolic" Data Dictionary and/or infer Description & Tags about a Dataset
using an OpenAI API-compatible Large Language Model (LLM).

It does this by compiling Summary Statistics & a Frequency Distribution of the Dataset,
and then prompting the LLM with detailed, configurable, MiniJinja-templated prompts with
these extended statistical context.

The Data Dictionary is "neuro-symbolic" as it uses a hybrid approach. It's primarily populated
deterministically using Summary Statistics & Frequency Distribution, and only the human-friendly
Label and Description (plus Content Type when --infer-content-type is set) are populated by the
"neural network" LLM using the same statistical context.

CHAT MODE:
You can also use the --prompt option to ask a natural language question about the Dataset.

If the question can be answered by solely using the Dataset's Summary Statistics and
Frequency Distribution data, the LLM will return the answer directly.

CHAT SQL RETRIEVAL-AUGMENTED GENERATION (RAG) SUB-MODE:
If the question cannot be answered using the Dataset's Summary Statistics & Frequency Distribution,
it will first create a Data Dictionary and a small random sample (default: 100 rows) of the Dataset
and provide it to the LLM as additional context to help it generate a SQL query that DETERMINISTICALLY
answers the natural language question.

Two SQL dialects are currently supported - DuckDB (highly recommended) & Polars. If the
QSV_DUCKDB_PATH environment variable is set to the absolute path of the DuckDB binary,
DuckDB will be used to answer the question. Otherwise, if the "polars" feature is enabled,
Polars SQL will be used.

If neither DuckDB nor Polars is available, the SQL query will be returned in a Markdown code block,
along with the reasoning behind the query.

Even in "SQL RAG" mode, though the SQL query is guaranteed to be deterministic, the query itself
may not be correct. In the event of a SQL query execution failure, run the same --prompt with
the --fresh option to request the LLM to generate a new SQL query.

When using DuckDB, all loaded DuckDB extensions will be sent as additional context to the LLM to let
it know what functions (even UDFs!) it can use in the SQL queries it generates. If you want a
specific function or technique to be used in the SQL query, mention it in the prompt.

SUPPORTED MODELS & LLM PROVIDERS:
OpenAI's open-weights gpt-oss model (both 20b and 120b variants) was used during development &
is recommended for most use cases.
It was also tested with OpenAI, TogetherAI, OpenRouter and Google Gemini cloud providers.
For Gemini, use the base URL "https://generativelanguage.googleapis.com/v1beta/openai".
Local LLMs tested include Ollama, Jan and LM Studio.

NOTE: LLMs are prone to inaccurate information being produced. Verify output results before using them.

CACHING:
As LLM inferencing takes time and can be expensive, describegpt caches the LLM inferencing results
in a either a disk cache (default) or a Redis cache. It does so by calculating the BLAKE3 hash of the
input file and using it as the primary cache key along with the prompt type, model and every flag that
influences the rendered prompt (including prompt-file, context-file, language, tag-vocab, num-tags,
enum-threshold, infer-content-type, sample-size, fewshot-examples, the QSV_DUCKDB_PATH toggle and the
generated Data Dictionary), so changing any of them produces a fresh LLM call rather than stale cached output.

The default disk cache is stored in the ~/.qsv-cache/describegpt directory with a default TTL of 28 days
and cache hits NOT refreshing an existing cached value's TTL.
Adjust the QSV_DISKCACHE_TTL_SECS & QSV_DISKCACHE_TTL_REFRESH env vars to change disk cache settings.
A QSV_DISKCACHE_TTL_SECS of 0 disables time-based expiration (entries are cached indefinitely).

Alternatively a Redis cache can be used instead of the disk cache. This is especially useful if you want
to share the cache across the network with other users or computers.
The Redis cache is stored in database 3 by default with a TTL of 28 days and cache hits NOT refreshing
an existing cached value's TTL. Adjust the QSV_DG_REDIS_CONNSTR, QSV_REDIS_MAX_POOL_SIZE,
QSV_REDIS_TTL_SECS & QSV_REDIS_TTL_REFRESH env vars to change Redis cache settings.
A QSV_REDIS_TTL_SECS of 0 disables expiration (entries are cached indefinitely).

Examples:

  # Generate a Data Dictionary, Description & Tags of data.csv using the bundled defaults
  # (a local LLM on http://localhost:1234/v1 running the google/gemma-4-26b-a4b model)
  qsv describegpt data.csv --all

  # Same, but against OpenAI's cloud API instead of a local LLM
  # (replace <API_KEY> with your OpenAI API key)
  qsv describegpt data.csv --base-url https://api.openai.com/v1 --api-key <API_KEY> --model openai/gpt-oss-20b --all

  # Generate a Data Dictionary of data.csv using the DeepSeek R1:14b model on a local Ollama instance
  qsv describegpt data.csv -u http://localhost:11434/v1 --model deepseek-r1:14b --dictionary

  # Generate a Data Dictionary that also infers a semantic Content Type for each field
  # (e.g. email, city, latitude) so the dictionary can later drive synthetic data generation
  qsv describegpt data.csv --dictionary --infer-content-type

  # Ask questions about the sample NYC 311 dataset using LM Studio with the default gemma-4-26b-a4b model.
  # Questions that can be answered using the Summary Statistics & Frequency Distribution of the dataset.
  qsv describegpt NYC_311.csv --prompt "What is the most common complaint?"

  # Ask detailed natural language questions that require SQL queries and auto-invoke SQL RAG mode
  # Generate a DuckDB SQL query to answer the question
  QSV_DUCKDB_PATH=/path/to/duckdb \
  qsv describegpt NYC_311.csv -p "What's the breakdown of complaint types by borough descending order?"

  # Prompt requires a natural language query. Convert query to SQL using the LLM and save results to
  # a file with the --sql-results option.  If generated SQL query runs successfully,
  # the file is "results.csv". Otherwise, it is "results.sql".
  qsv describegpt NYC_311.csv -p "Aggregate complaint types by community board" --sql-results results

  # Cache Dictionary, Description & Tags inference results using the Redis cache instead of the disk cache
  qsv describegpt data.csv --all --redis-cache

  # Get fresh Description & Tags inference results from the LLM and refresh disk cache entries for both
  qsv describegpt data.csv --description --tags --fresh

  # Get fresh inference results from the LLM and refresh the Redis cache entries for all three
  qsv describegpt data.csv --all --redis-cache --fresh

  # Forget a cached response for data.csv's data dictionary if it exists and then exit
  qsv describegpt data.csv --dictionary --forget

  # Flush/Remove ALL cached entries in the disk cache
  qsv describegpt --flush-cache

  # Flush/Remove ALL cached entries in the Redis cache
  qsv describegpt --redis-cache --flush-cache

  # Generate Data Dictionary but exclude ID columns from frequency analysis to reduce overhead
  qsv describegpt data.csv --dictionary --freq-options "--select '!id,!uuid' --limit 20"

  # Generate Data Dictionary, Description & Tags but reduce frequency context
  # by showing only top 5 values per field
  qsv describegpt data.csv --all --freq-options "--limit 5"

  # Generate Description using weighted frequencies with ascending sort
  qsv describegpt data.csv --description --freq-options "--limit 50 --asc --weight count_column"

  # Generate a Data Dictionary, Description & Tags using a previously compiled stats CSV file and
  # frequency CSV file instead of running the stats and frequency commands
  qsv describegpt data.csv --all --stats-options "file:my_stats.csv" --freq-options "file:my_freq.csv"

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_describegpt.rs.

For more detailed info on how describegpt works and how to prepare a prompt file,
see https://github.com/dathere/qsv/blob/master/docs/Describegpt.md and
https://github.com/dathere/qsv/wiki/AI-and-Documentation#describegpt

Usage:
    qsv describegpt [options] [<input>]
    qsv describegpt --prepare-context [options] [<input>]
    qsv describegpt --process-response [options] [<input>]
    qsv describegpt (--redis-cache) (--flush-cache)
    qsv describegpt --help

describegpt options:
                           DATA ANALYSIS/INFERENCING OPTIONS:
    --dictionary           Create a Data Dictionary using a hybrid "neuro-symbolic" pipeline - i.e.
                           the Dictionary is populated deterministically using Summary Statistics and
                           Frequency Distribution data, and only the human-friendly Label and Description
                           (and Content Type when --infer-content-type is set) are populated by the LLM
                           using the same statistical context.
                           The dataset's content language is also auto-detected locally (using
                           whatlang, not the LLM) from sampled values of its text columns,
                           and emitted as detected_language, detected_language_code (ISO 639-3) and
                           detected_language_confidence in the JSON dictionary (top-level) and JSON
                           Schema ("x-qsv" object) outputs. A language is only recorded when the
                           full sample AND each of 3 disjoint sub-samples independently agree on
                           it - text genuinely written in one language is stable across its own
                           sub-samples, while a table of proper nouns (city, country and person
                           names) is not. The confidence is reported but does not decide, as it
                           measures the margin between the top two candidate languages rather
                           than whether the text is in either of them. The fields are omitted
                           when the sub-samples disagree, and also when an explicit language is
                           given with the --language option. When a language IS recorded, the LLM
                           is also asked to generate its output (Labels, Descriptions, Tags and
                           the dataset Description) in it.
                           The Dictionary is a DRAFT for a human to review. The deterministic half
                           is reproducible, but the LLM half is not: inferring twice over the same
                           data can return different Labels, and (under --infer-content-type)
                           different roles and concepts. So save it, review it, correct it, and
                           keep the corrected copy - that file, not the model, is what makes a
                           later run reproducible. "qsv viz smart --dictionary infer" builds this
                           same dictionary and does exactly that, saving it beside the input as
                           <stem>.schema.json and reusing it on every later run.
    --description          Infer a general Description of the dataset based on detailed statistical context.
                           An Attribution signature is embedded in the Description.
    --tags                 Infer Tags that categorize the dataset based on detailed statistical context.
                           Useful for grouping datasets and filtering.
    -A, --all              Shortcut for --dictionary --description --tags.

                           DICTIONARY OPTIONS:
    --num-examples <n>     The number of Example values to include in the dictionary.
                           [default: 5]
    --truncate-str <n>     The maximum length of an Example value in the dictionary.
                           An ellipsis is appended to the truncated value.
                           If zero, no truncation is performed.
                           Bounds the prompt sent to the LLM, and applies to the
                           csv/json/semantic-md dictionary output. The jsonschema
                           output is machine-facing, so it always carries the full,
                           untruncated Example values.
                           [default: 25]
    --infer-content-type   Also have the LLM classify each field's semantic "Content Type", mapped to a
                           curated, documented vocabulary (e.g. email, city, category, name, credit card, etc.)
                           see https://github.com/dathere/qsv/blob/master/src/cmd/synthesize/faker_map.rs.
                           Adds a "Content Type" column/field to the Data Dictionary output.
                           Fields where cardinality equals the row count (i.e. every row has a distinct
                           non-null value - primary keys, surrogate keys, sequence numbers) are
                           deterministically classified as "unique_id", overriding any token the LLM
                           returned for that field. Float fields are exempt: a full-precision
                           measurement (a price, a coordinate) is all-unique without being a key.
                           For Date/DateTime fields, the LLM also infers the column's strftime date
                           format (e.g. "date:%m/%d/%Y"); the Markdown, JSON & JSON Schema dictionaries
                           then render Min/Max AND Examples in that inferred format so they match how
                           the dates actually appear in the data, instead of qsv's normalized form.
                           (TSV output keeps Min/Max & Examples in qsv's raw normalized form.)
                           For a CONTINUOUS numeric measure on a canonical scale (a percentage, a
                           0-1 ratio/probability, a bounded index), the LLM also proposes an
                           "x-qsv.gauge_range" [min, max]; qsv keeps it only when the field is a
                           numeric measure AND the observed data lies within it, so that a
                           "viz smart" dictionary-driven Data Schematic draws that KPI tile as a GAUGE.
                           (A KPI "vs target" delta uses "x-qsv.target", which is a GOAL you
                           hand-author - never inferred.)
                           For a MONETARY measure the LLM also proposes an "x-qsv.currency": the
                           ISO-4217 alpha-3 code (e.g. "USD") the amounts are denominated in.
                           Codes are validated against the ISO register, and qsv keeps one only
                           when the field is a numeric measure that reads as money, so a currency
                           on a count or on the column that NAMES the currency (that column is a
                           "currency_code" dimension) is dropped. Money columns are also tagged
                           with the "money" content type and the "measure.money" concept.
                           "qsv viz smart --dictionary" reads the code to prefix that column's
                           KPI tile with the currency's symbol.
                           For a NON-MONETARY numeric measure the LLM also proposes an
                           "x-qsv.unit": the UCUM code for the physical unit the values are
                           expressed in ("Cel", "[degF]", "km", "kg", "kW.h", "m/s", "%", ...).
                           UCUM (https://ucum.org/ucum) is the unit standard behind FHIR/HL7 and
                           what schema.org's unitCode is usually mapped from, so the annotation is
                           machine-parseable rather than free text. Codes are validated against a
                           curated subset of a few dozen common units - qsv is not a UCUM parser,
                           and an off-table code is dropped rather than half-honored. qsv keeps one
                           only when the field is a numeric measure that is NOT already money: for
                           money the "x-qsv.currency" above IS the unit, so a field never carries
                           both. Unlike "--denominator-unit", this unit never CONVERTS a value -
                           it only labels one - which is why it is proposed-and-verified rather
                           than declare-only.
                           When the dictionary carries exactly ONE "measure.population" field
                           (a count of people or households IN a region that another column
                           names), qsv DERIVES an "x-qsv.denominator" of {"column": "<that
                           field>"} on every region column able to hold it constantly. A
                           dictionary-driven "qsv viz smart" Data Schematic then charts a
                           PER-CAPITA rate map beside the raw count map, with no hand-edited
                           sidecar and no Census network fetch for a number the file already
                           carries. This one is DERIVED, not proposed: the LLM's only job is
                           tagging the population field. Two population fields are an ambiguity
                           qsv refuses rather than guesses at, and an explicit denominator flag
                           still outranks the hint. "measure.area" is a sibling concept the LLM
                           may tag, but qsv does not derive an area denominator from it yet - an
                           area divisor is unreadable without its unit.
                           For a numeric measure the LLM also proposes an "x-qsv.geo_level": the
                           AREAL unit its values are measured over ("geo.state" on a state
                           population), which is a different question from the field's own
                           "concept" ("measure.population" - what the values ARE, not the area
                           each covers). Only areal "geo." tokens are accepted; a latitude, a
                           street address, a timezone or a gazetteer id points at a spot rather
                           than bounding a region, so none of them can be a level. It is kept
                           only on a numeric measure, and it is never emitted on the field
                           itself: qsv copies the level of the field it DERIVED a denominator
                           from onto that hint, as {"column": "<field>", "level": "<token>"}.
                           This is what lets a consumer reject a denominator declared from a
                           COARSER geography than the region it is charted against - county
                           counts over state populations is a confidently wrong rate map, and no
                           amount of counting distinct values can tell it from a correct one.
                           The LLM also infers dataset-level INTER-COLUMN RELATIONSHIPS, emitted
                           as a "relationships" array (top-level in the JSON dictionary, and in
                           the dataset-level "x-qsv" object of the JSON Schema one). Each entry
                           has a "kind" of "joint", "ordered", "correlated" or "pipeline", plus a
                           "members" list of the field names involved.
                           A "pipeline" is a process whose stages narrow monotonically - planned
                           to committed to spent, impressions to clicks to conversions. Its stages
                           may be separate COLUMNS (listed in "members", upstream first - the
                           opposite direction from "ordered", which ascends) or the VALUES of one
                           category column (via "stage_column", an ordered "stages" list, and an
                           optional "value_column" to sum). "qsv viz smart --dictionary" reads
                           these to draw its pipeline funnel panel; edit them in the saved schema
                           to correct or add one.
    --infer-null-values    Also have the LLM propose each field's null sentinels - literal values
                           that stand in for "missing" (e.g. NULL, N/A, -999, 9999-12-31).
                           Emitted into the JSON Schema dictionary's per-property "x-qsv" object,
                           split into two lists that carry different warranties.
                           * "null_values" - proposed by the LLM AND independently confirmed by
                             qsv to occur as a literal value in that String column. Every observed
                             casing is listed.
                           * "null_candidates" - proposed by the LLM but NOT confirmable by any
                             scan; numeric/date placeholders that parse as valid values of the
                             column's own type (-999 is a legal integer), or tokens never seen in
                             the data. Each carries "confirm_required": true.
                           A proposal that is IMPOSSIBLE is dropped rather than reported: a
                           non-numeric token in a numeric column (no cell could hold it, or the
                           column would not have typed as numeric), and an echo of the null
                           placeholder the Frequency Distribution displays for cells qsv already
                           counts as empty.
                           A confirmed "null_values" entry means only that the literal is PRESENT
                           in the column; the judgment that it MEANS "missing" remains the LLM's.
                           This complements "qsv denull", which reports a narrower set - only the
                           columns that would promote to a numeric type once their sentinels are
                           blanked. A purely categorical column (status = ok/pending/NULL) is
                           outside denull's remit.
                           Sentinels are REPORTED, never applied - qsv does not modify your data
                           on an LLM's say-so. Only "qsv denull --apply" masks values, and only in
                           the columns it independently confirmed.
                           Only rendered by "--format JSONSchema"; the other formats ignore them.
    --two-pass             Run a second LLM call that takes the full first-pass Data Dictionary
                           as JSON context and refines each field's Label, Description and
                           (when --infer-content-type is set) Content Type using cross-field
                           awareness. The LLM can then relate fields that belong together
                           (e.g. street_no + street_name + city + state + zip describing a single
                           mailing address; first_name + last_name naming a single person;
                           lat + lng forming a coordinate pair). The refined dictionary becomes the
                           emitted output and is also what downstream Description, Tags and Prompt
                           inference phases see as dictionary context.
                           Roughly doubles dictionary LLM cost and latency, so opt-in.
                           Most useful when combined with --infer-content-type.
                           Allowed with the --dictionary, --all and --prompt inference flags.
                           Mutually exclusive with --prepare-context and --process-response
                           (MCP sampling is single-turn per inference phase).
    --addl-cols            Add additional columns to the dictionary from the Summary Statistics.
  --addl-cols-list <list>  A comma-separated list of additional stats columns to add to the dictionary.
                           The columns must be present in the Summary Statistics.
                           If the columns are not present in the Summary Statistics or already in the
                           dictionary, they will be ignored.
                           These values are case-insensitive and automatically set the --addl-cols option to true.
                           "everything" can be used to add all 45 "available" statistics columns.
                           You can adjust the available columns with --stats-options.
                           "everything!" automatically sets --stats-options to compute "all" 51 supported stats.
                           The 6 addl cols are the mode/s & antimode/s stats with each having counts & occurrences.
                           "moar" gets you even moar stats, with detailed outliers info.
                           "moar!" gets you even moar with --advanced stats (Kurtosis, Gini Coefficient & Shannon Entropy)
                           [default: sort_order, sortiness, mean, median, mad, stddev, variance, cv]

                           TAG OPTIONS:
    --num-tags <n>         The maximum number of tags to infer when the --tags option is used.
                           Maximum allowed value is 50.
                           [default: 10]
    --tag-vocab <file>     The CSV file containing the tag vocabulary to use for inferring tags.
                           If no tag vocabulary file is provided, the model will use free-form tags.
                           Supports local files, remote URLs (http/https), CKAN resources (ckan://),
                           and dathere:// scheme. Remote resources are cached locally.
                           The CSV file must have two columns with headers: first column is the tag,
                           second column is the description. Note that qsvlite only supports local files.
    --cache-dir <dir>      The directory to use for caching downloaded tag vocabulary resources.
                           If the directory does not exist, qsv will attempt to create it.
                           If the QSV_CACHE_DIR envvar is set, it will be used instead.
                           [default: ~/.qsv-cache]
    --ckan-api <url>       The URL of the CKAN API to use for downloading tag vocabulary resources
                           with the "ckan://" scheme.
                           If the QSV_CKAN_API envvar is set, it will be used instead.
                           [default: https://data.dathere.com/api/3/action]
    --ckan-token <token>   The CKAN API token to use. Only required if downloading private resources.
                           If the QSV_CKAN_TOKEN envvar is set, it will be used instead.

                           STATS/FREQUENCY OPTIONS:
    --stats-options <arg>  Options for the stats command used to generate summary statistics.
                           If it starts with "file:" prefix, the statistics are read from the
                           specified CSV file instead of running the stats command.
                           e.g. "file:my_custom_stats.csv"
                           [default: --infer-dates --infer-boolean --mad --quartiles --percentiles --force --stats-jsonl]
    --freq-options <arg>   Options for the frequency command used to generate frequency distributions.
                           You can use this to exclude certain variable types from frequency analysis
                           (e.g., --select '!id,!uuid'), limit results differently per use case, or
                           control output format. If --limit is specified here, it takes precedence
                           over --enum-threshold.
                           If it starts with "file:" prefix, the frequency data is read from the
                           specified CSV file instead of running the frequency command.
                           e.g. "file:my_custom_frequency.csv"
                           A "file:"-backed CSV is assumed to use frequency's default "(NULL)"
                           null text; a custom --null-text in a file-supplied CSV is not
                           recognized when validating inferred date/datetime formats.
                           [default: --rank-strategy dense]
    --enum-threshold <n>   The threshold for compiling Enumerations with the frequency command
                           before bucketing other unique values into the "Other" category.
                           This is a convenience shortcut for --freq-options --limit <n>.
                           If --freq-options contains --limit, this flag is ignored.
                           [default: 10]

                           CUSTOM PROMPT OPTIONS:
    -p, --prompt <prompt>  Custom prompt to answer questions about the dataset.
                           The prompt will be answered based on the dataset's Summary Statistics,
                           Frequency data & Data Dictionary. If the prompt CANNOT be answered by looking
                           at these metadata, a SQL query will be generated to answer the question.
                           If the "polars" or the "QSV_DUCKDB_PATH" environment variable is set
                           & the `--sql-results` option is used, the SQL query will be automatically
                           executed and its results returned.
                           Otherwise, the SQL query will be returned along with the reasoning behind it.
                           If it starts with "file:" prefix, the prompt is read from the file specified.
                           e.g. "file:my_long_prompt.txt"
    --sql-results <file>   The file to save the SQL query results to.
                           Only valid if the --prompt option is used & the "polars" or the
                           "QSV_DUCKDB_PATH" environment variable is set.
                           If the SQL query executes successfully, the results will be saved with a
                           ".csv" extension. Otherwise, it will be saved with a ".sql" extension so
                           the user can inspect why it failed and modify it.
    --prompt-file <file>   The configurable TOML file containing prompts to use for inferencing.
                           If no file is provided, default prompts will be used.
                           The prompt file uses the MiniJinja template engine (https://docs.rs/minijinja)
                           See https://github.com/dathere/qsv/blob/master/resources/describegpt_defaults.toml
    --context-file <file>  Path to a file with additional context about the dataset - e.g.
                           variable/code labels, provenance & domain notes - injected into the
                           prompts as the {{ context }} MiniJinja variable. The file TYPE is
                           sniffed from its contents (not its extension). Supported types:
                           plain text, Markdown, CSV, Excel/ODS spreadsheets (extracted to CSV),
                           and PDF or image files (JPEG/PNG/WebP/GIF) sent to the LLM as a
                           multimodal attachment (needs a multimodal model & endpoint; max ~32 MB).
                           Word/PowerPoint (docx/pptx) are NOT supported - convert to PDF or text.
                           By default qsv injects this context into the USER message; custom prompt
                           file templates may reference {{ context }} anywhere to place it instead.
                           If the option is unset or the file is empty, {{ context }} renders as an
                           empty string and the prompts are unaffected. The file's contents are part
                           of the cache key, so editing it produces a fresh LLM call.
                           Name any column you ADDED to the source data (a lookup, join or
                           computed field) and how it was made. Otherwise its gaps read as
                           defects of the source: e.g. "County_FIPS and County_Name are not in
                           the source file; they were added by looking up each ZIP code, and a
                           blank means the ZIP had no match". With such a line, descriptions
                           call those blanks enrichment gaps rather than missing source data.
    --markdown-template <file>  TOML file with MiniJinja templates for Markdown output. The TOML
                           contains four wrapper templates - one per inference kind:
                           dictionary_md_template, description_md_template, tags_md_template
                           and custom_prompt_md_template - plus a dictionary_md_body_template
                           that drives the per-field dictionary table that fills the
                           dictionary wrapper's {{ llm_response }}.
                           All template fields are optional; any omitted field falls back to
                           the embedded default, so a minimal TOML can override just the
                           templates you want to change.
                           Custom MiniJinja filters (pipe_escape, br_replace, human_count,
                           dict_cell, humanize_examples) and template variables are documented
                           inline in the default TOML referenced below.
                           If no file is provided, built-in defaults are used (matching legacy output).
                           See https://github.com/dathere/qsv/blob/master/resources/describegpt_md_defaults.toml
    --sample-size <n>      The number of rows to randomly sample from the input file for the sample data.
                           Uses the INDEXED sampling method with the qsv sample command.
                           [default: 100]
    --fewshot-examples     By default, few-shot examples are NOT included in the LLM prompt when
                           generating SQL queries. When this option is set, few-shot examples in the default
                           prompt file are included.
                           Though this will increase the quality of the generated SQL, it comes at
                           a cost - increased LLM API call cost in terms of tokens and execution time.
                           See https://en.wikipedia.org/wiki/Prompt_engineering for more info.
    --session <name>       Enable stateful session mode for iterative SQL RAG refinement.
                           The session name is the file path of the markdown file where session messages
                           will be stored. When used with --prompt, subsequent queries in the same session
                           will refine the baseline SQL query. SQL query results (10-row sample) and errors
                           are automatically included in subsequent messages for context.
    --session-len <n>      Maximum number of recent messages to keep in session context before
                           summarizing older messages. Only used when --session is specified.
                           [default: 10]
    --no-score-sql         Disable scoresql validation of generated SQL queries before execution.
                           By default, when --prompt generates a SQL query and --sql-results is set,
                           the query is scored and iteratively improved if below threshold.
    --score-threshold <n>  Minimum scoresql score for a SQL query to be accepted.
                           Typical range is 0-100; values >100 will always trigger retries
                           and the below-threshold warning.
                           [default: 50]
    --score-max-retries <n>  Max LLM re-prompts to improve a low-scoring SQL query.
                           [default: 3]

                           LLM API OPTIONS:
    -u, --base-url <url>   The LLM API URL. Supports APIs & local LLMs compatible with
                           the OpenAI API specification. Some common base URLs:
                             OpenAI: https://api.openai.com/v1
                             Gemini: https://generativelanguage.googleapis.com/v1beta/openai
                             TogetherAI: https://api.together.ai/v1
                           Local LLMs:
                             Ollama: http://localhost:11434/v1
                             Jan: https://localhost:1337/v1
                             LM Studio: http://localhost:1234/v1
                           Precedence: explicit CLI flag > QSV_LLM_BASE_URL env var > prompt file
                           base_url > built-in default (http://localhost:1234/v1).
                           NOTE: no docopt default — the absence of an explicit flag is what
                           lets the env var and the prompt file actually take effect.
    -m, --model <model>    The model to use for inferencing. This model must be compatible with OpenAI API spec.
                           Works with both cloud LLM providers and local LLMs.
                           Tested open weights models include OpenAI's gpt-oss-20b and gpt-oss-120b;
                           Google's Gemma family of open models; and Mistral's Magistral reasoning models.
                           Precedence: explicit CLI flag > QSV_LLM_MODEL env var > prompt file model
                           > built-in default (google/gemma-4-26b-a4b). No docopt default — same
                           rationale as --base-url above.
    --language <lang>      The output language/dialect/tone to use for the response. (e.g., "Spanish", "French",
                           "Hindi", "Mandarin", "Italian", "Castilian", "Franglais", "Taglish", "Pig Latin",
                           "Valley Girl", "Pirate", "Shakespearean English", "Chavacano", "Gen Z", "Yoda", etc.)
                           If set to a string, that language/dialect is ALWAYS used for the response,
                           overriding auto-detection AND suppressing the recorded detection entirely,
                           so the detected_language fields are omitted. If set to a float (0.0 to 1.0),
                           it specifies a minimum confidence floor. If not set, inference mode applies
                           no confidence floor (see below) and chat mode uses 80%.

                             INFERENCE MODE (--dictionary, --description & --tags) DETECTION:
                             The dataset's content language is auto-detected locally (using whatlang,
                             not the LLM) from sampled values of its text columns. A language is only
                             adopted when the full sample AND each of 3 disjoint sub-samples agree on
                             it; otherwise the model's default language is used. Confidence is NOT the
                             gate - it measures the margin between the top two candidates, not whether
                             the text is in either - so a float here is only an ADDITIONAL floor that
                             can further reject, never accept.

                             CHAT MODE (--prompt) DETECTION:
                             The language of the prompt itself is auto-detected, gated on an 80%
                             confidence threshold (a prompt is free-flowing prose, whatlang's actual
                             design domain, so the sub-sample agreement test does not apply). If the
                             threshold is met, it will specify the detected language in its response.
                             Note that LLMs often detect the language independently, but will often respond
                             in the model's default language. This option is here to ensure responses are
                             in the detected language of the prompt.
    --tour-audience <text>  Also write an "x-qsv.tour" guided-tour narration for the qsv
                           viz smart Data Schematic into the generated dictionary, addressed
                           to the given audience (e.g. "Explain like I'm 10", "a board of
                           directors", "data journalists"). Only meaningful with --dictionary
                           when the format is jsonschema; ignored otherwise. The audience
                           shapes ONLY the tour prose - field labels & descriptions keep
                           their normal register. "qsv viz smart --dictionary infer" forwards
                           this flag automatically (defaulting to "Explain like I'm 10").
    --addl-props <json>    Additional model properties to pass to the LLM chat/completion API.
                           Various models support different properties beyond the standard ones.
                           For instance, gpt-oss-20b supports the "reasoning_effort" property.
                           e.g. to set the "reasoning_effort" property to "high" & "temperature"
                           to 0.5, use '{"reasoning_effort": "high", "temperature": 0.5}'
    -k, --api-key <key>    The API key to use. If set, takes precedence over the QSV_LLM_APIKEY envvar.
                           Required when the base URL is not localhost.
                           Set to NONE to suppress sending the API key.
    -t, --max-tokens <n>   Limits the number of generated tokens in the output.
                           Set to 0 to disable token limits.
                           If the --base-url is localhost, indicating a local LLM,
                           the default is automatically set to 0.
                           [default: 10000]
    --timeout <secs>       Timeout for completions in seconds. If 0, no timeout is used.
                           Defaults to 300 if not set. If the --base-url is localhost,
                           indicating a local LLM, the timeout is automatically disabled
                           unless you set --timeout (or the QSV_TIMEOUT envvar) explicitly.
    --user-agent <agent>   Specify custom user agent. It supports the following variables -
                           $QSV_VERSION, $QSV_TARGET, $QSV_BIN_NAME, $QSV_KIND and $QSV_COMMAND.
                           Try to follow the syntax here -
                           https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
  --export-prompt <file>   Export the default prompts to the specified file that
                           can be used with the --prompt-file option.
                           The file will be saved with a .toml extension.
                           If the file already exists, it will be overwritten.
                           It will exit after exporting the prompts.

                           CACHING OPTIONS:
    --no-cache             Disable default disk cache.
  --disk-cache-dir <dir>   The directory to store the disk cache. Note that if the directory does not exist,
                           it will be created. If the directory exists, it will be used as is, and will not
                           be flushed. This option allows you to maintain several disk caches for different
                           describegpt jobs (e.g. one for a data portal, another for internal data exchange).
                           [default: ~/.qsv-cache/describegpt]
    --redis-cache          Use Redis instead of the default disk cache to cache LLM completions.
                           It connects to "redis://127.0.0.1:6379/3" by default, with a connection pool
                           size of 20, with a TTL of 28 days, and cache hits NOT refreshing an existing
                           cached value's TTL.
                           This option automatically disables the disk cache.
    --fresh                Send a fresh request to the LLM API, refreshing a cached response if it exists.
                           When a --prompt SQL query fails, you can also use this option to request the
                           LLM to generate a new SQL query.
    --forget               Remove the cached LLM answers of the selected phases (all
                           phases when none is selected) and then exit, without calling
                           the LLM. Pass the other options of the run whose answers
                           you are forgetting (model, language, tag options and so on),
                           since they are part of the cache key. A short model name
                           (e.g. gpt-oss-20b) is completed from the LLM server's model
                           list, as a run completes it; when the server cannot be
                           reached, the name is used as given, so pass the full one.
                           A Description, Tags or Prompt answer cached with a
                           dictionary is found only while that dictionary's answer is
                           still cached.
    --flush-cache          Flush the current cache entries on startup.
                           WARNING: This operation is irreversible.

                           MCP SAMPLING OPTIONS:
    --prepare-context      Output the prompt context as JSON to stdout without calling the LLM.
                           JSON includes system/user prompts, cache state, and analysis results
                           for each inference phase. Useful for inspecting prompts or piping to
                           custom LLM integrations. Used by the MCP server for sampling mode.
    --process-response     Process LLM responses provided as JSON via stdin. Takes the output
                           format from --prepare-context with LLM responses filled in, and
                           produces the final output (dictionary, description, tags, or prompt
                           results). Used by the MCP server for sampling mode.

Common options:
    -h, --help             Display this message
    --format <format>      Output format: Markdown, TSV, JSON, TOON, JSONSchema, SemanticMd, or OKF.
                           TOON is a compact, human-readable encoding of the JSON data model for LLM prompts.
                           Output conforms to the latest TOON v4 spec.
                           See https://toonformat.dev/ & https://toonformat.dev/guide/whats-new-in-v4.html
                           JSONSchema emits the Data Dictionary as a JSON Schema (draft 2020-12)
                           document, enriched with LLM-inferred Label, Description and Content Type
                           (the latter only when the infer-content-type flag is set). qsv- and LLM-
                           specific metadata not modeled by the JSON Schema spec (cardinality,
                           null_count, weighted example counts, content_type, null_values,
                           null_candidates, addl stats columns)
                           is preserved via a single x-qsv annotation object per property; unknown
                           keywords are ignored by validators per the 2020-12 spec.
                           The JSONSchema format requires the dictionary inference phase
                           (the dictionary or all flag). The description inference, when also run,
                           becomes the schema's top-level description; tags, when also run, are
                           embedded at x-qsv.tags. The prompt inference is not supported.
                           SemanticMd emits the Data Dictionary as a Semantic Markdown document
                           (https://semanticmd.org/) - human-readable markdown with light,
                           agent-parseable conventions that a companion converter turns into JSON.
                           It enriches each column with a catalog-wide Concept ID (for cross-dataset
                           join discovery), an analytical Role (dimension/measure/identifier/timestamp),
                           join keys & cardinality, data-quality flags, and a richer per-column
                           statistics block; it also emits a dataset grain and a temporal/spatial
                           envelope.
                           To populate Concept/Role/grain, SemanticMd implies --infer-content-type.
                           Like JSONSchema, it requires the dictionary inference phase (the
                           dictionary or all flag). The description inference, when also run, becomes
                           the '# Dataset' description; tags, when also run, are embedded in the
                           document frontmatter. The prompt inference is not supported.
                           OKF emits the Data Dictionary as an Open Knowledge Format document
                           (https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) -
                           a leaner, vendor-neutral plain-markdown-plus-YAML-frontmatter format. It
                           emits frontmatter (type/title/description/resource/timestamp/tags) and a
                           Schema section with a Column/Type/Content Type/Description/Enumeration
                           table. The type frontmatter key is set via the okf-type flag (default
                           "CSV Table"); ds-source maps to resource and ds-updated maps to timestamp.
                           Like SemanticMd, OKF implies infer-content-type, requires the dictionary
                           inference phase (the dictionary or all flag), folds the description
                           inference into the body prose and a single-sentence frontmatter
                           description, and embeds tags in the frontmatter. The prompt inference is
                           not supported.
                           [default: Markdown]
    --allow-extra-cols     When the format is JSONSchema, emit additionalProperties as true at the
                           schema root (default is false, strict). Only meaningful with the
                           JSONSchema format; ignored otherwise.
    --strict-dates         When the format is JSONSchema, emit format date or date-time for
                           columns that stats infers as Date or DateTime. Off by default because
                           qsv's --infer-dates is permissive (accepts strings like
                           "June 27, 1968") and JSON Schema's date formats require RFC 3339, so
                           the validate roundtrip would otherwise fail. Set this only when your
                           source columns are guaranteed to be RFC 3339 full-date / date-time.
                           Mirrors the same flag on the schema command.
    --ds-source <text>     For the SemanticMd & OKF formats only: the dataset source/provenance
                           recorded in the document frontmatter (e.g. a source URL or publisher).
                           For OKF this populates the `resource` key. Optional; the frontmatter key
                           is omitted when unset. Ignored by other formats.
    --ds-updated <text>    For the SemanticMd & OKF formats only: the dataset's last-updated date
                           recorded in the document frontmatter. For OKF this populates the
                           `timestamp` key. Optional. Ignored by other formats.
    --ds-license <text>    For the SemanticMd format only: the dataset license recorded in the
                           document frontmatter. Optional. Ignored by other formats.
    --okf-type <text>      For the OKF format only: the value of the required `type` frontmatter key
                           (e.g. "CSV Table", "BigQuery Table"). Optional; defaults to "CSV Table".
                           Ignored by other formats.
    -o, --output <file>    Write output to <file> instead of stdout. If --format is set to TSV,
                           separate files will be created for each prompt type with the pattern
                           {filestem}.{kind}.tsv (e.g., output.dictionary.tsv, output.tags.tsv).
    -q, --quiet            Do not print status messages to stderr.
```
## qsv diff

```text
Find the difference between two CSVs with ludicrous speed.

NOTE: diff does not support stdin. A file path is required for both arguments.
      Further, PRIMARY KEY VALUES MUST BE UNIQUE WITHIN EACH CSV.

      To check if a CSV has unique primary key values, use `qsv extdedup`
      with the same key columns using the `--select` option:

         $ qsv extdedup --select keycol data.csv --no-output

      The duplicate count will be printed to stderr.

Examples:

# Find the difference between two CSVs
qsv diff left.csv right.csv

# Find the difference between two CSVs when the right CSV has no headers
qsv diff left.csv --no-headers-right right-noheaders.csv

# Find the difference between two CSVs when the left CSV uses a tab delimiter
qsv diff --delimiter-left '\t' left.csv right-tab.tsv

# Find the difference between two CSVs when the left CSV uses a semicolon delimiter
qsv diff --delimiter-left ';' left.csv right-semicolon.csv

# Find the difference between two CSVs and write output with tab delimiter to a file
qsv diff -o diff-tab.tsv --delimiter-output '\t' left.csv right.csv

# Find the difference between two CSVs and write output with semicolon delimiter to a file
qsv diff -o diff-semicolon.csv --delimiter-output ';' left.csv right.csv

# Find the difference comparing records with the same values in the first two columns
qsv diff --key 0,1 left.csv right.csv

# Find the difference using first two columns as key and sort result by those columns
qsv diff -k 0,1 --sort-columns 0,1 left.csv right.csv

# Find the difference but replace equal field values with empty string (key fields still appear)
qsv diff --drop-equal-fields left.csv right.csv

# Find the difference but drop entire columns that have no differences anywhere (key columns still appear)
qsv diff --drop-equal-columns left.csv right.csv

# Combine both: keep only differing columns, and within them, blank out equal field values
qsv diff --drop-equal-columns --drop-equal-fields left.csv right.csv

# Find the difference but do not output headers in the result
qsv diff --no-headers-output left.csv right.csv

# Find the difference when both CSVs have no headers (generic headers _col_1, _col_2, etc. are used)
qsv diff --no-headers-left --no-headers-right left.csv right.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_diff.rs
See also https://github.com/dathere/qsv/wiki/Indexing-Compression-Diff#diff

Usage:
    qsv diff [options] [<input-left>] [<input-right>]
    qsv diff --help

diff options:
    --no-headers-left           When set, the first row will be considered as part of
                                the left CSV to diff. (When not set, the
                                first row is the header row and will be skipped during
                                the diff. It will always appear in the output.)
    --no-headers-right          When set, the first row will be considered as part of
                                the right CSV to diff. (When not set, the
                                first row is the header row and will be skipped during
                                the diff. It will always appear in the output.)
    --no-headers-output         When set, the diff result won't have a header row in
                                its output. If not set and both CSVs have no headers,
                                headers in the result will be: _col_1,_col_2, etc.
    --delimiter-left <arg>      The field delimiter for reading CSV data on the left.
                                Must be a single character. (default: ,)
    --delimiter-right <arg>     The field delimiter for reading CSV data on the right.
                                Must be a single character. (default: ,)
    --delimiter-output <arg>    The field delimiter for writing the CSV diff result.
                                Must be a single character. (default: ,)
    -k, --key <arg...>          The column indices that uniquely identify a record
                                as a comma separated list of 0-based indices, e.g. 0,1,2
                                or column names, e.g. name,age.
                                Note that when selecting columns by name, only the
                                left CSV's headers are used to match the column names
                                and it is assumed that the right CSV has the same
                                selected column names in the same order as the left CSV.
                                (default: 0)
    --sort-columns <arg...>     The column indices by which the diff result should be
                                sorted as a comma separated list of indices, e.g. 0,1,2
                                or column names, e.g. name,age.
                                Records in the diff result that are marked as "modified"
                                ("delete" and "add" records that have the same key,
                                but have different content) will always be kept together
                                in the sorted diff result and so won't be sorted
                                independently from each other.
                                Note that when selecting columns by name, only the
                                left CSV's headers are used to match the column names
                                and it is assumed that the right CSV has the same
                                selected column names in the same order as the left CSV.
    --drop-equal-fields         Drop values of equal fields in modified rows of the CSV
                                diff result (and replace them with the empty string).
                                Key field values will not be dropped.
    --drop-equal-columns        Drop entire columns from the diff result that have no
                                differences anywhere. A column is kept if it is a key
                                column, if it differs in any modified row, or if it has
                                a non-empty value in any added or deleted row. Otherwise
                                it is dropped. Can be combined with --drop-equal-fields.
    -j, --jobs <arg>            The number of jobs to run in parallel.
                                When not set, the number of jobs is set to the number
                                of CPUs detected.

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout.
    -d, --delimiter <arg>       Set ALL delimiters to this character.
                                Overrides --delimiter-right, --delimiter-left
                                and --delimiter-output.
```
## qsv edit

```text
Replace the value of a cell specified by its row and column.

Example:

items.csv
```csv
item,color
shoes,blue
flashlight,gray
```

# To output the data with the color of the shoes as green instead of blue
$ qsv edit items.csv color 0 green

```csv
item,color
shoes,green
flashlight,gray
```

You may also choose to specify the column name by its index (in this case 1).
Specifying a column as a number is prioritized by index rather than name.
If there is no newline (\n) at the end of the input data, it may be added to the output.

See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#edit

Usage:
    qsv edit [options] <input> <column> <row> <value>
    qsv edit --help

edit arguments:
    input                  The file from which to edit a cell value. Use '-' for standard input.
                           Must be either CSV, TSV, TAB, or SSV data.
    column                 The cell's column name or index. Indices start from the first column as 0.
                           Providing a value of underscore (_) selects the last column.
    row                    The cell's row index. Indices start from the first non-header row as 0.
    value                  The new value to replace the old cell content with.

If <row> is out of range:
  - in stdout/--output mode, the input is passed through unchanged with a warning on stderr.
  - in --in-place mode, the command errors and the input file is left untouched.

edit options:
    -i, --in-place         Overwrite the input file data with the output.
                           The input file is renamed to a .bak file in the same directory.
                           If the .bak file already exists, the command errors instead of overwriting it.
                           Symbolic links are rejected; pass the resolved path instead.
                           (Other Windows reparse points such as junction points are not detected.)

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       Start row indices from the header row as 0 (allows editing the header row).
```
## qsv enum

```text
Add a new column enumerating the lines of a CSV file. This can be useful to keep
track of a specific line order, give a unique identifier to each line or even
make a copy of the contents of a column.

The enum function has six modes of operation:

  1. INCREMENT. Add an incremental identifier to each of the lines:
    $ qsv enum file.csv

  2. UUID4. Add a uuid v4 to each of the lines:
    $ qsv enum --uuid4 file.csv

  3. UUID7. Add a uuid v7 to each of the lines:
    $ qsv enum --uuid7 file.csv

  4. CONSTANT. Create a new column filled with a given value:
    $ qsv enum --constant 0

  5. COPY. Copy the contents of a column to a new one:
    $ qsv enum --copy names

  6. HASH. Create a new column with the deterministic hash of the given column/s.
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

Examples:

  # Add an incremental index column starting from 0 (default)
  qsv enum data.csv

  # Add an incremental index column starting from 100 and incrementing by 10
  qsv enum --start 100 --increment 10 data.csv

  # Add a uuid v4 column
  qsv enum --uuid4 data.csv

  # Add a uuid v7 column
  qsv enum --uuid7 data.csv

  # Add a constant column with the value "active"
  qsv enum --constant active data.csv

  # Add a constant column with null values
  qsv enum --constant "<NULL>" data.csv

  # Add a copy of the "username" column as "username_copy"
  qsv enum --copy username data.csv

  # Add a hash column with the hash of columns "first_name" and "last_name"
  qsv enum --hash first_name,last_name data.csv

  # Add a hash column with the hash of all columns except an existing "hash" column
  qsv enum --hash 1- data.csv

  # Add a hash column with the hash of all columns except "id" and "uuid" columns
  qsv enum --hash "!id,!uuid" data.csv

  # Add a hash column with the hash of all columns that match the regex "record|name|address"
  qsv enum --hash "/record|name|address/" data.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_enumerate.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#enum

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
## qsv excel

```text
Exports a specified Excel/ODS sheet to a CSV file.
The first non-empty row of a sheet is assumed to be the header row.

Examples:

# Export the first sheet of an Excel file to a CSV file:
qsv excel input.xlsx --output output.csv

# Export the first sheet of an ODS file to a CSV file:
qsv excel input.ods -o output.csv

# Export the first sheet of an Excel file to a CSV file with a custom delimiter:
qsv excel input.xlsx -d ";" > output.csv

# Export a sheet by name (case-insensitive):
qsv excel --sheet "Sheet 3" input.xlsx

# Export a sheet by index:
# this exports the 3rd sheet (0-based index)
qsv excel -s 2 input.xlsx

# Export the last sheet (negative index):
qsv excel -s -1 input.xlsx

# Export the second to last sheet:
qsv excel -s -2 input.xls

# Export a table named "Table1" in an XLSX file. Note that --sheet is not required
# as the table definition includes the sheet.
qsv excel --table "Table1" input.xlsx

# Export a range of cells in the first sheet:
qsv excel --range C3:T25 input.xlsx

# Export a named range in the workbook. Note that --sheet is not required
# as named ranges include the sheet.
qsv excel --range MyRange input.xlsx

# Export a range of cells in the second sheet:
qsv excel --range C3:T25 -s 1 input.xlsx

# Export a range of cells in a sheet by name.
# Note the range name must be enclosed in single quotes in certain shells
# as it may contain special characters like ! and $:
qsv excel --range 'Sheet2!C3:T25' input.xlsx

# Export the cell C3 in the first sheet:
qsv excel --cell C3 input.xlsx

# Export a single cell from a specific sheet:
qsv excel --cell 'Sheet2!C3' input.xlsx

# Export metadata for all sheets in CSV format:
qsv excel --metadata csv input.xlsx

# Export metadata in short CSV mode which is much faster
# but doesn't contain as much metadata
qsv excel --metadata short input.xlsx

# Export metadata for all sheets in JSON format:
qsv excel --metadata json input.xlsx

# Export metadata to pretty-printed JSON - first letter is capital J
qsv excel --metadata JSON input.xlsx

# Export metadata in short, minified JSON mode - first letter is capital S
qsv excel --metadata Short input.xlsx

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_excel.rs.
See also https://github.com/dathere/qsv/wiki/Conversion-and-IO#excel

Usage:
    qsv excel [options] [<input>]
    qsv excel --help

Excel argument:
    <input>                   The spreadsheet file to read. Use "-" to read from stdin.
                              Supported formats: xls, xlsx, xlsm, xlsb, ods.

Excel options:
    -s, --sheet <name/index>   Name (case-insensitive) or zero-based index of sheet to export.
                               Negative indices start from the end (-1 = last sheet).
                               If the sheet cannot be found, qsv will read the first sheet.
                               [default: 0]
    --header-row <row>         The header row. Set if other than the first non-empty row of the sheet.
    --metadata <c|s|j|J|S>     Outputs workbook metadata in CSV or JSON format:
                                 index, sheet_name, type, visible, headers, column_count, row_count,
                                 safe_headers, safe_headers_count, unsafe_headers, unsafe_headers_count
                                 and duplicate_headers_count, names, name_count, tables, table_count.
                               headers is a list of the first row which is presumed to be the header row.
                               type is the sheet type (WorkSheet, DialogSheet, MacroSheet, ChartSheet, Vba).
                               visible is the sheet visibility (Visible, Hidden, VeryHidden).
                               row_count includes all rows, including the first row.
                               safe_headers is a list of headers with "safe"(PostgreSQL-ready) names.
                               unsafe_headers is a list of headers with "unsafe" names.
                               duplicate_headers_count is a count of duplicate header names.
                               names is a list of defined names in the workbook, with the associated formula.
                               name_count is the number of defined names in the workbook.
                               tables is a list of tables in the workbook, along with the sheet where
                                the table is found, the columns and the column_count.  (XLSX only)
                               table_count is the number of tables in the workbook.  (XLSX only)

                               In CSV(c) mode, the output is in CSV format.
                               In short(s) CSV mode, the output is in CSV format with only the
                                index, sheet_name, type and visible fields.

                               In JSON(j) mode, the output is minified JSON.
                               In Pretty JSON(J) mode, the output is pretty-printed JSON.
                               In Short(S) JSON mode, the output is minified JSON with only the
                                 index, sheet_name, type and visible fields.
                               For all JSON modes, the filename, the full file path, the workbook format
                                and the number of sheets are also included.
                               For XLS/XLSX/XLSM/XLSB workbooks, has_1904_epoch is also included,
                                indicating whether the workbook uses the 1904 date system
                                (true) or the 1900 date system (false). Omitted for ODS.
                               If metadata retrieval performance is a concern, use the short modes
                               as they return instantaneously as they don't need to process the sheet data.

                               If this option is used, all other Excel options are ignored.
                               [default: none]

    --table <table>            An Excel table (case-insensitive) to extract to a CSV.
                               Only valid for XLSX files. The --sheet option is ignored as a table could
                               be in any sheet. Overrides --range option.
    --range <range>            An Excel format range - like RangeName, C:T, C3:T25 or 'Sheet1!C3:T25' to
                               extract to the CSV. If the specified range contains the required sheet,
                               the --sheet option is ignored.
                               If the range is not found, qsv will exit with an error.
    --cell <cell>              A single cell reference - like C3 or 'Sheet1!C3' to extract.
                               This is a convenience option equivalent to --range C3:C3.
                               If both --cell and --range are specified, --cell takes precedence.

    --error-format <format>    The format to use when formatting error cells.
                               There are 3 formats:
                                 * "code": return the error code.
                                    (#DIV/0!; #N/A; #NAME?; #NULL!; #NUM!; #REF!; #VALUE!; #DATA!)
                                 * "formula": return the formula, prefixed with '#'.
                                    (e.g. #=A1/B1 where B1 is 0; #=100/0)
                                 * "both": return both error code and the formula.
                                    (e.g. #DIV/0!: =A1/B1)
                               [default: code]
    --flexible                 Continue even if the number of columns is different from row to row.
    --trim                     Trim all fields so that leading & trailing whitespaces are removed.
                               Also removes embedded linebreaks.
    --date-format <format>     Optional date format to use when formatting dates.
                               See https://docs.rs/chrono/latest/chrono/format/strftime/index.html
                               for the full list of supported format specifiers.
                               Note that if a date format is invalid, qsv will fall back and
                               return the date as if no date-format was specified.
     --keep-zero-time          Keep the time part of a date-time field if it is 00:00:00.
                               By default, qsv will remove the time part if it is 00:00:00.
     -j, --jobs <arg>          The number of jobs to run in parallel.
                               When not set, the number of jobs is set to the number of CPUs detected.

Common options:
    -h, --help                 Display this message
    -o, --output <file>        Write output to <file> instead of stdout.
    -d, --delimiter <arg>      The delimiter to use when writing CSV data.
                               Must be a single character. (default: ,)
    -q, --quiet                Do not display export summary message.
```
## qsv exclude

```text
Removes a set of CSV data from another set based on the specified columns.

Also can compute the intersection of two CSV sets with the -v flag.

Matching is always done by ignoring leading and trailing whitespace. By default,
matching is done case sensitively, but this can be disabled with the --ignore-case
flag.

The columns arguments specify the columns to match for each input. Columns can
be referenced by name or index, starting at 1. Specify multiple columns by
separating them with a comma. Specify a range of columns with `-`. Both
columns1 and columns2 must specify exactly the same number of columns.
(See 'qsv select --help' for the full syntax.)

Either <input1> or <input2> can be set to `-` to read from stdin, but not both.

Examples:

  # Remove all records in previously-processed.csv from records.csv
  qsv exclude id records.csv id previously-processed.csv

  # Remove all records in previously-processed.csv matching on multiple columns
  qsv exclude col1,col2 records.csv col1,col2 previously-processed.csv

  # Remove all records in previously-processed.csv matching on column ranges
  qsv exclude col1-col5 records.csv col1-col5 previously-processed.csv

  # Remove all records in previously-processed.csv with the same id from records.csv
  # and write to new-records.csv
  qsv exclude id records.csv id previously-processed.csv > new-records.csv

  # Remove all records in previously-processed.csv with the same id from records.csv
  # and write to new-records.csv
  qsv exclude id records.csv id previously-processed.csv --output new-records.csv

  # Get the intersection of records.csv and previously-processed.csv on id column
  # (i.e., only records present in both files)
  qsv exclude -v id records.csv id previously-processed.csv -o intersection.csv

  # Do a case insensitive exclusion on the id column
  qsv exclude --ignore-case id records.csv id previously-processed.csv

  # Read records.csv from stdin
  cat records.csv | qsv exclude id - id previously-processed.csv

  # Chain exclude with sort to create a new sorted records file without previously processed records
  qsv exclude id records.csv id previously-processed.csv | \
      qsv sort > new-sorted-records.csv

  # Chain exclude with sort and dedup to create a new sorted deduped records file
  qsv exclude id records.csv id previously-processed.csv | qsv sort | \
      qsv --sorted dedup > new-sorted-deduped-records.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_exclude.rs.
See also https://github.com/dathere/qsv/wiki/Joins-and-Set-Ops#exclude

Usage:
    qsv exclude [options] <columns1> <input1> <columns2> <input2>
    qsv exclude --help

input arguments:
    <input1> is the file from which data will be removed.
    <input2> is the file containing the data to be removed from <input1>
     e.g. 'qsv exclude id records.csv id previously-processed.csv'
    Either input may be set to `-` to read from stdin, but not both.

exclude options:
    -i, --ignore-case      When set, matching is done case insensitively.
    -v, --invert           When set, matching rows will be the only ones included,
                           forming set intersection, instead of the ones discarded.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load <input2>
                           into memory using CONSERVATIVE heuristics.
```
## qsv explode

```text
Explodes a row into multiple ones by splitting a column value based on the
given separator.

Example:

```csv
name,colors
John,blue|yellow
Mary,red
```

# Can be exploded on the "colors" <column> based on the "|" <separator>
$ qsv explode colors "|" data.csv

```csv
name,colors
John,blue
John,yellow
Mary,red
```

See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#explode

Usage:
    qsv explode [options] <column> <separator> [<input>]
    qsv explode --help

explode options:
    -r, --rename <name>    New name for the exploded column.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv extdedup

```text
Remove duplicate rows from an arbitrarily large CSV/text file using a memory-mapped,
on-disk hash table.

Unlike the 'dedup' command, this command does not load the entire file into memory
to sort the CSV first before deduping it.

This allows it to run in constant memory and the output will retain the input sort order.

This command has TWO modes of operation.

 * CSV MODE
   when --select is set, it dedupes based on the given column/s. See `qsv select --help`
   for select syntax details.
 * LINE MODE
   when --select is NOT set, it deduplicates any input text file (not just CSVs) on a
   line-by-line basis.

A duplicate count will be sent to <stderr>.

See also https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#extdedup

Usage:
    qsv extdedup [options] [<input>] [<output>]
    qsv extdedup --help

extdedup options:
    -s, --select <arg>         Select a subset of columns to dedup.
                               Note that the outputs will remain at the full width of the CSV.
                               If --select is NOT set, extdedup will work in LINE MODE, deduping
                               the input as a text file on a line-by-line basis.
    --no-output                Do not write deduplicated output to <output>.
                               Use this if you only want to know the duplicate count.
                               Applies to both CSV MODE and LINE MODE.
    -D, --dupes-output <file>  Write duplicates to <file>.
                               In CSV MODE, <file> is a valid CSV with the same columns as the
                               input plus a leading "dupe_rowno" column (1-based data row number).
                               In LINE MODE, <file> is NOT a valid CSV — each duplicate line is
                               prefixed by its 0-based file line index and a tab character.
    -H, --human-readable       Comma separate duplicate count.
    --memory-limit <arg>       How much memory to use before deduping switches to a
                               temporary file on disk (see --temp-dir).
                               If less than 50, this is a percentage of total memory.
                               If more than 50, this is the memory in MB to allocate, capped
                               at 90 percent of total memory.
                               Defaults to 100 MB. Raising this mostly just uses more memory,
                               as deduping on disk needs far less memory per row.
    --temp-dir <arg>           Directory to store temporary hash table file.
                               If not specified, defaults to operating system temp directory.

Common options:
                               CSV MODE ONLY:
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. That is, it will be deduped with the rest
                               of the rows. Otherwise, the first row will always
                               appear as the header row in the output.
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character. (default: ,)

    -h, --help                 Display this message
    -q, --quiet                Do not print duplicate count to stderr.
```
## qsv extsort

```text
Sort an arbitrarily large CSV/text file using a multithreaded external sort algorithm.

This command has TWO modes of operation.

 * CSV MODE
   when --select is set, it sorts based on the given column/s. Requires an index.
   See `qsv select --help` for select syntax details.

   STATS-CACHE AWARE: in CSV MODE, when a single ASCII column is selected and a valid
   stats cache exists (see `qsv stats --stats-jsonl`), extsort uses the cached sort order
   to detect if the column is already in ascending order and, if so, streams the input
   through unchanged, skipping the external sort entirely. Not applied with --reverse or
   multi-column selections. Disable with QSV_STATSCACHE_MODE=none.
 * LINE MODE
   when --select is NOT set, it sorts any input text file (not just CSVs) on a
   line-by-line basis. If sorting a non-CSV file, be sure to set --no-headers,
   otherwise, the first line will not be included in the external sort.

See also https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#extsort

Usage:
    qsv extsort [options] [<input>] [<output>]
    qsv extsort --help

External sort option:
    -s, --select <arg>     Select a subset of columns to sort (CSV MODE).
                           Note that the outputs will remain at the full width of the CSV.
                           If --select is NOT set, extsort will work in LINE MODE, sorting
                           the input as a text file on a line-by-line basis.
    -R, --reverse          Reverse order
    --memory-limit <arg>   The memory budget for sorting each in-memory chunk. Input that
                           exceeds it is sorted in chunks spilled to the tmp-dir, then merged.
                           The budget is approximate - peak memory use is higher, as it
                           does not count sort scratch space, allocator overhead, or the
                           merge phase's read buffer (~1 MB per chunk).
                           If less than 50, this is a percentage of total memory.
                           If more than 50, this is the memory in MB to allocate, capped
                           at 90 percent of total memory.
                           [default: 20]
    --tmp-dir <arg>        The directory to use for externally sorting file segments.
                           [default: ./]
    -j, --jobs <arg>       The number of jobs to run in parallel.
                           When not set, the number of jobs is set to the
                           number of CPUs detected.

Common options:
                           CSV MODE ONLY:
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)

    -h, --help             Display this message
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers and will be sorted with the rest
                           of the rows. Otherwise, the first row will always
                           appear as the header row in the output.
```
## qsv fetch

```text
Send/Fetch data to/from web services for every row using HTTP Get.

Fetch is integrated with `jaq` (a jq clone) to directly parse out values from an API JSON response.
(See https://github.com/01mf02/jaq for more info on how to use the jaq JSON Query Language)

CACHE OPTIONS:
Fetch caches responses to minimize traffic and maximize performance. It has four
mutually-exclusive caching options:

1. In memory cache (the default)
2. Disk cache
3. Redis cache
4. No cache

In memory Cache:
In memory cache is the default and is used if no caching option is set.
It uses a non-persistent, in-memory, 2 million entry Least Recently Used (LRU)
cache for each fetch session. To change the maximum number of entries in the cache,
set the --mem-cache-size option.

Disk Cache:
For persistent, inter-session caching, a DiskCache can be enabled with the --disk-cache flag.
By default, it will store the cache in the directory ~/.qsv-cache/fetch, with a cache expiry
Time-to-Live (TTL) of 2,419,200 seconds (28 days), and cache hits NOT refreshing the TTL
of cached values.

Set the --disk-cache-dir option and the environment variables QSV_DISKCACHE_TTL_SECS and
QSV_DISKCACHE_TTL_REFRESH to change default DiskCache settings.

Redis Cache:
Another persistent, inter-session cache option is a Redis cache, enabled with
the --redis-cache flag.
By default, it will connect to a local Redis instance at redis://127.0.0.1:6379/1,
with a cache expiry Time-to-Live (TTL) of 2,419,200 seconds (28 days),
and cache hits NOT refreshing the TTL of cached values.

Set the environment variables QSV_REDIS_CONNSTR, QSV_REDIS_TTL_SECS and
QSV_REDIS_TTL_REFRESH to change default Redis settings.

If you don't want responses to be cached at all, use the --no-cache flag.

NETWORK OPTIONS:
Fetch recognizes RateLimit and Retry-After headers and dynamically throttles requests
to be as fast as allowed. The --rate-limit option sets the maximum number of queries per second
(QPS) to be made. The default is 0, which means to go as fast as possible, automatically
throttling as required, based on rate-limit and retry-after response headers.

To use a proxy, set the environment variables HTTP_PROXY, HTTPS_PROXY or ALL_PROXY
(e.g. export HTTPS_PROXY=socks5://127.0.0.1:1086). Your operating system's own
proxy configuration (macOS System Settings, Windows registry) is also honored;
the environment variables take precedence over it.

qsv fetch supports brotli, gzip and deflate automatic decompression for improved throughput
and performance, preferring brotli over gzip over deflate.

It automatically upgrades its connection to the much faster and more efficient HTTP/2 protocol
with adaptive flow control if the server supports it.
See https://www.cloudflare.com/learning/performance/http2-vs-http1.1/ and
https://medium.com/coderscorner/http-2-flow-control-77e54f7fd518 for more info.

URL OPTIONS:
<url-column> needs to be a fully qualified URL path. Alternatively, you can dynamically
construct URLs for each CSV record with the --url-template option (see Examples below).

JSON RESPONSE HANDLING:
When --jaq is not used, fetch parses each successful response with serde_json and
writes it back out (compact by default, or re-indented with --pretty). Object key
order is preserved (qsv enables serde_json's preserve_order feature), but the body
is otherwise normalized: all insignificant whitespace is removed (compact) or
re-indented (--pretty); number representations are canonicalized (e.g. 1e2 -> 100,
leading zeros stripped, exponent form normalized); duplicate keys within a JSON
object are collapsed (last value wins); and responses that are not valid JSON are
written as an empty cell (or the parse error if --store-error is set). If you need
byte-exact server output, post-process the response yourself or use --jaq to
extract specific fields.

Example:

USING THE URL-COLUMN ARGUMENT:

data.csv
```csv
URL
https://api.zippopotam.us/us/90210
https://api.zippopotam.us/us/94105
https://api.zippopotam.us/us/92802
```

# Given the data.csv above, fetch the JSON response.
$ qsv fetch URL data.csv

Note the output will be a JSONL file - with a minified JSON response per line, not a CSV file.

# Now, if we want to generate a CSV file with the parsed City and State, we use the
# new-column and jaq options.
$ qsv fetch URL --new-column CityState --jaq '[ ."places"[0]."place name",."places"[0]."state abbreviation" ]' \
    data.csv > data_with_CityState.csv

data_with_CityState.csv
```csv
URL,CityState
https://api.zippopotam.us/us/90210,"[""Beverly Hills"",""CA""]"
https://api.zippopotam.us/us/94105,"[""San Francisco"",""CA""]"
https://api.zippopotam.us/us/92802,"[""Anaheim"",""CA""]"
```

# As you can see, entering jaq selectors on the command line is error prone and can quickly become cumbersome.
# Alternatively, the jaq selector can be saved and loaded from a file using the --jaqfile option.
$ qsv fetch URL --new-column CityState --jaqfile places.jaq data.csv > datatest.csv

Examples:

USING THE --URL-TEMPLATE OPTION:
Instead of using hardcoded URLs, you can also dynamically construct the URL for each CSV row using CSV column
values in that row.

Example 1:
For example, we have a CSV with four columns and we want to geocode against the geocode.earth API that expects
latitude and longitude passed as URL parameters.

addr_data.csv
```csv
location, description, latitude, longitude
Home, "house is not a home when there's no one there", 40.68889829703977, -73.99589368107037
X, "marks the spot", 40.78576117777992, -73.96279560368552
work, "moolah", 40.70692672280804, -74.0112264146281
school, "exercise brain", 40.72916494539206, -73.99624185993626
gym, "exercise muscles", 40.73947342617386, -73.99039923885411
```

# Geocode addresses in addr_data.csv, pass the latitude and longitude fields and store
# the response in a new column called response into enriched_addr_data.csv.
$ qsv fetch --url-template "https://api.geocode.earth/v1/reverse?point.lat={latitude}&point.lon={longitude}" \
    addr_data.csv -c response > enriched_addr_data.csv

Example 2:
# Geocode addresses in addresses.csv, pass the "street address" and "zip-code" fields
# and use jaq to parse placename from the JSON response into a new column in addresses_with_placename.csv.
# Note how field name non-alphanumeric characters (space and hyphen) in the url-template were replaced with _.
$ qsv fetch --jaq '."features"[0]."properties", ."name"' addresses.csv -c placename --url-template \
  "https://api.geocode.earth/v1/search/structured?address={street_address}&postalcode={zip_code}" \
  > addresses_with_placename.csv

USING THE HTTP-HEADER OPTION:
The --http-header option allows you to append arbitrary key value pairs (a valid pair is a key and value
separated by a colon) to the HTTP header (to authenticate against an API, pass custom header fields, etc.).
Note that you can pass as many key-value pairs by using --http-header option repeatedly. For example:

  $ qsv fetch URL data.csv --http-header "X-Api-Key:TEST_KEY" -H "X-Api-Secret:ABC123XYZ" -H "Accept-Language: fr-FR"

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_fetch.rs.
See also https://github.com/dathere/qsv/wiki/HTTP-and-Web#fetch

Usage:
    qsv fetch [<url-column> | --url-template <template>] [--jaq <selector> | --jaqfile <file>] [--http-header <k:v>...] [options] [<input>]
    qsv fetch --help

Fetch options:
    <url-column>               Name of the column with the URL.
                               Mutually exclusive with --url-template.
    --url-template <template>  URL template to use. Use column names enclosed with
                               curly braces to insert the CSV data for a record.
                               Mutually exclusive with url-column.
    -c, --new-column <name>    Put the fetched values in a new column. Specifying this option
                               results in a CSV. Otherwise, the output is in JSONL format.
    --jaq <selector>           Apply jaq selector to API returned JSON value.
                               Mutually exclusive with --jaqfile,
    --jaqfile <file>           Load jaq selector from file instead.
                               Mutually exclusive with --jaq.
    --pretty                   Prettify JSON responses. Otherwise, they're minified.
                               If the response is not in JSON format, it's passed through.
                               Note that --pretty requires the --new-column option.
    --rate-limit <qps>         Rate Limit in Queries Per Second (max: 1000). Note that fetch
                               dynamically throttles as well based on rate-limit and
                               retry-after response headers.
                               Set to 0 to go as fast as possible, automatically throttling as required.
                               CAUTION: Only use zero for APIs that use RateLimit and/or Retry-After headers,
                               otherwise your fetch job may look like a Denial Of Service attack.
                               Even though zero is the default, this is mitigated by --max-errors having a
                               default of 10.
                               [default: 0 ]
    --timeout <seconds>        Timeout for each URL request.
                               [default: 30 ]
    --default-encoding <enc>   Fallback character encoding used to decode a response body when
                               the server does NOT send a charset parameter in its Content-Type
                               header. Accepts WHATWG encoding labels, e.g. utf-8, windows-1252,
                               iso-8859-1, shift_jis, euc-jp, koi8-r.
                               When the server DOES send a charset, the server always wins and
                               this option is ignored.
                               [default: utf-8]
    -H, --http-header <k:v>    Append custom header(s) to the HTTP header. Pass multiple key-value pairs
                               by adding this option multiple times, once for each pair. The key and value
                               should be separated by a colon.
    --max-retries <count>      Maximum number of retries per record before an error is raised.
                               [default: 5]
    --max-errors <count>       Maximum number of errors before aborting.
                               Set to zero (0) to continue despite errors.
                               [default: 10 ]
    --store-error              On error, store error code/message instead of blank value.
    --cookies                  Allow cookies.
    --user-agent <agent>       Specify custom user agent. It supports the following variables -
                               $QSV_VERSION, $QSV_TARGET, $QSV_BIN_NAME, $QSV_KIND and $QSV_COMMAND.
                               Try to follow the syntax here -
                               https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
    --report <d|s>             Creates a report of the fetch job. The report has the same name as the input file
                               with the ".fetch-report" suffix.
                               There are two kinds of report - d for "detailed" & s for "short". The detailed
                               report has the same columns as the input CSV with six additional columns -
                               qsv_fetch_url, qsv_fetch_status, qsv_fetch_cache_hit, qsv_fetch_retries,
                               qsv_fetch_elapsed_ms & qsv_fetch_response.
                               The short report only has the six columns without the "qsv_fetch_" prefix.
                               [default: none]

                               CACHING OPTIONS:
    --no-cache                 Do not cache responses.

    --mem-cache-size <count>   Maximum number of entries in the in-memory LRU cache.
                               [default: 2000000]

    --disk-cache               Use a persistent disk cache for responses. The cache is stored in the directory
                               specified by --disk-cache-dir. If the directory does not exist, it will be
                               created. If the directory exists, it will be used as is.
                               It has a default Time To Live (TTL)/lifespan of 28 days and cache hits do not
                               refresh the TTL of cached values.
                               Adjust the QSV_DISKCACHE_TTL_SECS & QSV_DISKCACHE_TTL_REFRESH env vars
                               to change DiskCache settings. A QSV_DISKCACHE_TTL_SECS of 0 disables
                               time-based expiration (entries are cached indefinitely).
    --disk-cache-dir <dir>     The directory <dir> to store the disk cache. Note that if the directory
                               does not exist, it will be created. If the directory exists, it will be used as is,
                               and will not be flushed. This option allows you to maintain several disk caches
                               for different fetch jobs (e.g. one for geocoding, another for weather, etc.)
                               [default: ~/.qsv-cache/fetch]

    --redis-cache              Use Redis to cache responses. It connects to "redis://127.0.0.1:6379/1"
                               with a connection pool size of 20, with a TTL of 28 days, and a cache hit
                               NOT renewing an entry's TTL.
                               Adjust the QSV_REDIS_CONNSTR, QSV_REDIS_MAX_POOL_SIZE, QSV_REDIS_TTL_SECS &
                               QSV_REDIS_TTL_REFRESH env vars respectively to change Redis settings.
                               A QSV_REDIS_TTL_SECS of 0 disables expiration (entries cached indefinitely).
                               This option is ignored if the --disk-cache option is enabled.

    --cache-error              Cache error responses even if a request fails. If an identical URL is requested,
                               the cached error is returned. Otherwise, the fetch is attempted again
                               for --max-retries.
    --flush-cache              Flush all the keys in the current cache on startup. This only applies to
                               Disk and Redis caches.

Common options:
    -h, --help                 Display this message
    -o, --output <file>        Write output to <file> instead of stdout.
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. Namely, it will be sorted with the rest
                               of the rows. Otherwise, the first row will always
                               appear as the header row in the output.
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character. (default: ,)
    -p, --progressbar          Show progress bars. Will also show the cache hit rate upon completion.
                               Not valid for stdin.
```
## qsv fetchpost

```text
Fetchpost sends/fetches data to/from web services for every row using HTTP Post.
As opposed to fetch, which uses HTTP Get.

CSV data is posted using two methods:
1. As an HTML Form using using the <column-list> argument
   The columns are used to construct the HTML form data and posted to the server
   as a URL-encoded form. (content-type: application/x-www-form-urlencoded)
2. As a payload using a MiniJinja template with the --payload-tpl <file> option
   The template file is used to construct the payload and posted to the server
   as JSON by default (content-type: application/json), with automatic checking if the
   rendered template is valid JSON.
   The --content-type option can override the expected content type. However, it is
   the user's responsibility to ensure the content-type format is valid.

Fetchpost is integrated with `jaq` (a jq clone) to directly parse out values from an API JSON response.
(See https://github.com/01mf02/jaq for more info on how to use the jaq JSON Query Language)

CACHE OPTIONS:
Fetchpost caches responses to minimize traffic and maximize performance. It has four
mutually-exclusive caching options:

1. In memory cache (the default)
2. Disk cache
3. Redis cache
4. No cache

In memory Cache:
In memory cache is the default and is used if no caching option is set.
It uses a non-persistent, in-memory, 2 million entry Least Recently Used (LRU)
cache for each fetch session. To change the maximum number of entries in the cache,
set the --mem-cache-size option.

Disk Cache:
For persistent, inter-session caching, a DiskCache can be enabled with the --disk-cache flag.
By default, it will store the cache in the directory ~/.qsv-cache/fetchpost, with a cache expiry
Time-to-Live (TTL) of 2,419,200 seconds (28 days), and cache hits NOT refreshing the TTL
of cached values.

Set the --disk-cache-dir option and the environment variables QSV_DISKCACHE_TTL_SECS and
QSV_DISKCACHE_TTL_REFRESH to change default DiskCache settings.

Redis Cache:
Another persistent, inter-session cache option is a Redis cache, enabled with
the --redis-cache flag.
By default, it will connect to a local Redis instance at redis://127.0.0.1:6379/2,
with a cache expiry Time-to-Live (TTL) of 2,419,200 seconds (28 days),
and cache hits NOT refreshing the TTL of cached values.

Set the environment variables QSV_FP_REDIS_CONNSTR, QSV_REDIS_TTL_SECS and
QSV_REDIS_TTL_REFRESH to change default Redis settings.

Note that the default values are the same as the fetch command, except fetchpost creates the
cache at database 2, as opposed to database 1 with fetch.

If you don't want responses to be cached at all, use the --no-cache flag.

NETWORK OPTIONS:
Fetchpost recognizes RateLimit and Retry-After headers and dynamically throttles requests
to be as fast as allowed. The --rate-limit option sets the maximum number of queries per second
(QPS) to be made. The default is 0, which means to go as fast as possible, automatically
throttling as required, based on rate-limit and retry-after response headers.

To use a proxy, set the environment variables HTTP_PROXY, HTTPS_PROXY or ALL_PROXY
(e.g. export HTTPS_PROXY=socks5://127.0.0.1:1086). Your operating system's own
proxy configuration (macOS System Settings, Windows registry) is also honored;
the environment variables take precedence over it.

qsv fetchpost supports brotli, gzip and deflate automatic decompression for improved throughput
and performance, preferring brotli over gzip over deflate.

Gzip compression of requests bodies is supported with the --compress flag. Note that
public APIs typically do not support gzip compression of request bodies because of the
"zip bomb" vulnerability. This option should only be used with private APIs where this
is not a concern.

It automatically upgrades its connection to the much faster and more efficient HTTP/2 protocol
with adaptive flow control if the server supports it.
See https://www.cloudflare.com/learning/performance/http2-vs-http1.1/ and
https://medium.com/coderscorner/http-2-flow-control-77e54f7fd518 for more info.

URL OPTIONS:
<url-column> needs to be a fully qualified URL path. It can be specified as a column name
from which the URL value will be retrieved for each record, or as the URL literal itself.

JSON RESPONSE HANDLING:
When --jaq is not used, fetchpost parses each successful response with serde_json and
writes it back out (compact by default, or re-indented with --pretty). Object key
order is preserved (qsv enables serde_json's preserve_order feature), but the body
is otherwise normalized: all insignificant whitespace is removed (compact) or
re-indented (--pretty); number representations are canonicalized (e.g. 1e2 -> 100,
leading zeros stripped, exponent form normalized); duplicate keys within a JSON
object are collapsed (last value wins); and responses that are not valid JSON are
written as an empty cell (or the parse error if --store-error is set). If you need
byte-exact server output, post-process the response yourself or use --jaq to
extract specific fields.

EXAMPLES:

data.csv
  URL, zipcode, country
  https://httpbin.org/post, 90210, USA
  https://httpbin.org/post, 94105, USA
  https://httpbin.org/post, 92802, USA

Given the data.csv above, fetch the JSON response.

  $ qsv fetchpost URL zipcode,country data.csv

Note the output will be a JSONL file - with a minified JSON response per line, not a CSV file.

Now, if we want to generate a CSV file with a parsed response - getting only the "form" property,
we use the new-column and jaq options.

  $ qsv fetchpost URL zipcode,country --new-column form --jaq '."form"' data.csv > data_with_response.csv

data_with_response.csv
  URL,zipcode,country,form
  https://httpbin.org/post,90210,USA,"{""country"": String(""USA""), ""zipcode"": String(""90210"")}"
  https://httpbin.org/post,94105,USA,"{""country"": String(""USA""), ""zipcode"": String(""94105"")}"
  https://httpbin.org/post,92802,USA,"{""country"": String(""USA""), ""zipcode"": String(""92802"")}"

Alternatively, since we're using the same URL for all the rows, we can just pass the url directly on the command-line.

  $ qsv fetchpost https://httpbin.org/post 2,3 --new-column form --jaqfile form.jaq data.csv > data_with_formdata.csv

Also note that for the column-list argument, we used the column index (2,3 for second & third column)
instead of using the column names, and we loaded the jaq selector from the form.jaq file.

The form.jaq file simply contains the string literal ".form", including the enclosing double quotes:

form.jaq
  ".form"

USING THE HTTP-HEADER OPTION:

The --http-header option allows you to append arbitrary key value pairs (a valid pair is a key and value
separated by a colon) to the HTTP header (to authenticate against an API, pass custom header fields, etc.).
Note that you can pass as many key-value pairs by using --http-header option repeatedly. For example:

  $ qsv fetchpost https://httpbin.org/post col1-col3 data.csv -H "X-Api-Key:TEST_KEY" -H "X-Api-Secret:ABC123XYZ"

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_fetch.rs.
See also https://github.com/dathere/qsv/wiki/HTTP-and-Web#fetchpost

Usage:
    qsv fetchpost (<url-column>) (<column-list> | --payload-tpl <file>) [--jaq <selector> | --jaqfile <file>] [--http-header <k:v>...] [options] [<input>]
    qsv fetchpost --help

Fetchpost arguments:
    <url-column>               Name of the column with the URL.
                               Otherwise, if the argument starts with `http`, the URL to use.
    <column-list>              Comma-delimited list of columns to insert into the HTTP Post body.
                               Uses `qsv select` syntax - i.e. Columns can be referenced by index or
                               by name if there is a header row (duplicate column names can be disambiguated
                               with more indexing). Column ranges can also be specified. Finally, columns
                               can be selected using regular expressions.
                               See 'qsv select --help' for examples.

Fetchpost options:
    -t, --payload-tpl <file>   Instead of <column-list>, use a MiniJinja template file to render a JSON
                               payload in the HTTP Post body. You can also use --payload-tpl to render
                               a non-JSON payload, but --content-type will have to be set manually.
                               If a rendered JSON is invalid, `fetchpost` will abort and return an error.
    --content-type <arg>       Overrides automatic content types for `<column-list>`
                               (`application/x-www-form-urlencoded`) and `--payload-tpl` (`application/json`).
                               Typical alternative values are `multipart/form-data` and `text/plain`.
                               It is the responsibility of the user to format the payload accordingly
                               when using --payload-tpl.
   -j, --globals-json <file>   A JSON file containing global variables.
                               When posting as an HTML Form, this file is added to the Form data.
                               When constructing a payload using a MiniJinja template, the JSON
                               properties can be accessed in templates using the "qsv_g" namespace
                               (e.g. {{qsv_g.api_key}}, {{qsv_g.base_url}}).
    -c, --new-column <name>    Put the fetched values in a new column. Specifying this option
                               results in a CSV. Otherwise, the output is in JSONL format.
    --jaq <selector>           Apply jaq selector to API returned JSON response.
                               Mutually exclusive with --jaqfile.
    --jaqfile <file>           Load jaq selector from file instead.
                               Mutually exclusive with --jaq.
    --pretty                   Prettify JSON responses. Otherwise, they're minified.
                               If the response is not in JSON format, it's passed through unchanged.
                               Note that --pretty requires the --new-column option.
    --rate-limit <qps>         Rate Limit in Queries Per Second (max: 1000). Note that fetch
                               dynamically throttles as well based on rate-limit and
                               retry-after response headers.
                               Set to 0 to go as fast as possible, automatically throttling as required.
                               CAUTION: Only use zero for APIs that use RateLimit and/or Retry-After headers,
                               otherwise your fetchpost job may look like a Denial Of Service attack.
                               Even though zero is the default, this is mitigated by --max-errors having a
                               default of 10.
                               [default: 0 ]
    --timeout <seconds>        Timeout for each URL request.
                               [default: 30 ]
    --default-encoding <enc>   Fallback character encoding used to decode a response body when
                               the server does NOT send a charset parameter in its Content-Type
                               header. Accepts WHATWG encoding labels, e.g. utf-8, windows-1252,
                               iso-8859-1, shift_jis, euc-jp, koi8-r.
                               When the server DOES send a charset, the server always wins and
                               this option is ignored.
                               [default: utf-8]
    -H, --http-header <k:v>    Append custom header(s) to the HTTP header. Pass multiple key-value pairs
                               by adding this option multiple times, once for each pair. The key and value
                               should be separated by a colon.
    --compress                 Compress the HTTP request body using gzip. Note that most servers do not support
                               compressed request bodies unless they are specifically configured to do so. This
                               should only be enabled for trusted scenarios where "zip bombs" are not a concern.
                               see https://github.com/postmanlabs/httpbin/issues/577#issuecomment-875814469
                               for more info.
    --max-retries <count>      Maximum number of retries per record before an error is raised.
                               [default: 5]
    --max-errors <count>       Maximum number of errors before aborting.
                               Set to zero (0) to continue despite errors.
                               [default: 10 ]
    --store-error              On error, store error code/message instead of blank value.
    --cookies                  Allow cookies.
    --user-agent <agent>       Specify custom user agent. It supports the following variables -
                               $QSV_VERSION, $QSV_TARGET, $QSV_BIN_NAME, $QSV_KIND and $QSV_COMMAND.
                               Try to follow the syntax here -
                               https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
    --report <d|s>             Creates a report of the fetchpost job. The report has the same name as the
                               input file with the ".fetchpost-report" suffix.
                               There are two kinds of report - d for "detailed" & s for "short". The detailed
                               report has the same columns as the input CSV with seven additional columns -
                               qsv_fetchp_url, qsv_fetchp_form, qsv_fetchp_status, qsv_fetchp_cache_hit,
                               qsv_fetchp_retries, qsv_fetchp_elapsed_ms & qsv_fetchp_response.
                               The short report only has the seven columns without the "qsv_fetchp_" prefix.
                               [default: none]

                               CACHING OPTIONS:
    --no-cache                 Do not cache responses.

    --mem-cache-size <count>   Maximum number of entries in the in-memory LRU cache.
                               [default: 2000000]

    --disk-cache               Use a persistent disk cache for responses. The cache is stored in the directory
                               specified by --disk-cache-dir. If the directory does not exist, it will be
                               created. If the directory exists, it will be used as is.
                               It has a default Time To Live (TTL)/lifespan of 28 days and cache hits do not
                               refresh the TTL of cached values.
                               Adjust the QSV_DISKCACHE_TTL_SECS & QSV_DISKCACHE_TTL_REFRESH env vars
                               to change DiskCache settings. A QSV_DISKCACHE_TTL_SECS of 0 disables
                               time-based expiration (entries are cached indefinitely).
    --disk-cache-dir <dir>     The directory <dir> to store the disk cache. Note that if the directory
                               does not exist, it will be created. If the directory exists, it will be used as is,
                               and will not be flushed. This option allows you to maintain several disk caches
                               for different fetchpost jobs (e.g. one for geocoding, another for weather, etc.)
                               [default: ~/.qsv-cache/fetchpost]

    --redis-cache              Use Redis to cache responses. It connects to "redis://127.0.0.1:6379/2"
                               with a connection pool size of 20, with a TTL of 28 days, and a cache hit
                               NOT renewing an entry's TTL.
                               Adjust the QSV_FP_REDIS_CONNSTR, QSV_REDIS_MAX_POOL_SIZE, QSV_REDIS_TTL_SECS &
                               QSV_REDIS_TTL_REFRESH respectively to change Redis settings.
                               A QSV_REDIS_TTL_SECS of 0 disables expiration (entries cached indefinitely).

    --cache-error              Cache error responses even if a request fails. If an identical URL is requested,
                               the cached error is returned. Otherwise, the fetch is attempted again
                               for --max-retries.
    --flush-cache              Flush all the keys in the current cache on startup. This only applies to
                               Disk and Redis caches.

Common options:
    -h, --help                 Display this message
    -o, --output <file>        Write output to <file> instead of stdout.
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. Namely, it will be sorted with the rest
                               of the rows. Otherwise, the first row will always
                               appear as the header row in the output.
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character. (default: ,)
    -p, --progressbar          Show progress bars. Will also show the cache hit rate upon completion.
                               Not valid for stdin.
```
## qsv fill

```text
Fill empty fields in selected columns of a CSV.

This command fills empty fields in the selected column
using the last seen non-empty field in the CSV. This is
useful to forward-fill values which may only be included
the first time they are encountered.

The option `--default <value>` fills all empty values
in the selected columns with the provided default value.
When `--default` is set, it takes precedence over forward-fill
and `--first`, which become no-ops.

The option `--first` fills empty values using the first
seen non-empty value in that column, instead of the most
recent non-empty value in that column.

The option `--backfill` fills empty values at the start of
the CSV with the first valid value in that column. This
requires buffering rows with empty values in the target
column which appear before the first valid value.

The option `--groupby` groups the rows by the specified
columns before filling in the empty values. Using this
option, empty values are only filled with values which
belong to the same group of rows, as determined by the
columns selected in the `--groupby` option.

When both `--groupby` and `--backfill` are specified, and the
CSV is not sorted by the `--groupby` columns, rows may be
re-ordered during output due to the buffering of rows
collected before the first valid value.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_fill.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#fill

Usage:
    qsv fill [options] [--] <selection> [<input>]
    qsv fill --help

fill options:
    -g, --groupby <keys>    Group by specified columns.
    -f, --first             Fill using the first valid value of a column, instead of the latest.
    -b, --backfill          Fill initial empty values with the first valid value.
    -v, --default <value>   Fill using this default value.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv fixedwidth

```text
Converts fixed-width text (fields at fixed byte-column positions, no
delimiters) to CSV.

By default, this expects the input's first line to be a comment enumerating
the 1-based starting byte position of each column, comma-separated and
prefixed with "#" - the same format `qsv table --align leftfwf` produces
(e.g. "#1,10,15"). Every subsequent line is a data record; each field runs
from its starting position up to (but not including) the next column's
starting position, or to the end of the line for the last column. Trailing
whitespace in each field is trimmed.

If the input doesn't have such a header comment - e.g. it comes from an
external system - specify the column positions explicitly with --positions,
or column widths with --widths.

Examples:
    Convert output of `qsv table --align leftfwf` back to CSV:
        qsv table --align leftfwf data.csv | qsv fixedwidth > roundtrip.csv

    Convert a file with explicit 1-based column start positions:
        qsv fixedwidth --positions 1,10,15 mainframe_extract.txt

    Convert a file with explicit column widths instead of positions:
        qsv fixedwidth --widths 9,5,20 mainframe_extract.txt

See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#fixedwidth

Usage:
    qsv fixedwidth [options] [<input>]
    qsv fixedwidth --help

fixedwidth options:
    --positions <arg>      Comma-separated, 1-based starting byte position of
                           each column (e.g. "1,10,15"). Overrides any "#..."
                           header comment in the input.
    --widths <arg>         Comma-separated width, in bytes, of each column
                           (e.g. "9,5,20"). An alternative to --positions;
                           the two are mutually exclusive.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
```
## qsv fixlengths

```text
Transforms CSV data so that all records have the same length. The length is
the length of the longest record in the data (not counting trailing empty fields,
but at least 1). Records with smaller lengths are padded with empty fields.

This requires two complete scans of the CSV data: one for determining the
record size and one for the actual transform. Because of this, the input
given must be a file and not stdin.

Alternatively, if --length is set, then all records are forced to that length.
This requires a single pass and can be done with stdin.

See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#fixlengths

Usage:
    qsv fixlengths [options] [<input>]
    qsv fixlengths --help

fixlengths options:
    -l, --length <arg>     Forcefully set the length of each record. If a
                           record is not the size given, then it is truncated
                           or expanded as appropriate.
    -r, --remove-empty     Remove empty columns.
    -i, --insert <pos>     If empty fields need to be inserted, insert them
                           at <pos>. If <pos> is zero, then it is inserted
                           at the end of each record. If <pos> is negative, it
                           is inserted from the END of each record going backwards.
                           If <pos> is positive, it is inserted from the BEGINNING
                           of each record going forward. [default: 0]
    --quote <arg>          The quote character to use. [default: "]
    --escape <arg>         The escape character to use. When not specified,
                           quotes are escaped by doubling them.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -q, --quiet            Don't print removed column information.
```
## qsv flatten

```text
Prints flattened records such that fields are labeled separated by a new line.
This mode is particularly useful for viewing one record at a time. Each
record is separated by a special '#' character (on a line by itself), which
can be changed with the --separator flag.

There is also a condensed view (-c or --condense) that will shorten the
contents of each field to provide a summary view.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_flatten.rs.
See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#flatten

Usage:
    qsv flatten [options] [<input>]
    qsv flatten --help

flatten options:
    -c, --condense <arg>          Limits the length of each field to the value
                                  specified. If the field is UTF-8 encoded, then
                                  <arg> refers to the number of code points.
                                  Otherwise, it refers to the number of bytes.
    -f, --field-separator <arg>   A string of characters to write between a column name
                                  and its value.
    -s, --separator <arg>         A string of characters to write after each record.
                                  When non-empty, a new line is automatically
                                  appended to the separator.
                                  [default: #]

Common options:
    -h, --help             Display this message
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. When set, the name of each field
                           will be its index.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv fmt

```text
Formats CSV data with a custom delimiter or CRLF line endings.

Generally, all commands in qsv output CSV data in a default format, which is
the same as the default format for reading CSV data. This makes it easy to
pipe multiple qsv commands together. However, you may want the final result to
have a specific delimiter or record separator, and this is where 'qsv fmt' is
useful.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_fmt.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#fmt

Usage:
    qsv fmt [options] [<input>]
    qsv fmt --help

fmt options:
    -t, --out-delimiter <arg>  The field delimiter for writing CSV data.
                               Must be a single character.
                               "T" or "\t" can be used as shortcuts for tab.
                               [default: ,]
    --crlf                     Use '\r\n' line endings in the output.
    --ascii                    Use ASCII field/record separators: Unit Separator
                               (U+001F) for fields and Record Separator (U+001E)
                               for records. Substitute (U+001A) is used as the
                               quote character.
    --quote <arg>              The quote character to use. Must be a single
                               character. [default: "]
    --quote-always             Put quotes around every value.
    --quote-never              Never put quotes around any value.
    --escape <arg>             The escape character to use. When not specified,
                               quotes are escaped by doubling them.
    --no-final-newline         Do not write a newline at the end of the output.
                               This makes it easier to paste the output into Excel.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv foreach

```text
Execute a shell command once per record in a given CSV file.

NOTE: Windows users are recommended to use Git Bash as their terminal when
running this command. Download it from https://git-scm.com/downloads. When installing,
be sure to select "Use Git from the Windows Command Prompt" to ensure that the
necessary Unix tools are available in the terminal.

WARNING: This command can be dangerous. Be careful when using it with
untrusted input.

Or per @thadguidry: 😉
Please ensure when using foreach to use trusted arguments, variables, scripts, etc.
If you don't do due diligence and blindly use untrusted parts... foreach can indeed
become a footgun and possibly fry your computer, eat your lunch, and expose an entire
datacenter to a cancerous virus in your unvetted batch file you grabbed from some
stranger on the internet that runs...FOR EACH LINE in your CSV file. GASP!"

Examples:

Delete all files whose filenames are listed in the filename column:

  $ qsv foreach filename 'rm {}' assets.csv

Execute a command that outputs CSV once per record without repeating headers:

  $ qsv foreach query --unify 'search --year 2020 {}' queries.csv > results.csv

Same as above but with an additional column containing the current value:

  $ qsv foreach query -u -c from_query 'search {}' queries.csv > results.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_foreach.rs.
See also https://github.com/dathere/qsv/wiki/Scripting-Luau-Python#foreach

If any child command exits with a non-zero status, foreach finishes processing
all rows but then exits with a non-zero status of its own.

Usage:
    qsv foreach [options] <column> <command> [<input>]
    qsv foreach --help

foreach arguments:
    column      The column whose value is substituted into the command.
                Only a single column is accepted.
    command     The command to execute. Use "{}" to substitute the value
                of the current input file line. The command must be
                non-empty after whitespace trimming.
                If you need to execute multiple commands, use a shell
                script. See foreach_multiple_commands_with_shell_script()
                in tests/test_foreach.rs for an example.
    input       The CSV file to read. If not provided, will read from stdin.

foreach options:
    -u, --unify                If the output of the executed command is a CSV,
                               unify the result by skipping headers on each
                               subsequent command. Does not work when --dry-run is true.
                               The first child's CSV header row becomes canonical;
                               later children are expected to produce the same schema.
    -c, --new-column <name>    If unifying, add a new column with given name
                               and copying the value of the current input file line.
    --dry-run <file|boolean>   If set to true (the default for safety reasons), the commands are
                               sent to stdout instead of executing them.
                               If set to a file, the commands will be written to the specified
                               text file instead of executing them. The file is only created
                               after all flag validation succeeds, so a conflicting flag
                               combination will not truncate an existing file.
                               Only if set to false will the commands be actually executed.
                               [default: true]

Common options:
    -h, --help             Display this message
    -n, --no-headers       When set, the file will be considered to have no
                           headers.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -p, --progressbar      Show progress bars. Not valid for stdin.
```
## qsv frequency

```text
Compute a frequency distribution table on input data. It has CSV and JSON output modes.
https://en.wikipedia.org/wiki/Frequency_(statistics)#Frequency_distribution_table

In CSV output mode (default), the table is formatted as CSV data with the following
columns - field,value,count,percentage,rank.

The rank column is 1-based and is calculated based on the count of the values,
with the most frequent having a rank of 1. In case of ties, the rank is calculated
based on the rank-strategy option - "dense" (default), "min", "max", "ordinal", or "average".

Only the top N values (set by the --limit option) are computed, with the rest of the values
grouped into an "Other" category with a special rank of 0. The "Other" category includes
the count of remaining unique values that are not in the top N values.

In JSON output mode, the table is formatted as nested JSON data. In addition to
the columns above, the JSON output also includes the row count, field count, rank-strategy,
each field's data type, cardinality, nullcount, sparsity, uniqueness_ratio and its stats.

Since this command computes an exact frequency distribution table, memory proportional
to the cardinality of each column would be normally required.

However, this is problematic for columns with ALL unique values (e.g. an ID column),
as the command will need to allocate memory proportional to the column's cardinality.

To overcome this, the frequency command uses several mechanisms:

STATS CACHE:
If the stats cache exists for the input file, it is used to get column cardinality information.
This short-circuits frequency compilation for columns with all unique values (i.e. where
rowcount == cardinality), eliminating the need to maintain an in-memory hashmap for ID columns.
This allows `frequency` to handle larger-than-memory datasets with the added benefit of also
making it faster when working with datasets with ID columns.

That's why for MAXIMUM PERFORMANCE, it's HIGHLY RECOMMENDED to create an index (`qsv index data.csv`)
and pre-populate the stats cache (`qsv stats data.csv --cardinality --stats-jsonl`)
BEFORE running `frequency`.

MEMORY-AWARE CHUNKING:
When working with large datasets, memory-aware chunking is automatically enabled. Chunk size
is dynamically calculated based on available memory and record sampling.

You can override this behavior by setting the QSV_FREQ_CHUNK_MEMORY_MB environment variable.
(set to 0 for dynamic sizing, or a positive number for a fixed memory limit per chunk,
or any non-u64 value (e.g. -1 or "auto") for CPU-based chunking (1 chunk = num records/number of
CPUs)), or by setting the --jobs option.

"COMPLETE" FREQUENCY TABLES FOR ID COLUMNS:
By default, ID columns will have an `<ALL UNIQUE>` value with count equal to
rowcount and percentage set to 100 with a rank of 0. This is done by using the
stats cache to fetch each column's cardinality - allowing qsv to short-circuit
frequency compilation and eliminate the need to maintain a hashmap for ID columns.
The stats cache counts untrimmed values, so if trimming changes any value in such
a column (e.g. " a" and "a" would merge), that column is counted in full instead,
and a message names it.

If you wish to compile a "complete" frequency table even for ID columns, set
QSV_STATSCACHE_MODE to "none". This will force the frequency command to compute
frequencies for all columns regardless of cardinality, even for ID columns.

In this case, the unique limit (--unq-limit) option is particularly useful when
a column has all unique values  and --limit is set to 0.
Without a unique limit, the frequency table for that column will be the same as
the number of rows in the data.
With a unique limit, the frequency table will be a sample of N unique values,
all with a count of 1.

The --lmt-threshold option also allows you to apply the --limit and --unq-limit
options only when the number of unique items in a column >= threshold.
This is useful when you want to apply limits only to columns with a large number
of unique items and not to columns with a small number of unique items.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_frequency.rs.
See also https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#frequency

Usage:
    qsv frequency [options] [<input>]
    qsv frequency --help

frequency options:
    -s, --select <arg>      Select a subset of columns to compute frequencies
                            for. See 'qsv select --help' for the format
                            details. This is provided here because piping 'qsv
                            select' into 'qsv frequency' will disable the use
                            of indexing.
    -l, --limit <arg>       Limit the frequency table to the N most common
                            items. Set to '0' to disable a limit.
                            If negative, only return values with an occurrence
                            count >= absolute value of the negative limit.
                            e.g. --limit -2 will only return values with an
                            occurrence count >= 2.
                            [default: 10]
    --sketch-method <m>     Algorithm used to compute the frequency table.
                            Choices: 'exact' (default) tracks every distinct value
                            in a HashMap; 'frequent_items' uses the Apache
                            DataSketches Frequent Items (Misra-Gries) sketch to
                            track top-K heavy hitters with bounded error and
                            constant memory. The frequent_items mode rejects
                            asc, weight, ignore-case, no-trim, other-sorted,
                            null-sorted, frequency-jsonl, stats-filter, and
                            json/pretty-json/toon output; the frequency cache is
                            bypassed. Counts are estimates. The flags
                            rank-strategy, lmt-threshold, and unq-limit are
                            silently ignored under this mode (the sketch's
                            natural ordering is top-K by estimate descending;
                            tied counts use the sketch's hash-table iteration
                            order). The 'Other' row format diverges from exact:
                            label is the bare other-text (no unique-count suffix
                            since the sketch cannot recover the true count of
                            items not in the top-K); rank is 0 to match the
                            exact convention. Its count is approximate.
                            NULLs are counted exactly, outside the sketch, and
                            are reported as in exact mode (after "Other").
                            Note: 'frequent_items' requires a little-endian
                            target. Apache DataSketches does not support
                            big-endian platforms (e.g., s390x); on those
                            builds, this choice is rejected.
                            [default: exact]
    --sketch-map-size <n>   Maximum map size for the Frequent Items sketch.
                            Must be a power of two and at least 8. Larger values
                            tighten error bounds at the cost of more memory.
                            Only used when sketch-method is frequent_items.
                            [default: 4096]
    -u, --unq-limit <arg>   If a column has all unique values, limit the
                            frequency table to a sample of N unique items.
                            Set to '0' to disable a unique_limit.
                            Only applies in unweighted mode; ignored when --weight is set.
                            [default: 10]
    --lmt-threshold <arg>   The threshold for which --limit and --unq-limit
                            will be applied. If the number of unique items
                            in a column >= threshold, the limits will be applied.
                            Set to '0' to disable the threshold and always apply limits.
                            [default: 0]
-r, --rank-strategy <arg>   The strategy to use when there are count-tied values in the frequency table.
                            See https://en.wikipedia.org/wiki/Ranking for more info.
                            Valid values are:
                              * dense: Assigns consecutive integers regardless of ties,
                                incrementing by 1 for each new count value (AKA "1223" ranking).
                              * min: Tied items receive the minimum rank position (AKA "1224" ranking).
                              * max: Tied items receive the maximum rank position (AKA "1334" ranking).
                              * ordinal: The next rank is the current rank plus 1 (AKA "1234" ranking).
                              * average: Tied items receive the average of their ordinal positions
                                (AKA "1 2.5 2.5 4" ranking).
                            Note that tied values with the same rank are sorted alphabetically.
                            [default: dense]
    --pct-dec-places <arg>  The number of decimal places to round the percentage to.
                            If negative, the number of decimal places will be set
                            automatically to the minimum number of decimal places needed
                            to represent the percentage accurately, up to the absolute
                            value of the negative number.
                            [default: -5]
    --other-sorted          By default, the "Other" category is placed at the
                            end of the frequency table for a field. If this is enabled, the
                            "Other" category will be sorted with the rest of the
                            values by count.
    --other-text <arg>      The text to use for the "Other" category. If set to the
                            literal string "<NONE>" (case-sensitive, exact match), the
                            "Other" category will not be included in the frequency table.
                            [default: Other]
    --no-other              Don't include the "Other" category in the frequency table.
                            This is equivalent to --other-text "<NONE>".
    --null-sorted           By default, the NULL category (controlled by --null-text)
                            is placed at the end of the frequency table for a field,
                            after "Other" if present. If this is enabled, the NULL
                            category will be sorted with the rest of the values by count.
    -a, --asc               Sort the frequency tables in ascending order by count.
                            The default is descending order. Note that this option will
                            also reverse ranking - i.e. the LEAST frequent values will
                            have a rank of 1.
    --no-trim               Don't trim whitespace from values when computing frequencies.
                            The default is to trim leading and trailing whitespaces.
    --null-text <arg>       The text to use for NULL values. If set to the literal
                            string "<NONE>" (case-sensitive, exact match), NULLs
                            will not be included in the frequency table
                            (equivalent to --no-nulls).
                            [default: (NULL)]
    --no-nulls              Don't include NULLs in the frequency table.
                            This is equivalent to --null-text "<NONE>".
    --pct-nulls             Include NULL values in percentage and rank calculations.
                            When disabled (default), percentages are "valid percentages"
                            calculated with NULLs excluded from the denominator, and
                            NULL entries display empty percentage and rank values.
                            When enabled, NULLs are included in the denominator
                            (original behavior).
                            Has no effect when --no-nulls is set.
    -i, --ignore-case       Ignore case when computing frequencies.
                            The stats cache's cardinality is case-sensitive,
                            so it cannot prove that case-folded values are
                            unique. All-unique columns are therefore counted
                            in full instead of being short-circuited to
                            <ALL_UNIQUE> - except Integer columns, which have
                            no letters to fold (unless trimming changes one
                            of their values). On large files with all-unique
                            text columns (e.g. emails), this can use memory
                            proportional to the row count. Exclude such
                            columns with -s if you don't need them.
    --no-float <cols>       Exclude Float columns from frequency analysis.
                            Floats typically contain continuous values where
                            frequency tables are not meaningful.
                            To exclude ALL Float columns, use --no-float "*"
                            To exclude Floats except specific columns, specify
                            a comma-separated list of Float columns to INCLUDE.
                            e.g. "--no-float *" excludes all Floats
                                 "--no-float price,rate" excludes Floats
                                    except 'price' and 'rate'
                            Requires stats cache for type detection.
    --stats-filter <expr>   Filter columns based on their statistics using a Luau expression.
                            Columns where the expression evaluates to `true` are EXCLUDED.
                            Available fields: field, type, is_ascii, cardinality, nullcount,
                            sum, min, max, range, sort_order, min_length, max_length, mean,
                            stddev, variance, cv, sparsity, q1, q2_median, q3, iqr, mad,
                            skewness, mode, antimode, n_negative, n_zero, n_positive, etc.
                            e.g. "nullcount > 1000" - exclude columns with many nulls
                                 "type == 'Float'" - exclude Float columns
                                 "cardinality > 500 and nullcount > 0" - compound expression
                            Requires stats cache and the "luau" feature.
   --all-unique-text <arg>  The text to use for the "<ALL_UNIQUE>" category.
                            [default: <ALL_UNIQUE>]
    --vis-whitespace        Visualize whitespace characters in the output. See
                            https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#whitespace-markers
                            for the list of whitespace markers.
    -j, --jobs <arg>        The number of jobs to run in parallel when the given CSV data has
                            an index. Note that a file handle is opened for each job.
                            When not set, defaults to the number of CPUs detected.

                            FREQUENCY CACHE OPTIONS:
    --frequency-jsonl       Write the complete frequency distribution as a
                            JSONL cache file (FILESTEM.freq.csv.data.jsonl).
                            Requires a non-stdin input file. The cache contains
                            metadata and per-column frequency data.
                            ALL_UNIQUE columns (rowcount == cardinality) get a single
                            ALL_UNIQUE sentinel. HIGH_CARDINALITY columns (cardinality
                            exceeds the smaller of --high-card-threshold/--high-card-pct
                            of rowcount) get a single HIGH_CARDINALITY sentinel.
                            Columns with any value that is not valid UTF-8 get
                            a single NON_UTF8 sentinel, since the cache stores
                            values as UTF-8 text. HIGH_CARDINALITY and NON_UTF8
                            columns are recomputed when the cache is reused.
                            When a valid (fresh) cache already exists, frequency will
                            automatically reuse it instead of recomputing from the CSV.
                            Use --force to regenerate the cache even when it is valid.
                            Cache is NOT used when --ignore-case, --no-trim, or --weight
                            are active, as these change how values are computed.
    --high-card-threshold <arg>  Absolute cardinality threshold for HIGH_CARDINALITY
                                 classification in the frequency cache.
                                 Can also be set with QSV_FREQ_HIGH_CARD_THRESHOLD env var
                                 (env var takes precedence when CLI value equals the default).
                                 Only used with --frequency-jsonl.
                                 [default: 100]
    --high-card-pct <arg>   Percentage of rowcount threshold for HIGH_CARDINALITY
                            classification in the frequency cache. Must be between 1 and 100.
                            Can also be set with QSV_FREQ_HIGH_CARD_PCT env var
                            (env var takes precedence when CLI value equals the default).
                            Only used with --frequency-jsonl.
                            [default: 90]
    --force                 Force recomputation even when a valid frequency cache
                            exists, bypassing the auto-reuse path. Also regenerates
                            the cache when combined with --frequency-jsonl.

                            JSON OUTPUT OPTIONS:
    --json                  Output frequency table as nested JSON instead of CSV.
                            The JSON output includes additional metadata: row count, field count,
                            data type, cardinality, null count, sparsity, uniqueness_ratio and
                            17 additional stats (e.g. sum, min, max, range, sort_order, mean, sem, etc.).
    --pretty-json           Same as --json but pretty prints the JSON output.
    --toon                  Output frequency table and select stats in TOON format instead of CSV.
                            TOON is a compact, human-readable encoding of the JSON data model for LLM prompts.
                            See https://toonformat.dev/ for more info.
    --no-stats              When using the JSON or TOON output mode, do not include the additional stats.
    --weight <column>       Compute weighted frequencies using the specified column as weights.
                            The weight column must be numeric. When specified, frequency counts
                            are multiplied by the weight value for each row. The weight column is
                            automatically excluded from frequency computation. Missing or
                            unparsable weights default to 1.0. Zero, negative, NaN and infinite
                            weights are ignored and do not contribute to frequencies.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will NOT be included
                           in the frequency table. Additionally, the 'field'
                           column will be 1-based indices instead of header
                           names.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    --flexible             Allow records with a varying number of fields.
                           Without this, a "ragged" record (one with more or
                           fewer fields than the header) is an error. With it,
                           extra fields are ignored and a SHORT record
                           contributes no value at all for its missing
                           columns (not even a null), so those columns are counted
                           fewer times. Note that field selection stops at the
                           first missing column, so an out-of-order selection
                           (e.g. `3,1`) makes a short record skip columns that
                           ARE present.
    --memcheck             Use CONSERVATIVE heuristics for the in-memory load
                           check (file size vs. available + free_swap × platform
                           factor − headroom), instead of the default NORMAL
                           check (file size vs. total memory − headroom). The
                           CONSERVATIVE check is stricter and trips OOM far
                           more readily. (See also: QSV_MEMORY_CHECK env var,
                           equivalent to passing --memcheck.)
                           Independently of this flag, the in-memory load
                           check runs whenever frequency takes the
                           non-parallel path. On OOM (in either NORMAL or
                           CONSERVATIVE mode), qsv auto-creates an index when
                           no index exists (skipped for stdin) AND switches
                           to the Frequent Items sketch (Apache DataSketches
                           Misra-Gries, equivalent to `--sketch-method
                           frequent_items`) where compatible. The sketch
                           fallback can also fire when an index is already
                           present and the OOM still trips (e.g., when jobs
                           is pinned to 1 on a pre-indexed file). A wwarn is
                           emitted when the sketch fallback engages.
```
## qsv get

```text
Get tabular data from various sources into a managed, queryable disk cache.

`get` fetches a resource once, stores it compressed (zstd) and content-addressed
(BLAKE3) in the qsv cache, auto-builds a qsv index for it (for instant random
access & exact record counts), and records rich metadata (ETag, Last-Modified,
sizes, record count, TTL). Re-fetches send a conditional request
(ETag/Last-Modified) so unchanged resources are revalidated, not re-downloaded.
Large remote resources stream into the cache as parallel byte-ranges (tune with
the QSV_GET_PART_SIZE and QSV_GET_CONCURRENCY env vars).

Once cached, a resource can be read by ANY qsv command using the `dc:` prefix,
e.g. `qsv stats dc:data.csv`. Stale `dc:` entries are auto-refreshed.

A glob (e.g. data/*.csv) or directory source fetches every matching tabular file
(.csv/.tsv/.tab/.ssv) — supported for local paths and (with the get_cloud feature)
cloud buckets/prefixes. --name is ignored when a source expands to multiple files.

Supported sources:
    local file path, directory, or glob (e.g. /data/*.csv)
    http:// or https:// URL
    dathere://<path>          datHere qsv-lookup-tables repo
    ckan://<id>               a CKAN resource by id
    ckan://<name>?            a CKAN resource by name (resource_search)
    s3://<bucket>/<key>       AWS S3 / S3-compatible       (get_cloud feature)
    gs://<bucket>/<key>       Google Cloud Storage         (get_cloud feature)
    az://<container>/<key>    Azure Blob Storage           (get_cloud feature)
Cloud credentials are read from the standard AWS_*/AZURE_*/GOOGLE_* environment
variables (and IAM roles); use --cloud-opt for one-off overrides such as region
or endpoint. (sftp:// is planned for a later release.)

`--sample` PREVIEW vs the `sample` command: `get --sample N` is a cheap PEEK — it
streams just the first N rows from the head (stopping early, so a huge remote file
is barely touched) and caches nothing. It is NOT a statistical sample. For a random,
representative subset use `qsv sample` instead (which downloads the whole remote
file first, except for its streaming --bernoulli method).

Examples:
    Fetch a CSV into the cache and read it back with another command:
        $ qsv get https://example.com/data.csv --name data.csv
        $ qsv stats dc:data.csv

    Peek at a remote CSV WITHOUT caching it (preview mode, streams to stdout):
        $ qsv get https://example.com/big.csv --sample 10
        $ qsv get https://example.com/big.csv --offset 500 --sample 10
        $ qsv get https://example.com/big.csv --sample 20 --random

    Seed a CKAN reference table:
        $ qsv get "ckan://covid-vaccinations?" --name vax.csv

    Fetch every matching file via a glob or directory (each is cached separately):
        $ qsv get '/data/*.csv'
        $ qsv get /data/

    Fetch from cloud object storage (requires the get_cloud feature):
        $ qsv get s3://my-bucket/data.csv --name data.csv
        $ qsv get gs://my-bucket/data.csv --cloud-opt skip_signature=true
        $ qsv get 's3://my-bucket/exports/*.csv'

    Show what's in the cache, then prune old entries:
        $ qsv get cache-list
        $ qsv get cache-prune --older-than=30d

    Export an already-cached entry to a file or stdout (offline; no re-fetch):
        $ qsv get cache-fetch data.csv --output /tmp/data.csv
        $ qsv get cache-fetch data.csv | qsv stats

    Verify cached blob integrity, then retune an entry's TTL & policy:
        $ qsv get cache-list --verify
        $ qsv get cache-set-ttl data.csv --ttl=86400
        $ qsv get cache-set-policy data.csv --refresh=never

    The `dc:` handle prefix is accepted (and ignored) wherever a cached <name> is
    expected, so a `dc:` reference copied from another command works as-is:
        $ qsv get cache-fetch dc:data.csv --output /tmp/data.csv
        $ qsv get cache-set-ttl dc:data.csv --ttl=86400
        $ qsv get cache-set-policy dc:data.csv --refresh=never

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_get.rs.

Usage:
    qsv get cache-list [--verify] [options]
    qsv get cache-info [options]
    qsv get cache-fetch <name> [options]
    qsv get cache-clear [options]
    qsv get cache-prune --older-than=<val> [options]
    qsv get cache-set-ttl <name> --ttl=<secs> [options]
    qsv get cache-set-policy <name> --refresh=<policy> [options]
    qsv get [--cloud-opt <kv>...] [options] <source>...
    qsv get --help

get arguments:
    <source>...            One or more sources to fetch into the cache.
    <name>                 For cache-fetch / cache-set-ttl / cache-set-policy: the
                           cached logical name (`dc:` handle) to read or modify.
                           A leading `dc:` prefix is accepted and ignored.

cache-fetch writes an ALREADY-cached entry's (decompressed) contents to the --output
file (or stdout if omitted or `-`). It is offline: it reads the cached blob directly and
never re-fetches the source. Errors if <name> is not in the cache.

get options:
    --name <name>          Logical cache name (the `dc:` handle) for the fetched
                           entry. Defaults to the source's terminal path segment.
                           Ignored when multiple sources are given.
    --ttl <secs>           Per-entry time-to-live in seconds. -1 = never expire.
                           Also the value applied by cache-set-ttl. [default: 2419200]
    --refresh <policy>     Revalidation policy for `dc:` use: on-stale, always or never.
                           A `dc:` input re-fetches only past TTL; `always` does not
                           change that - it only makes that fetch unconditional,
                           skipping If-None-Match/If-Modified-Since revalidation.
                           Also the value applied by cache-set-policy. [default: on-stale]
    --compress <algo>      Transparent blob compression: zstd or none.
                           [default: zstd]
    --force                Re-fetch even if a fresh cached copy exists.
    --sample <n>           PREVIEW: stream the first N data records of <source> to
                           stdout (or the --output file) WITHOUT caching. No `dc:`
                           entry is created. The sniffed header row is re-attached.
                           Single <source> only.
    --offset <mb>          PREVIEW: skip ~<mb> megabytes (via an HTTP Range request)
                           before sampling, realigning to the next record boundary.
                           Implies --sample. Requires a Range-capable source.
    --random               PREVIEW: random (reservoir) sampling. Streams the full
                           source and parses it from the start, so quoted multi-line
                           records stay intact. Slower than --sample (which only
                           reads the head); use it when you need a uniform sample.
    --cloud-opt <kv>       Extra cloud object-store config as a `key=value` pair
                           (repeatable), e.g. region=us-east-1 or
                           skip_signature=true. Overrides the
                           AWS_*/AZURE_*/GOOGLE_* environment. (get_cloud only)
    --ckan-api <url>       CKAN Action API base URL. Overrides the QSV_CKAN_API
                           env var. [default: https://data.dathere.com/api/3/action]
    --ckan-token <token>   CKAN API token. Overrides the QSV_CKAN_TOKEN env var.
    --timeout <secs>       HTTP timeout in seconds. For cache downloads this is an INACTIVITY
                           timeout: the transfer aborts only if no data is received from the
                           server for this long, so a slow-but-steady download is NOT cut off.
                           Preview mode (--sample / --offset / --random) instead uses it as a
                           total-request timeout. 0 = no timeout. [default: 60]
    --older-than <val>     For cache-prune: remove entries older than this age.
                           Accepts seconds, or a value with an s/m/h/d/w suffix
                           (e.g. 3600, 90m, 30d, 2w).
    --json                 For cache-list/cache-info: output JSON instead of a table.
    --verify               For cache-list: recompute each cached blob's BLAKE3 and
                           report OK/FAIL per name (exits non-zero on any failure).

Common options:
    -h, --help             Display this message
    --cache-dir <dir>      The qsv cache directory.
                           If the QSV_CACHE_DIR envvar is set, it will be used instead.
                           The cache itself (its get/ subdirectory) is readable
                           by you only.
                           [default: ~/.qsv-cache]
    -o, --output <file>    For a single <source> (or cache-fetch <name>), write the
                           (decompressed) data to <file> (use `-` for stdout).
    -q, --quiet            Do not print progress/summary messages to stderr.
```
## qsv geocode

```text
Geocodes a location in CSV data using one of five geocoders:
 * Geonames  - OFFLINE. Matches partial city names, WGS-84 coordinates and country codes
               against a local, updatable index of Geonames cities, downloaded
               automatically on first use. Multithreaded and cached.
 * GeoIP2    - OFFLINE. Locates IP addresses and URLs using a local copy of the MaxMind
               GeoLite2 City database, which you download manually.
 * OpenCage  - ONLINE. Worldwide forward geocoding of free-form street addresses and
               reverse geocoding of coordinates, using the OpenCage API. Requires an
               OpenCage API key.
 * Geoclient - ONLINE. Geocodes New York City addresses, BBLs, BINs, intersections and
               places using NYC's Geoclient API, returning NYC-specific attributes such
               as council districts and census tracts. Requires a free NYC API key.
 * Census    - ONLINE. Geocodes US addresses and coordinates using the free, keyless US
               Census Geocoder, returning Census geographies (state, county, tract,
               block group and block GEOIDs, and more) for Census data enrichment.

The major subcommands are:
 * suggest      - (Geonames) given a partial city name, return the closest city.
 * reverse      - (Geonames) given a WGS-84 coordinate, return the nearest city.
 * countryinfo  - (Geonames) given an ISO 3166-1 alpha-2 country code, return the
                  country's information.
 * iplookup     - (GeoIP2) given an IP address or URL, return its city.
 * opencage     - (OpenCage) forward or reverse geocode an address or coordinate.
 * geoclient    - (Geoclient) geocode a New York City location.
 * census       - (Census) geocode a US address or coordinate.
 * index-*      - manage the local Geonames cities index.
                  (index-check, index-update, index-load & index-reset)
 * cache-*      - manage the persistent on-disk OpenCage, Geoclient and Census result
                  caches.
                  (cache-clear, cache-prune & cache-info)

Each geocoding subcommand has a "now" variant - suggestnow, reversenow, countryinfonow,
iplookupnow, opencagenow, geoclientnow and censusnow - that geocodes a single location
given on the command line instead of a CSV column.

### Geonames
The suggest, reverse and countryinfo subcommands use a local Geonames cities index. Two
prebuilt, English-only indexes, built from the Geonames Gazetteer cities files, are
distributed on the qsv GitHub repo:

 * cities15000 - cities with populations > 15,000 (about ~26k cities). The default.
 * cities1000  - cities with populations > 1,000 (about ~140k cities). Resolves small
                 towns the default omits, at ~4x the index size.

The first time you run one of these subcommands, qsv downloads the default cities15000
index and uses it going forward. To switch to cities1000, run `qsv geocode index-load 1000`.
See https://download.geonames.org/export/dump/ for more information.
Use the index-* operations (see "index-* operations" below) to update the index, rebuild it
with other languages or more cities, or load another one.

#### suggest
Suggest a Geonames city based on a partial city name. It returns the closest Geonames
city record based on the Jaro-Winkler distance between the partial city name and the
Geonames city name.

The geocoded information is formatted based on --formatstr, returning it in
'%location' format (i.e. "(lat, long)") if not specified.

Use the --new-column option if you want to keep the location column, e.g.

Geocode file.csv city column and set the geocoded value to a new column named lat_long.

  $ qsv geocode suggest city --new-column lat_long file.csv

Limit suggestions to the US, Canada and Mexico.

  $ qsv geocode suggest city --country us,ca,mx file.csv

Limit suggestions to New York State and California, with matches in New York state
having higher priority as its listed first.

  $ qsv geocode suggest city --country us --admin1 "New York,US.CA" file.csv

If we use admin1 codes, we can omit --country as it will be inferred from the admin1 code prefix.

  $ qsv geocode suggest city --admin1 "US.NY,US.CA" file.csv

Geocode file.csv city column with --formatstr=%state and set the
geocoded value a new column named state.

  $ qsv geocode suggest city --formatstr %state --new-column state file.csv

Use dynamic formatting to create a custom format.

  $ qsv geocode suggest city -f "{name}, {admin1}, {country} in {timezone}" file.csv

Using French place names. You'll need to rebuild the index with the --languages option first

  $ qsv geocode suggest city -f "{name}, {admin1}, {country} in {timezone}" -l fr file.csv

#### suggestnow
Accepts the same options as suggest, but does not require an input file.
Its default format is more verbose - "{name}, {admin1} {country}: {latitude}, {longitude}"

  $ qsv geocode suggestnow "New York"
  $ qsv geocode suggestnow --country US -f %cityrecord "Paris"
  $ qsv geocode suggestnow --admin1 "US.OH" "Athens"

#### reverse
Reverse geocode a WGS 84 coordinate to the nearest City. It returns the closest Geonames
city record based on the Euclidean distance between the coordinate and the nearest city.
It accepts "lat, long" or "(lat, long)" format.

The geocoded information is formatted based on --formatstr, returning it in
'%city-admin1' format if not specified, e.g.

Reverse geocode file.csv LatLong column. Set the geocoded value to a new column named City.

  $ qsv geocode reverse LatLong -c City file.csv

Reverse geocode file.csv LatLong column and set the geocoded value to a new column
named CityState, output to a file named file_with_citystate.csv.

  $ qsv geocode reverse LatLong -c CityState file.csv -o file_with_citystate.csv

The same as above, but get the timezone instead of the city and state.

  $ qsv geocode reverse LatLong -f %timezone -c tz file.csv -o file_with_tz.csv

#### reversenow
Accepts the same options as reverse, but does not require an input file.

  $ qsv geocode reversenow "40.71427, -74.00597"
  $ qsv geocode reversenow --country US -f %cityrecord "40.71427, -74.00597"
  $ qsv geocode reversenow "(39.32924, -82.10126)"

#### countryinfo
Returns the country information for the specified ISO-3166 2-letter country code.

  $ qsv geocode countryinfo country_col data.csv
  $ qsv geocode countryinfo --formatstr "%json" country_col data.csv
  $ qsv geocode countryinfo -f "%continent" country_col data.csv
  $ qsv geocode countryinfo -f "{country_name} ({fips}) in {continent}" country_col data.csv

#### countryinfonow
Accepts the same options as countryinfo, but does not require an input file.

  $ qsv geocode countryinfonow US
  $ qsv geocode countryinfonow --formatstr "%pretty-json" US
  $ qsv geocode countryinfonow -f "%continent" US
  $ qsv geocode countryinfonow -f "{country_name} ({fips}) in {continent}" US

#### index-* operations
Manage the local Geonames cities index used by the Geonames and GeoIP2 subcommands.

It has four operations:
 * check  - checks if the local Geonames index is up-to-date compared to the Geonames website.
            returns the index file's metadata JSON to stdout.
 * update - updates the local Geonames index with the latest changes from the Geonames website.
            use this command judiciously as it downloads about ~200mb of data from Geonames
            and rebuilds the index from scratch using the --languages option.
            If you don't need a language other than English, use the index-load subcommand instead
            as it's faster and will not download any data from Geonames.
 * reset  - resets the local Geonames index to the default prebuilt, English-only Geonames cities
            index (cities15000) - downloading it from the qsv GitHub repo for the current qsv version.
 * load   - load a Geonames cities index from a file, making it the default index going forward.
            If set to a published population floor (15000 or 1000), it will download that
            prebuilt English-only Geonames index rkyv file from the qsv GitHub repo for the
            current qsv version. cities1000 (~140k cities) resolves small towns the default
            cities15000 (~26k) omits, at ~4x the index size.

Update the Geonames cities index with the latest changes.

  $ qsv geocode index-update

Rebuild the index using the latest Geonames data w/ English, French, German & Spanish place names

  $ qsv geocode index-update --languages en,fr,de,es

Load an alternative Geonames cities index from a file, making it the default index going forward.

  $ qsv geocode index-load my_geonames_index.rkyv

### GeoIP2
The iplookup subcommand locates an IP address - or the IP address a URL's host resolves
to - using a local copy of the MaxMind GeoLite2 City database, then returns that city's
record from the local Geonames cities index. It therefore supports the same --formatstr
formats as the Geonames subcommands. If the IP address cannot be located, or its city is
not in the Geonames index (e.g. a small town not in the default cities15000 index), the
IP address itself is returned.

The GeoLite2 City database will need to be MANUALLY downloaded from MaxMind. Though it is
free, you will need to create a MaxMind account to download the GeoIP2 Binary database (mmdb)
from https://www.maxmind.com/en/accounts/current/geoip/downloads.
Copy the GeoLite2-City.mmdb file to the ~/.qsv-cache/ directory or point to it using the
QSV_GEOIP2_FILENAME environment variable.

#### iplookup
Given an IP address or URL, return its city's location metadata. The default format is
'%city-admin1-country' (e.g. "San Francisco, California US").

  $ qsv geocode iplookup IP_col data.csv
  $ qsv geocode iplookup --formatstr "%json" IP_col data.csv
  $ qsv geocode iplookup -f "%cityrecord" IP_col data.csv

#### iplookupnow
Accepts the same options as iplookup, but does not require an input file.

  $ qsv geocode iplookupnow 140.174.222.253
  $ qsv geocode iplookupnow https://amazon.com
  $ qsv geocode iplookupnow --formatstr "%json" 140.174.222.253
  $ qsv geocode iplookupnow -f "%cityrecord" 140.174.222.253

### OpenCage
Online forward or reverse geocoding using the OpenCage Geocoding API
(https://opencagedata.com). Unlike the suggest/reverse subcommands which use the
local Geonames index, opencage geocodes real street addresses online.

Compared with more popular commercial geocoders such as Google Maps, OpenCage is
built on open data, chiefly OpenStreetMap, so its results come with far fewer strings:
 * you may store results as long as you like - even after you stop being a customer -
   which is what makes qsv's persistent result cache permissible.
 * results can be displayed on any map.
 * results may be used commercially, behind a firewall or publicly.
 * pricing is a flat monthly or annual fee. A free trial (2,500 requests/day) lets you
   test it, but is not for production use, which needs a paid plan.
 * bad results can be fixed at the source by correcting OpenStreetMap.

See https://opencagedata.com/why-use-open-data.

Requires an OpenCage API key. Set it with --api-key or the QSV_OPENCAGE_API_KEY
environment variable (the --api-key flag takes precedence). Get a free key at
https://opencagedata.com/users/sign_up.

OpenCage's Terms of Service explicitly allow caching, so results are cached in a
persistent on-disk cache (see --cache-ttl & --no-cache). Re-runs and duplicate
queries do NOT re-hit the API. The free trial allows 2,500 requests/day at 1
request/second; rows are processed sequentially and rate-limited (see --rate-limit).

#### opencage
The <column> may contain either a free-form address (forward geocoding) or a
"lat, long" / "(lat, long)" WGS-84 coordinate (reverse geocoding). The mode is
auto-detected per row; pass --reverse to force reverse geocoding.

The --country option, if set, restricts results to the given ISO 3166-1 alpha-2
country code(s). The --timeout, --language, --invalid-result, --new-column, --rename
and --output options behave as they do for the other subcommands.

The --formatstr option supports these OpenCage-specific formats:
  * '%+' | '%formatted'   - the OpenCage formatted address (default)
  * '%lat-long'           - <latitude>, <longitude>
  * '%location'           - (<latitude>, <longitude>)
  * '%city'               - the city/town/village
  * '%state' | '%admin1'  - the state/province
  * '%county' | '%admin2' - the county
  * '%country'            - the ISO 3166-1 alpha-2 country code
  * '%country_name'       - the country name
  * '%postcode'           - the postal code
  * '%confidence'         - the OpenCage confidence score (0-10)
  * '%json'               - the first OpenCage result as JSON
  * '%pretty-json'        - the first OpenCage result as pretty JSON
Dynamic formatting is also supported, using dotted keys, e.g.
  "{components.city}, {components.country}" or "{annotations.timezone.name}".
Available keys: formatted, lat, lng, confidence, components.<name> and
annotations.<dotted.path>.

The special "%dyncols:" format is also supported, adding multiple columns to the
output CSV. Set --formatstr to "%dyncols:" followed by a comma-delimited list of
"{col_name:key}" pairs, where key is one of the dynamic keys above, e.g.
  "%dyncols: {city:components.city}, {tz:annotations.timezone.name}"
Like the other subcommands, "%dyncols:" cannot be combined with --new-column.

  $ qsv geocode opencage address --api-key YOURKEY file.csv
  $ qsv geocode opencage address --country us -f '%json' file.csv
  $ qsv geocode opencage coord_col --reverse -c city file.csv
  $ qsv geocode opencage address -f '{components.city}, {components.country}' file.csv
  $ qsv geocode opencage address -f '%dyncols: {city:components.city}, {pc:components.postcode}' file.csv

#### opencagenow
Accepts the same options as opencage, but does not require an input file.

  $ qsv geocode opencagenow --api-key YOURKEY "Brooklyn, NY"
  $ qsv geocode opencagenow "40.71427, -74.00597"
  $ qsv geocode opencagenow -f '%pretty-json' "Eiffel Tower, Paris"

### Geoclient
Online geocoding of New York City locations using NYC's Geoclient v2 API
(https://api-portal.nyc.gov), a REST wrapper around the NYC Department of City
Planning's Geosupport system. Besides coordinates, it returns NYC-specific attributes
such as the BBL, BIN, community district, city council district, census tracts, NTA
and ZIP code. It only geocodes locations in the five boroughs.

The public API requires a free subscription key: sign up at https://api-portal.nyc.gov
and subscribe to the "Geoclient V2 User" product. Set the key with --api-key or the
QSV_GEOCLIENT_API_KEY environment variable (--api-key takes precedence).
To use a self-hosted Geoclient (https://github.com/mlipper/geoclient), set
QSV_GEOCLIENT_API_URL to its base URL (e.g. http://localhost:8080/geoclient/v2) -
no key is needed then.

The public API allows 100 requests/second per IP, 2,500 requests/minute and 500,000
requests/day. Requests are sent concurrently (see --jobs) behind a rate limiter that
defaults to 40 requests/second, to stay under the per-minute cap (see --rate-limit).
Requests that are rate-limited or fail on the server are retried up to 3 times. If 10
requests in a row still fail, the run is aborted, as the quota is likely exhausted.
Results are cached in a persistent on-disk cache (see --cache-ttl & --no-cache), and
duplicate locations are only looked up once.

#### geoclient
The --endpoint option selects the kind of lookup:
  * search       - (default) a free-form NYC location in <column>, e.g.
                   "314 W 100 St Manhattan", "Empire State Building" or a BBL/BIN.
  * bin          - a Building Identification Number in <column>.
  * bbl          - a Borough-Block-Lot in <column>, either as 10 digits (1000670001)
                   or delimited (1-67-1, 1/00067/0001).
  * normalize    - a street name in <column>, returned in Geosupport's normalized
                   form ("w 100 st" -> "WEST  100 STREET"). It only standardizes the
                   name: it does not check that the street exists. By default, numbers
                   are padded for sorting ("WEST    1 STREET"), the same spacing as the
                   street names in other Geoclient results; to compare with
                   single-spaced data, add --params format=C ("WEST 1 STREET").
  * streetcode   - a Geosupport street code in <column> (the borough digit plus a 5-,
                   7- or 10-digit code: 6, 8 or 11 digits, e.g. 11361001), returned as
                   the street's name. Other values are left unchanged, not sent.
  * address, addresspoint, intersection, place, blockface - structured lookups whose
                   inputs come from several columns, mapped with --params.

For the structured endpoints, --params maps Geoclient parameters to input columns
("name={Column}") or to fixed values ("name=value"), comma-separated. Parameter names
are case-sensitive:
  * address, addresspoint - houseNumber, street, and borough or zip
  * intersection - crossStreetOne, crossStreetTwo, borough
                   (optional: boroughCrossStreetTwo, compassDirection)
  * place        - name, and borough or zip
  * blockface    - onStreet, crossStreetOne, crossStreetTwo, borough
                   (optional: boroughCrossStreetOne, boroughCrossStreetTwo, compassDirection)
The borough may be a name (Manhattan), an abbreviation (MN) or a number (1-5).
With a structured endpoint, <column> is not sent to the API: it is only the column that
is replaced with the result (or that --rename applies to). For search, --params may
set fixed search options, e.g. "exactMatchMaxLevel=5". For normalize and streetcode,
it may set format - S (sort, the default) pads numbers so names sort numerically
("WEST    1 STREET"), C (compact) does not ("WEST 1 STREET") - and length (4-32,
default 32), which abbreviates names to fit (length=10: "W 100 ST").

A location that Geoclient cannot geocode is left unchanged (or set to --invalid-result).
So is a search that matches in MORE than one borough - typically a street address
without its borough, e.g. "100 Broadway" exists in Manhattan, Brooklyn, Queens and
Staten Island - rather than silently picking one; add the borough or ZIP code to the
input. (If one of the matches is an exact match, it is used.) A warning reports how
many rows were ambiguous.

Why a location did not geocode is available through %dyncols keys starting with
"_reject." - filled only on those rows, e.g. {why:_reject.message} gives Geosupport's
reason (e.g. "ADDRESS NUMBER OUT OF RANGE") or, for an ambiguous search, the boroughs
matched - marked "[street only]" where only the street's address range matched, not a
property. Other useful keys are _reject.reasonCode, _reject.message2 (the second
message of address and place lookups) and _reject._resultCount. With geoclientnow,
the JSON formats print the reject under "_reject". So that rejected searches carry
their reason, search sends returnRejections=true unless it is set in --params.

The --formatstr option supports these Geoclient-specific formats:
  * '%+' | '%lat-long'    - <latitude>, <longitude> (default). For normalize and
                            streetcode, which return no coordinates: the street name
                            (firstStreetNameNormalized).
  * '%location'           - (<latitude>, <longitude>)
  * '%bbl'                - the BBL
  * '%bin'                - the BIN (buildingIdentificationNumber)
  * '%normalized-address' - the address on one line, single-spaced, e.g.
                            "314 WEST 100 STREET, NEW YORK, NY 10025". Empty unless
                            the result has a house number (address and search results).
  * '%nyc-districts'      - 11 columns, as with "%dyncols:": borough,
                            community_district, council_district, assembly_district,
                            state_senate_district, congressional_district,
                            police_precinct, school_district, nta2020,
                            census_tract2020 and zip_code. Filled for address,
                            intersection, place and search results; bbl, bin and
                            addresspoint results only have the borough.
  * '%json'               - the full Geoclient result as JSON
  * '%pretty-json'        - the full Geoclient result as pretty JSON
Dynamic formatting is also supported, using any Geoclient result field, e.g.
  "{bbl} - council district {cityCouncilDistrict}". Commonly used fields include
latitude, longitude, bbl, buildingIdentificationNumber, communityDistrict,
cityCouncilDistrict, censusTract2020, nta2020, zipCode, xCoordinate, yCoordinate and
uspsPreferredCityName. A field missing from a result renders empty.
Two fields are added by qsv: _resultCount (how many results geocoded successfully)
and, for search, _level (the Geosupport search level of the result used).
For bbl and bin lookups, latitude/longitude are the building's internal label point.

The "%dyncols:" format is also supported, e.g.
  "%dyncols: {bbl:bbl}, {council:cityCouncilDistrict}, {tract:censusTract2020}"
  "%dyncols: {lat:latitude}, {lng:longitude}, {why:_reject.message}"

  $ qsv geocode geoclient address --api-key YOURKEY nyc_311.csv
  $ qsv geocode geoclient bbl --endpoint bbl -f '%dyncols: {lat:latitude}, {lng:longitude}' pluto.csv
  $ qsv geocode geoclient Street --endpoint address -c latlong --params "houseNumber={HouseNo},street={Street},borough={Borough}" file.csv

#### geoclientnow
Accepts the same options as geoclient (search, bin, bbl, normalize and streetcode
endpoints only), but does not require an input file.

  $ qsv geocode geoclientnow "350 5th Ave Manhattan"
  $ qsv geocode geoclientnow --endpoint bbl -f '%pretty-json' 1008350041
  $ qsv geocode geoclientnow --endpoint normalize "w 100 st"

### Census
Online geocoding of US addresses and coordinates using the US Census Geocoder
(https://geocoding.geo.census.gov/geocoder). It is free and needs no API key. Besides
coordinates and the matched address, it returns the Census geographies a location falls
in - state, county, tract, block group and block, and more (places, county subdivisions,
congressional and state legislative districts, urban areas, ZCTAs, etc.) - with their
GEOIDs, which is what joining Census statistics to your data needs.

To use a caching proxy that speaks the same API (e.g.
https://github.com/dathere/uscensus-caching-geocoder), set QSV_CENSUS_GEOCODER_URL to its
base URL (e.g. http://localhost:8080/geocoder). As the proxy caches results itself, using
the --no-cache option is then suggested.

#### census
There are three kinds of input:
  * a one-line address in <column> (the default), e.g.
    "4600 Silver Hill Rd, Washington, DC 20233".
  * an address in several columns, mapped with --params to the parts street, city,
    state and zip ("name={Column}" or a fixed "name=value"), e.g.
    "street={Street},city={City},state=MD,zip={Zip}". The Census Geocoder
    needs a street plus a ZIP code, or a street plus city and state: a row without
    them is not sent, and is left unchanged (or set to --invalid-result). <column> is
    then only the column the result goes in.
  * a "lat, long" WGS 84 coordinate in <column>, with --reverse. It returns the Census
    geographies at that point (there is no matched address).

The --benchmark (address ranges release) and --vintage (geography release) options
select what Census matches against. The defaults, Public_AR_Current and
Current_Current, are the latest. Use e.g. --vintage Census2020_Current for 2020 Census
geographies or ACS2026_Current for the ones the ACS uses. See
https://geocoding.geo.census.gov/geocoder/vintages?benchmark=Public_AR_Current.

Census has single-record and batch endpoints. A single lookup returns everything; a batch
lookup (up to 2,000 addresses per upload, one upload at a time) is much faster for large
files, but only returns the matched address, coordinates, TIGER line and match type, and
the state, county, tract, block group and block. By default (--census-mode auto), each
read chunk of rows (see --batch) is geocoded in batch when the --formatstr only needs
those fields and at least 50 of its locations are not cached yet; otherwise one request
per location is sent, 5 per second (see --rate-limit). Batch lookups are only used with
Current_* vintages.
An address the batch endpoint matches to more than one address (a "Tie") is not
geocoded; a warning counts them. --census-mode single geocodes them with the first match.
Connecticut batch matches are looked up again one by one: in Current vintages, its
counties are its planning regions, which batch results do not carry. Otherwise, batch
and single results are the same, except that coordinates can differ in their last
digit (~1e-12 degrees), as Census rounds them differently in the two.

A location that Census cannot geocode is left unchanged (or set to --invalid-result).
Requests that are rate-limited or fail on the server are retried up to 3 times. If 10
requests (or batch uploads) in a row still fail, the run is aborted. An HTTP 400 answer
(e.g. an invalid --benchmark or --vintage) stops the run. Results are cached in a
persistent on-disk cache (see --cache-ttl & --no-cache), and duplicate locations are only
looked up once. Batch no-matches and ties are not cached, as batch matching varies with
the load on the Census servers.

The --formatstr option supports these Census-specific formats:
  * '%+' | '%lat-long'    - <latitude>, <longitude> (default)
  * '%location'           - (<latitude>, <longitude>)
  * '%matched-address'    - the matched address, e.g.
                            "4600 SILVER HILL RD, WASHINGTON, DC, 20233"
  * '%census-geoids'      - 5 columns, as with "%dyncols:": census_state,
                            census_county, census_tract, census_blockgroup and
                            census_block - the GEOIDs of the location's state (24),
                            county (24033), tract (24033802405), block group
                            (240338024052) and block (240338024052004). ACS vintages
                            have no blocks, so census_block is empty for them.
  * '%json'               - the full result as JSON
  * '%pretty-json'        - the full result as pretty JSON
The result qsv returns (and prints for %json) has these fields: matchedAddress,
coordinates.x (longitude), coordinates.y (latitude), tigerLine.tigerLineId,
tigerLine.side, addressComponents (address searches), geographies (Census's own,
verbatim: one array of features per layer) and flat - the first feature of each layer,
e.g. flat.Counties.GEOID, flat.Census Tracts.TRACT or
flat.120th Congressional Districts.BASENAME. qsv adds _resultCount (how many addresses
matched; the first is used), _matchType (Exact or Non_Exact, batch lookups only) and
_source (single or batch). A field missing from a result renders empty.
Dynamic formatting is also supported, e.g. "{matchedAddress} ({tigerLine.side})".
As layer names contain spaces, the flat fields can only be used with "%dyncols:", e.g.
  "%dyncols: {tract:flat.Census Tracts.GEOID}, {cd:flat.120th Congressional Districts.GEOID}"
Layer names vary by vintage (e.g. "2020 Census Blocks" in Current vintages, "Census
Blocks" in Census2020 ones); run censusnow with -f %pretty-json to see them.

  $ qsv geocode census Address -f %census-geoids addresses.csv
  $ qsv geocode census Address --params "street={Street},city={City},state={State},zip={Zip}" -c latlong file.csv
  $ qsv geocode census LatLong --reverse -f '%dyncols: {tract:flat.Census Tracts.GEOID}' points.csv

#### censusnow
Accepts the same options as census (except --params), but does not require an
input file.

  $ qsv geocode censusnow "4600 Silver Hill Rd, Washington, DC 20233"
  $ qsv geocode censusnow -f %pretty-json "1600 Pennsylvania Ave NW, Washington, DC 20500"
  $ qsv geocode censusnow --reverse -f %census-geoids "38.84601, -76.92744"

### OpenCage, Geoclient & Census result caches

#### cache-* operations
Manage the persistent on-disk result caches used by the opencage, geoclient and census
subcommands. They are separate from the Geonames cities index, and live in
{cache-dir}/geocode-opencage_v3.redb, {cache-dir}/geocode-geoclient_v3.redb and
{cache-dir}/geocode-censusgeocoder_v3.redb.
Each operation applies to all three caches; cache-info prints one JSON line per cache.

It has three operations:
 * clear  - wipe the entire disk caches, removing all cached results.
 * prune  - delete cache entries older than the --older-than value. The value is either
            an absolute date/datetime (e.g. 2025-01-31, "2025-01-31 12:00:00") or a
            relative age with a unit suffix - s(econds), m(inutes), h(ours), d(ays) or
            w(eeks). e.g. 30d, 2w, 48h, 90m, 3600s.
 * info   - report the cache directory, entry count, on-disk size and the oldest/newest
            cached entry timestamps. Emits a JSON summary to stdout.

Wipe the entire OpenCage, Geoclient and Census caches.

  $ qsv geocode cache-clear

Delete cached entries older than 30 days.

  $ qsv geocode cache-prune --older-than 30d

Delete cached entries created before a specific date.

  $ qsv geocode cache-prune --older-than 2025-01-01

Show cache statistics.

  $ qsv geocode cache-info

Examples:

# For US locations, you can retrieve the us_state_fips_code and us_county_fips_code fields of a US City
# to help with Census data enrichment.
qsv geocode suggest city_col --country US -f \
"%dyncols: {geocoded_city_col:name}, {state_col:admin1}, {county_col:admin2},  {state_fips_code:us_state_fips_code}, {county_fips_code:us_county_fips_code}"\
    input_data.csv -o output_data_with_fips.csv

# For US locations, you can reverse geocode the us_state_fips_code and us_county_fips_code fields of a WGS 84 coordinate
# to help with Census data enrichment. The coordinate can be in "lat, long" or "(lat, long)" format.
qsv geocode reverse wgs84_coordinate_col --country US -f \
"%dyncols: {geocoded_city_col:name}, {state_col:admin1}, {county_col:admin2},  {state_fips_code:us_state_fips_code}, {county_fips_code:us_county_fips_code}"\
    input_data.csv -o output_data_with_fips.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_geocode.rs.
See also https://github.com/dathere/qsv/wiki/Geospatial#geocode

Usage:
qsv geocode suggest [--formatstr=<string>] [options] <column> [<input>]
qsv geocode suggestnow [options] <location>
qsv geocode reverse [--formatstr=<string>] [options] <column> [<input>]
qsv geocode reversenow [options] <location>
qsv geocode countryinfo [options] <column> [<input>]
qsv geocode countryinfonow [options] <location>
qsv geocode iplookup [options] <column> [<input>]
qsv geocode iplookupnow [options] <location>
qsv geocode opencage [--formatstr=<string>] [options] <column> [<input>]
qsv geocode opencagenow [options] <location>
qsv geocode geoclient [--formatstr=<string>] [options] <column> [<input>]
qsv geocode geoclientnow [options] <location>
qsv geocode census [--formatstr=<string>] [options] <column> [<input>]
qsv geocode censusnow [options] <location>
qsv geocode index-load [--timeout=<seconds>] <index-file>
qsv geocode index-check
qsv geocode index-update [--languages=<lang>] [--cities-url=<url>] [--force] [--timeout=<seconds>]
qsv geocode index-reset [--timeout=<seconds>]
qsv geocode cache-clear [options]
qsv geocode cache-prune --older-than=<val> [options]
qsv geocode cache-info [options]
qsv geocode --help

geocode arguments:

    <input>                     The input file to read from. If not specified, reads from stdin.

    <column>                    The column to geocode. Used by suggest, reverse & countryinfo subcommands.
                                For suggest, it must be a column with a City string pattern.
                                For reverse, it must be a column using WGS 84 coordinates in
                                "lat, long" or "(lat, long)" format.
                                For countryinfo, it must be a column with a ISO 3166-1 alpha-2 country code.
                                For iplookup, it must be a column with an IP address or a URL.
                                For opencage, it may be a free-form address OR a WGS 84 coordinate.
                                For geoclient, it is the NYC location, BIN, BBL, street name or
                                street code (see --endpoint).
                                For census, it is a one-line US address or, with --reverse, a
                                WGS 84 coordinate (with --params, the column the result goes in).
                                Note that you can use column selector syntax to select the column, but only
                                the first column will be used. See `select --help` for more information.

    <location>                  The location to geocode for suggestnow, reversenow, countryinfonow and
                                iplookupnow subcommands.
                                  For suggestnow, its a City string pattern.
                                  For reversenow, it must be a WGS 84 coordinate.
                                  For countryinfonow, it must be a ISO 3166-1 alpha-2 code.
                                  For iplookupnow, it must be an IP address or a URL.
                                  For opencagenow, it must be an address OR a WGS 84 coordinate.
                                  For geoclientnow, it is a NYC location, BIN, BBL, street name or street code.
                                  For censusnow, it is a one-line US address or, with --reverse,
                                  a WGS 84 coordinate.

    <index-file>                The alternate geonames index file to use. It must be a .rkyv file.
                                For convenience, if this is set to a published population floor
                                (15000 or 1000), it will download that prebuilt English-only Geonames
                                index rkyv file from the qsv GitHub repo for the current qsv version and
                                use it. Only used by the index-load subcommand.

geocode options:
    -c, --new-column <name>     Put the transformed values in a new column instead. Not valid when
                                using the '%dyncols:' --formatstr option.
    -r, --rename <name>         New name for the transformed column.
    --country <country_list>    The comma-delimited, case-insensitive list of countries to filter for.
                                Country is specified as a ISO 3166-1 alpha-2 (two-letter) country code.
                                https://en.wikipedia.org/wiki/ISO_3166-2

                                It is the topmost priority filter, and will be applied first. If multiple
                                countries are specified, they are matched in priority order.

                                For suggest, this will limit the search to the specified countries.

                                For reverse, this ensures that the returned city is in the specified
                                countries (especially when geocoding coordinates near country borders).
                                If the coordinate is outside the specified countries, the returned city
                                will be the closest city as the crow flies in the specified countries.

                                SUGGEST only options:
    --min-score <score>         The minimum Jaro-Winkler distance score.
                                [default: 0.8]
    --admin1 <admin1_list>      The comma-delimited, case-insensitive list of admin1s to filter for.
                                Only a place inside one of them is returned. A value with no match
                                inside them is left unchanged (or set to the invalid-result value),
                                and the number of such values is reported on stderr.

                                If it has the form CC.CODE, it will be treated as an admin1 code
                                (e.g. US.NY, JP.40, CN.23 - case-insensitive, so us.ny also works).
                                Otherwise, it will be treated as an admin1 name (e.g New York, Tokyo, Shanghai).
                                US territories, which Geonames files as countries of their own, are
                                accepted as US.PR, US.VI, US.GU, US.AS and US.MP.

                                Requires the --country option, unless every entry is an admin1 code:
                                then the countries are inferred from the code prefixes (e.g. US.TX,US.PR
                                infers US and PR), and the --country option is not required.

                                If specifying multiple admin1 filters, you can mix admin1 codes and names.
                                A place inside any of them qualifies, and the best-scoring one is
                                returned, preferring a place whose name is exactly the value.

                                Matches are made using a starts_with() comparison (i.e. "US.N" will match "US.NY",
                                "US.NJ", etc. for admin1 code. "New" will match "New York", "New Jersey",
                                "Newfoundland", etc. for admin1 name.) Note that a few full Geonames codes are
                                prefixes of others (e.g. KZ.12 also matches KZ.12510143), so such a code
                                also admits the longer codes it prefixes.

                                admin1 is the second priority filter, and will be applied after country filters.
                                See https://download.geonames.org/export/dump/admin1CodesASCII.txt for
                                recognized admin1 codes/names.

                                REVERSE only option:
    -k, --k_weight <weight>     Use population-weighted distance for reverse subcommand.
                                (i.e. nearest.distance - k * city.population)
                                Larger values will favor more populated cities.
                                If not set (default), the population is not used and the
                                nearest city is returned.

                                OPENCAGE, GEOCLIENT & CENSUS options:
    --api-key <key>             The API key for the opencage and geoclient subcommands.
                                If set, it takes precedence over the QSV_OPENCAGE_API_KEY
                                (opencage) or QSV_GEOCLIENT_API_KEY (geoclient) environment
                                variable. Get a free OpenCage key at
                                https://opencagedata.com/users/sign_up, or a Geoclient
                                subscription key at https://api-portal.nyc.gov.
    --rate-limit <qps>          Maximum number of API requests per second.
                                Defaults to 1 for opencage (its free trial allows 1
                                request/second, 2,500/day), 40 for geoclient (the
                                public API allows 100/second per IP but only 2,500/minute,
                                so 41.6/second sustained, and 500,000/day) and 5 for census
                                (single-record lookups; batch uploads are paced separately).
    --cache-ttl <seconds>       Time-to-live for the persistent on-disk result cache.
                                A value of 0 disables time-based expiration (entries are
                                cached indefinitely). Use --no-cache to disable caching entirely.
                                [default: 1209600]
    --no-cache                  Disable the persistent on-disk result cache. Duplicate
                                queries within a run are still de-duplicated
                                (for geoclient and census, within each --batch).

                                OPENCAGE only options:
    --reverse                  Force reverse geocoding for opencage/opencagenow (treat the
                                query as a "lat, long" WGS-84 coordinate). If not set, forward
                                and reverse mode is auto-detected per row.
                                For census/censusnow, <column> holds "lat, long" coordinates
                                and the Census geographies at that point are returned.
    --no-annotations            Omit OpenCage annotations (timezone, currency, etc.) from the
                                result and from %json output.

                                GEOCLIENT only options:
    --endpoint <name>           The Geoclient lookup: search (default), bin, bbl, normalize,
                                streetcode, address, addresspoint, intersection, place
                                or blockface.
                                See GEOCLIENT above.
    --params <list>             Comma-separated Geoclient parameters for the structured
                                endpoints, each "name={Column}" or "name=value", e.g.
                                "houseNumber={HouseNo},street={Street},borough={Boro}".
                                For search, only fixed options are allowed, e.g.
                                "exactMatchMaxLevel=5".
                                Also used by census to read an address from several
                                columns: see CENSUS only options.

                                CENSUS only options:
    --benchmark <name>          The Census Geocoder benchmark (address ranges release).
                                Default: Public_AR_Current.
    --vintage <name>            The Census Geocoder vintage (geography release), e.g.
                                Current_Current, Census2020_Current or ACS2026_Current.
                                Default: Current_Current.
    --census-mode <mode>        Whether to use the Census batch endpoints:
                                  auto   - (default) batch when the output only needs batch
                                           fields and at least 50 rows of a --batch still
                                           need a lookup.
                                  batch  - always batch. An output that needs more than
                                           the batch fields (e.g. %json) is an error.
                                  single - one request per location.
                                The address parts for census --params are street, city,
                                state and zip, e.g. "street={Street},city={City},state=NY".
                                A street needs a zip, or a city and state.

    -f, --formatstr=<string>    The place format to use. It has three options:
                                1. Use one of the predefined formats.
                                2. Use dynamic formatting to create a custom format.
                                3. Use the special format "%dyncols:" to dynamically add multiple
                                   columns to the output CSV using fields from a geocode result.

                                PREDEFINED FORMATS:
                                  * '%city-state' - e.g. Brooklyn, New York
                                  * '%city-country' - Brooklyn, US
                                  * '%city-state-country' | '%city-admin1-country' - Brooklyn, New York US
                                  * '%city-county-state' | '%city-admin2-admin1' - Brooklyn, Kings County, New York
                                  * '%city' - Brooklyn
                                  * '%state' | '%admin1' - New York
                                  * '%county' | '%admin2' - Kings County
                                  * '%country' - US
                                  * '%country_name' - United States
                                  * '%cityrecord' - returns the full city record as a string
                                  * '%admin1record' - returns the full admin1 record as a string
                                  * '%admin2record' - returns the full admin2 record as a string
                                  * '%lat-long' - <latitude>, <longitude>
                                  * '%location' - (<latitude>, <longitude>)
                                  * '%id' - the Geonames ID
                                  * '%capital' - the capital
                                  * '%continent' - the continent (only valid for countryinfo subcommand)
                                  * '%population' - the population
                                  * '%timezone' - the timezone
                                  * '%json' - the full city record as JSON
                                  * '%pretty-json' - the full city record as pretty JSON
                                  * '%+' - use the subcommand's default format.
                                           suggest - '%location'
                                           suggestnow - '{name}, {admin1} {country}: {latitude}, {longitude}'
                                           reverse & reversenow - '%city-admin1-country'
                                           countryinfo - '%country_name'
                                           iplookup - '%city-admin1-country'
                                           iplookupnow - '{name}, {admin1} {country}: {latitude}, {longitude}'


                                If an invalid format is specified, it will be treated as '%+'.

                                Note that when using the JSON predefined formats with the now subcommands,
                                the output will be valid JSON, as the "Location" header will be omitted.

                                DYNAMIC FORMATTING:
                                Alternatively, you can use dynamic formatting to create a custom format.
                                To do so, set the --formatstr to a dynfmt template, enclosing field names
                                in curly braces.
                                The following ten cityrecord fields are available:
                                  id, name, latitude, longitude, country, admin1, admin2, capital,
                                  timezone, population

                                Fifteen additional countryinfo field are also available:
                                  iso3, fips, area, country_population, continent, tld, currency_code,
                                  currency_name, phone, postal_code_format, postal_code_regex, languages,
                                  country_geonameid, neighbours, equivalent_fips_code

                                For US places, two additional fields are available:
                                  us_county_fips_code and us_state_fips_code

                                  e.g. "City: {name}, State: {admin1}, Country: {country} {continent} - {languages}"

                                If an invalid template is specified, "Invalid dynfmt template" is returned.

                                Both predefined and dynamic formatting are cached. Subsequent calls
                                with the same result will be faster as it will use the cached result instead
                                of searching the Geonames index.

                                DYNAMIC COLUMNS ("%dyncols:") FORMATTING:
                                Finally, you can use the special format "%dyncols:" to dynamically add multiple
                                columns to the output CSV using fields from a geocode result.
                                To do so, set --formatstr to "%dyncols:" followed by a comma-delimited list
                                of key:value pairs enclosed in curly braces.
                                The key is the desired column name and the value is one of the same fields
                                available for dynamic formatting.

                                 e.g. "%dyncols: {city_col:name}, {state_col:admin1}, {county_col:admin2}"

                                will add three columns to the output CSV named city_col, state_col & county_col.

                                Note that using "%dyncols:" will cause the command to geocode EACH row without
                                using the cache, so it will be slower than predefined or dynamic formatting.
                                Also, countryinfo and countryinfonow subcommands currently do not support "%dyncols:".
                                [default: %+]
    -l, --language <lang>       The language to use when geocoding. The language is specified as a ISO 639-1 code.
                                Note that the Geonames index must have been built with the specified language
                                using the `index-update` subcommand with the --languages option.
                                If the language is not available, the first language in the index is used.
                                [default: en]

    --invalid-result <string>   The string to return when the geocode result is empty/invalid.
                                If not set, the original value is used.
    -j, --jobs <arg>            The number of jobs to run in parallel.
                                When not set, the number of jobs is set to the number of CPUs detected.
                                For geoclient and census, it is the number of requests in
                                flight at once.
    -b, --batch <size>          The number of rows per batch to load into memory, before running in parallel.
                                Set to 0 to load all rows in one batch.
                                [default: 50000]
    --timeout <seconds>         Timeout for downloading Geonames cities index.
                                Also applies to each Geonames source file downloaded
                                when rebuilding the index with index-update, and to the
                                prebuilt index downloaded by index-load and index-reset -
                                raise it on slow connections.
                                For opencage, geoclient and census, it is the timeout for each
                                API request.
                                [default: 120]
    --cache-dir <dir>           The directory to use for caching the Geonames cities index
                                and the persistent on-disk OpenCage, Geoclient and Census result
                                caches.
                                If the directory does not exist, qsv will attempt to create it.
                                If the QSV_CACHE_DIR envvar is set, it will be used instead.
                                The index file is named for the qsv release, so each upgrade
                                downloads a new one. When it does, qsv deletes the index files
                                of all but the 5 most recent releases found in this directory.
                                [default: ~/.qsv-cache]

                                CACHE-PRUNE only option:
    --older-than <val>          Delete OpenCage, Geoclient and Census cache entries older than
                                this value.
                                Accepts an absolute date/datetime (e.g. 2025-01-31) or a
                                relative age with a unit suffix (s/m/h/d/w = seconds,
                                minutes, hours, days or weeks; e.g. 30d, 2w, 48h).
                                Required by the cache-prune subcommand.

                                INDEX-UPDATE only options:
    --languages <lang-list>     The comma-delimited, case-insensitive list of languages to use when building
                                the Geonames cities index.
                                The languages are specified as Geonames language codes - the ISO 639-1
                                2-letter code where one exists (e.g. en,fr,de,es), else the ISO 639-2/3 code.
                                See https://download.geonames.org/export/dump/iso-languagecodes.txt to look up codes
                                and https://download.geonames.org/export/dump/alternatenames/ for the supported
                                language files. 253 languages are currently supported.
                                If not set, the languages the current index was built with are used
                                (en if there is no current index).
                                Setting it to a different list than the current index's forces a rebuild.
    --cities-url <url>          The URL to download the Geonames cities file from. There are several
                                available at https://download.geonames.org/export/dump/.
                                  cities500.zip   - cities with populations > 500; ~200k cities, 56mb
                                  cities1000.zip  - population > 1000; ~140k cities, 44mb
                                  cities5000.zip  - population > 5000; ~53k cities, 21mb
                                  cities15000.zip - population > 15000; ~26k cities, 13mb
                                Note that the more cities are included, the larger the local index file will be,
                                lookup times will be slower, and the search results will be different.
                                For convenience, if this is set to 500, 1000, 5000 or 15000, it will be
                                converted to a geonames cities URL.
                                If not set, the cities file the current index was built from is used
                                (cities15000.zip if there is no current index).
                                Setting it to a different URL than the current index's forces a rebuild.
    --force                     Force update the Geonames cities index. If not set, qsv will check if there
                                are updates available at Geonames.org before updating the index.
                                With --force, the index is built even if there is no current index.

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout.
    -d, --delimiter <arg>       The field delimiter for reading CSV data.
                                Must be a single character. (default: ,)
    -p, --progressbar           Show progress bars. Will also show the cache hit rate upon completion.
                                Not valid for stdin.
```
## qsv geoconvert

```text
Convert between various spatial formats and CSV/SVG including GeoJSON, SHP, and more.

For example to convert a GeoJSON file into CSV data:

  $ qsv geoconvert file.geojson geojson csv

To use stdin as input instead of a file path, use a dash "-":

  $ qsv prompt -m "Choose a GeoJSON file" -F geojson | qsv geoconvert - geojson csv

To convert a CSV file into GeoJSON data, specify the WKT geometry column with the --geometry flag:

  $ qsv geoconvert file.csv csv geojson --geometry geometry

Alternatively specify the latitude and longitude columns with the --latitude and --longitude flags:

  $ qsv geoconvert file.csv csv geojson --latitude lat --longitude lon

Convert latitude/longitude columns into a WKT geometry column, reading a TSV file:

  $ qsv geoconvert file.tsv csv csv --latitude lat --longitude lon

For CSV input, rows whose geometry cannot be used are skipped: an empty geometry, latitude
or longitude cell, WKT that does not parse, a latitude or longitude that is not a finite
number, or a latitude outside -90..90 or longitude outside -180..180. A warning on stderr
counts the skipped rows and gives the line of the first one. If EVERY row is skipped,
geoconvert fails instead, as the columns are then most likely wrong - swapped, or holding
projected coordinates such as State Plane feet. Latitude and longitude values may be
padded with spaces.

Swapped latitude/longitude columns are only caught when the swapped values fall out of
range (e.g. US West Coast longitudes near -122). Where both values are within +/-90
(e.g. New York: 40.7, -74), swapped columns are NOT detected - check a few rows on a map.

A shapefile needs its .shp, .shx and .dbf files side by side. If its .prj file describes a
projected coordinate system (e.g. NY State Plane), geoconvert warns: the coordinates are
output unchanged, so they are not the WGS-84 longitude/latitude that GeoJSON requires.
Reprojection is not done by geoconvert; reproject the shapefile first, e.g. with
ogr2ogr -t_srs EPSG:4326 out.shp in.shp

Coordinates are converted as 64-bit floating point numbers, which hold 15-17 significant
digits in all (whole and decimal digits together). A coordinate written with more digits
than that is output shortened, and its last digit may change: 40.123456789012345 becomes
40.123456789012344, and the longitude -122.123456789012345 becomes -122.12345678901235.
The difference is far below what GPS can measure; 7 decimal places is already about 1 cm.

See also https://github.com/dathere/qsv/wiki/Geospatial#geoconvert

Usage:
    qsv geoconvert [options] (<input>) (<input-format>) (<output-format>)
    qsv geoconvert --help

geoconvert REQUIRED arguments:
    <input>           The spatial file to convert. To use stdin instead, use a dash "-".
                      Note: SHP input must be a path to a .shp file and cannot use stdin.
    <input-format>    Valid values are "geojson", "shp", and "csv"
    <output-format>   Valid values are:
                      - For GeoJSON input: "csv", "svg", and "geojsonl"
                      - For SHP input: "csv", "geojson", "geojsonl", and "svg"
                      - For CSV input: "geojson", "geojsonl", "svg", and "csv"
                        (CSV output has the geometry as a WKT column)

geoconvert options:
                                 REQUIRED FOR CSV INPUT
    -g, --geometry <geometry>    The name of the column that has WKT geometry.
                                 Alternative to --latitude and --longitude.
    -y, --latitude <col>         The name of the column with northing values.
    -x, --longitude <col>        The name of the column with easting values.

    -l, --max-length <length>    The maximum column length in bytes when the output format
                                 is CSV. Oftentimes, the geometry column is too long to fit
                                 in a CSV file, causing other tools like Python & PostgreSQL
                                 to fail. If a column is too long, it will be truncated to
                                 the specified length and an ellipsis ("...") will be
                                 appended, so a truncated value is up to 3 bytes longer.

Common options:
    -h, --help                   Display this message
    -o, --output <file>          Write output to <file> instead of stdout.
    -d, --delimiter <arg>        The field delimiter for reading CSV input.
                                 Must be a single character. (default: ,)
```
## qsv headers

```text
Prints the fields of the first row in the CSV data.

These names can be used in commands like 'select' to refer to columns in the
CSV data.

Note that multiple CSV files may be given to this command. This is useful with
the --union flag.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_headers.rs.
See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#headers

Usage:
    qsv headers [options] [<input>...]
    qsv headers --help

headers arguments:
    <input>...             The CSV file(s) to read. Use '-' for standard input.
                           If input is a directory, all files in the directory will
                           be read as input.
                           If the input is a file with a '.infile-list' extension,
                           the file will be read as a list of input files.
                           If the input are snappy-compressed files(s), it will be
                           decompressed automatically.

headers options:
    -j, --just-names       Only show the header names (hide column index).
                           This is automatically enabled if more than one
                           input is given.
    -J, --just-count       Only show the number of headers.
    --union                Shows the union of headers across all inputs
                           (deduplicated).
    --trim                 Trim leading/trailing space, tab, and quote
                           characters from header name.

Common options:
    -h, --help             Display this message
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv help

```text

Usage:
    qsv <command> [<args>...]
    qsv [options]

Options:
    --list                           List all commands available.
    --envlist                        List all qsv-relevant environment variables.
    --capabilities                   Print version, features & installed commands as JSON.
    -u, --update                     Update qsv to the latest release from GitHub.
    -U, --updatenow                  Update qsv to the latest release from GitHub w/o confirming.
    --generate-help-md               Generate Markdown help files in docs/help/.
    --export-tool-definitions <dir>  Write JSON tool definitions, help Markdown and a
                                     manifest for every installed command to <dir>.
                                     For one command, use <command> --help --format json|md
    --update-mcp-skills              Regenerate MCP skills JSON files for Claude Desktop.
    -h, --help           Display this message
    <command> -h         Display the command help message
    -v, --version        Print version info, mem allocator, features installed,
                         max_jobs, num_cpus, build info then exit

sponsored by datHere - Data Infrastructure Engineering (https://qsv.datHere.com)
Need a UI & more advanced data-wrangling? Upgrade to qsv pro (https://qsvpro.datHere.com)

```
## qsv implode

```text
Implodes multiple rows into one by grouping on key column(s) and joining the
values of another column with the given separator. The inverse of `explode`.

Examples:

```csv
name,color
John,blue
John,yellow
John,light red
Mary,red
```

# Can be imploded by key column "name", joining the "color" column with "; "
$ qsv implode -k name -v color "; " data.csv

```csv
name,color
John,blue; yellow; light red
Mary,red
```

# With `-r colors` the value column is renamed
$ qsv implode -k name -v color -r colors "; " data.csv

```csv
name,colors
John,blue; yellow; light red
Mary,red
```

Only the key column(s) and the value column appear in the output; any other
columns are dropped.

By default, all input rows are buffered in memory and groups are emitted in the
order keys are first seen. If the input is already sorted by the key column(s),
use --sorted to stream groups as they are seen (memory proportional to the
largest group, not the whole input).

See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#implode

Usage:
    qsv implode [options] -k <keys> -v <value> <separator> [<input>]
    qsv implode --help

implode options:
    -k, --keys <keys>      Key column(s) to group by. Supports the usual
                           selector syntax (e.g. "name", "1", "1-3", "a,c").
    -v, --value <value>    The column whose values will be joined per group.
                           Must resolve to exactly one column.
    -r, --rename <name>    New name for the imploded value column.
    --sorted               Assume input is pre-sorted by the key column(s).
                           Streams groups as they are seen; memory is bounded
                           by the size of the largest group.
    --skip-empty           Skip empty values when joining. By default, empty
                           values are included as empty tokens so that
                           round-tripping with `explode` is lossless.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv index

```text
Creates an index of the given CSV data, which can make other operations like
slicing, splitting and gathering statistics much faster.

Note that this does not accept CSV data on stdin. You must give a file
path. The index is created at 'path/to/input.csv.idx'. The index will be
automatically used by commands that can benefit from it. If the original CSV
data changes after the index is made, commands that try to use it will result
in an error (you have to regenerate the index before it can be used again).

However, if the environment variable QSV_AUTOINDEX_SIZE is set, qsv will
automatically create an index when the input file size >= specified size (bytes).
It will also automatically update stale indices as well.

See also https://github.com/dathere/qsv/wiki/Indexing-Compression-Diff#index

Usage:
    qsv index [options] <input>
    qsv index --help

index options:
    -o, --output <file>    Write index to <file> instead of <input>.idx.
                           Generally, this is not currently useful because
                           the only way to use an index is if it is specially
                           named <input>.idx.

Common options:
    -h, --help             Display this message
```
## qsv input

```text
Read CSV data with special commenting, quoting, trimming, line-skipping &
non UTF-8 encoding rules and transforms it to a "normalized", UTF-8 encoded CSV.

Generally, all qsv commands support basic options like specifying the delimiter
used in CSV data. However, this does not cover all possible types of CSV data. For
example, some CSV files don't use '"' for quotes or use different escaping styles.

Also, CSVs with preamble lines can have them skipped with the --skip-lines & --auto-skip
options. Similarly, --skip-lastlines allows epilogue lines to be skipped.

Finally, non UTF-8 encoded files are "lossy" saved to UTF-8 by default, replacing all
invalid UTF-8 sequences with �. Note though that this is not true transcoding.

If you need to properly transcode non UTF-8 files, you'll need to use a tool like `iconv`
before processing it with qsv - e.g. to convert an ISO-8859-1 encoded file to UTF-8:
    `iconv -f ISO-8859-1 -t UTF-8 input.csv -o utf8_output.csv`.

You can change this behavior with the --encoding-errors option.

See https://github.com/dathere/qsv#utf-8-encoding for more details.

This command is typically used at the beginning of a data pipeline (thus the name `input`)
to normalize & prepare CSVs for further processing with other qsv commands.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_input.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#input

Usage:
    qsv input [options] [<input>]
    qsv input --help

input options:
    --quote <arg>            The quote character to use. [default: "]
    --escape <arg>           The escape character to use. When not specified,
                             quotes are escaped by doubling them.
    --no-quoting             Disable quoting completely when reading CSV data.
    --quote-style <arg>      The quoting style to use when writing CSV data.
                             Possible values: all, necessary, nonnumeric and never.
                              All: Quotes all fields.
                              Necessary: Quotes fields only when necessary - when fields
                               contain a quote, delimiter or record terminator.
                               Quotes are also necessary when writing an empty record
                               (which is indistinguishable from a record with one empty field).
                              NonNumeric: Quotes all fields that are non-numeric.
                              Never: Never write quotes. Even if it produces invalid CSV.
                             [default: necessary]
    --skip-lines <arg>       The number of preamble CSV records to skip.
    --auto-skip              Sniffs a CSV for preamble records and automatically
                             skips them. Takes precedence over --skip-lines option.
                             Does not work with <stdin>.
    --skip-lastlines <arg>   The number of epilogue CSV records to skip.
    --trim-headers           Trim leading & trailing whitespace & quotes from header values.
    --trim-fields            Trim leading & trailing whitespace from field values.
    --comment <char>         The comment character to use (single-byte; only the
                             first byte of the UTF-8 encoding is matched). When set,
                             lines starting with this byte will be skipped.
    --encoding-errors <arg>  How to handle UTF-8 encoding errors.
                             Possible values: replace, skip, strict.
                               replace: Replace invalid UTF-8 sequences with �.
                                  skip: Fields with encoding errors are "<SKIPPED>".
                                strict: Fail on any encoding errors.
                             [default: replace]

Common options:
    -h, --help               Display this message
    -o, --output <file>      Write output to <file> instead of stdout.
    -d, --delimiter <arg>    The field delimiter for reading CSV data.
                             Must be a single character. (default: ,)
```
## qsv join

```text
Joins two sets of CSV data on the specified columns.

The default join operation is an 'inner' join. This corresponds to the
intersection of rows on the keys specified.

Joins are always done by ignoring leading and trailing whitespace. By default,
joins are done case sensitively, but this can be disabled with the --ignore-case
flag.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_join.rs.
See also https://github.com/dathere/qsv/wiki/Joins-and-Set-Ops#join

Usage:
    qsv join [options] <columns1> <input1> <columns2> <input2>
    qsv join --help

input arguments:
    <input1>                is the first CSV data set to join.
    <input2>                is the second CSV data set to join.
    <columns1> & <columns2> are the columns to join on for each input.

    The columns arguments specify the columns to join for each input. Columns can
    be referenced by name or index, starting at 1. Specify multiple columns by
    separating them with a comma. Specify a range of columns with `-`. Both
    columns1 and columns2 must specify exactly the same number of columns.
    (See 'qsv select --help' for the full syntax.)

    For <input1> and <input2>, specifying `-` indicates reading from stdin.
    e.g. 'qsv frequency -s Agency nyc311.csv | qsv join value - id nycagencyinfo.csv'

join options:
    --left                 Do a 'left outer' join. This returns all rows in
                           first CSV data set, including rows with no
                           corresponding row in the second data set. When no
                           corresponding row exists, it is padded out with
                           empty fields.
    --left-anti            Do a 'left anti' join. This returns all rows in
                           first CSV data set that has no match with the
                           second data set.
    --left-semi            Do a 'left semi' join. This returns all rows in
                           first CSV data set that has a match with the
                           second data set.
    --right                Do a 'right outer' join. This returns all rows in
                           second CSV data set, including rows with no
                           corresponding row in the first data set. When no
                           corresponding row exists, it is padded out with
                           empty fields. (This is the reverse of 'outer left'.)
    --right-anti           This returns only the rows in the second CSV data set
                           that do not have a corresponding row in the first
                           data set. The output schema is the same as the
                           second dataset.
    --right-semi           This returns only the rows in the second CSV data set
                           that have a corresponding row in the first data set.
                           The output schema is the same as the second data set.
    --full                 Do a 'full outer' join. This returns all rows in
                           both data sets with matching records joined. If
                           there is no match, the missing side will be padded
                           out with empty fields. (This is the combination of
                           'outer left' and 'outer right'.)
    --cross                USE WITH CAUTION.
                           This returns the cartesian product of the CSV
                           data sets given. The number of rows return is
                           equal to N * M, where N and M correspond to the
                           number of rows in the given data sets, respectively.
    --nulls                When set, joins will work on empty fields.
                           Otherwise, empty fields are completely ignored.
                           (In fact, any row that has an empty field in the
                           key specified is ignored.)
    --keys-output <file>   Write successfully joined keys to <file>.
                           This means that the keys are written to the output
                           file when a match is found, with the exception of
                           anti joins, where keys are written when NO match
                           is found.
                           Cross joins do not write keys.

                           JOIN KEY TRANSFORMATION OPTIONS:
                           Note that transformations are applied to TEMPORARY
                           join key columns. The original columns are not modified
                           and the TEMPORARY columns are removed after the join.
-i, --ignore-case           When set, joins are done case insensitively.
-z, --ignore-leading-zeros  When set, leading zeros are ignored in join keys.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv joinp

```text
Joins two sets of CSV data on the specified columns using the Polars engine.

The default join operation is an 'inner' join. This corresponds to the
intersection of rows on the keys specified.

Unlike the join command, joinp can process files larger than RAM, is multithreaded,
has join key validation, a maintain row order option, pre-join filtering, supports
non-equi & asof joins and its output columns can be coalesced (no duplicate columns).

Returns the shape of the join result (number of rows, number of columns) to stderr.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_joinp.rs.
See also https://github.com/dathere/qsv/wiki/Joins-and-Set-Ops#joinp

Usage:
    qsv joinp [options] <columns1> <input1> <columns2> <input2>
    qsv joinp --cross [--validate <arg>] <input1> <input2> [--decimal-comma] [--delimiter <arg>] [--output <file>]
    qsv joinp --non-equi <expr> <input1> <input2> [options] [--output <file>]
    qsv joinp --help

joinp arguments:
    Both <input1> aka <left> & <input2> aka <right> files need to have headers.
    Stdin is not supported.

    The columns arguments specify the columns to join for each input. Columns are
    referenced by name. Specify multiple columns by separating them with a comma.
    Both <columns1> and <columns2> must specify exactly the same number of columns.

    Note that <input1> is the left CSV data set and <input2> is the right CSV data set.

joinp options:
    --left                 Do a 'left outer' join. This returns all rows in
                           first CSV data set, including rows with no
                           corresponding row in the second data set. When no
                           corresponding row exists, it is padded out with
                           empty fields.
    --left-anti            This returns only the rows in the first CSV data set
                           that do not have a corresponding row in the second
                           data set. The output schema is the same as the
                           first dataset.
    --left-semi            This returns only the rows in the first CSV data set
                           that have a corresponding row in the second data set.
                           The output schema is the same as the first data set.
    --right                Do a 'right outer' join. This returns all rows in
                           second CSV data set, including rows with no
                           corresponding row in the first data set. When no
                           corresponding row exists, it is padded out with
                           empty fields. (This is the reverse of 'outer left'.)
    --right-anti           This returns only the rows in the second CSV data set
                           that do not have a corresponding row in the first
                           data set. The output schema is the same as the
                           second dataset.
    --right-semi           This returns only the rows in the second CSV data set
                           that have a corresponding row in the first data set.
                           The output schema is the same as the second data set.
    --full                 Do a 'full outer' join. This returns all rows in
                           both data sets with matching records joined. If
                           there is no match, the missing side will be padded
                           out with empty fields.
    --cross                USE WITH CAUTION.
                           This returns the cartesian product of the CSV
                           data sets given. The number of rows return is
                           equal to N * M, where N and M correspond to the
                           number of rows in the given data sets, respectively.
                           The columns1 and columns2 arguments are ignored.
    --non-equi <expr>      Do a non-equi join. The given expression is evaluated
                           for each row in the left dataset and can refer to columns
                           in the left and right dataset. If the expression evaluates
                           to true, the row is joined with the corresponding row in
                           the right dataset.
                           The expression is a valid Polars SQL where clause, with each
                           column name followed by "_left" or "_right" suffixes to indicate
                           which data set the column belongs to.
                           (e.g. "salary_left >= min_salary_right AND \
                                  salary_left <= max_salary_right AND \
                                  experience_left >= min_exp_right")

    --coalesce             Force the join to coalesce columns with the same name.
                           For inner joins, this is not necessary as the join
                           columns are automatically coalesced.

    --filter-left <arg>    Filter the left CSV data set by the given Polars SQL
                           expression BEFORE the join. Only rows that evaluates
                           to true are used in the join.
    --filter-right <arg>   Filter the right CSV data set by the given Polars SQL
                           expression BEFORE the join. Only rows that evaluates
                           to true are used in the join.
    --validate <arg>       Validate the join keys BEFORE performing the join.
                           Valid values are:
                             none - No validation is performed.
                             onetomany - join keys are unique in the left data set.
                             manytoone - join keys are unique in the right data set.
                             onetoone - join keys are unique in both left & right data sets.
                           [default: none]

                            JOIN OPTIONS:
    --maintain-order <arg>  Which row order to preserve, if any. Valid values are:
                              none, left, right, left_right, right_left
                            Defaults to "none", which lets the engine emit rows in
                            whatever order it finishes them - faster on large joins,
                            but the output is NOT reproducible: the same invocation
                            can return the same rows in a different order each run.
                            "left" orders by the left row only, so when one left row
                            matches several right rows those matches are tied and
                            their relative order is still unspecified. Use
                            "left_right" (or "right_left") for a fully deterministic,
                            byte-repeatable order.
                            Only inner, left, right and full joins can maintain order;
                            cross, non-equi and asof joins ignore this option.
                            [default: none]
    --nulls                When set, joins will work on empty fields.
                           Otherwise, empty fields are completely ignored.
    --streaming            Write the join result as it is computed, batch by batch, instead
                           of collecting the whole result in memory first. Use this when the
                           result is too big for memory: it uses less memory but is slower.
                           An --output file is written beside its target and only moved into
                           place if the join succeeds; overwriting an existing file copies the
                           result into it, so it keeps its owner, group, mode and links, and
                           briefly needs disk space for two copies.
                           On stdout, rows are sent as they are computed, so a join that fails
                           part-way leaves its output cut short; check the exit code.

                           POLARS CSV PARSING OPTIONS:
    --try-parsedates       When set, will attempt to parse the columns as dates.
                           If the parse fails, columns remain as strings.
                           This is useful when the join keys are formatted as
                           dates with differing date formats, as the date formats
                           will be normalized. Note that this will be automatically
                           enabled when using asof joins.
    --infer-len <arg>      The number of rows to scan when inferring the schema of the CSV.
                           Set to 0 to do a full table scan (warning: very slow).
                           Only used when --cache-schema is 0 or 1 and no cached schema exists or
                           when --infer-len is 0.
                           [default: 10000]
    --cache-schema <arg>   Create and cache Polars schema JSON files.
                           Ignored when --infer-len is 0.
                           ‎ -2: treat all columns as String. A Polars schema file is created & cached.
                           ‎ -1: treat all columns as String. No Polars schema file is created.
                           ‎  0: do not cache Polars schema. Uses --infer-len to infer schema.
                           ‎  1: cache Polars schema with the following behavior:
                                * If schema file exists and is newer than input: use cached schema
                                * If schema file missing/outdated and stats cache exists:
                                  derive schema from stats and cache it
                                * If no schema or stats cache: infer schema using --infer-len
                                  and cache the result
                                Schema files use the same name as input with .pschema.json extension
                                (e.g., data.csv -> data.pschema.json).
                           ‎NOTE: If the input files have pschema.json files that are newer or created
                           at the same time as the input files, they will be used to inform the join
                           operation regardless of the value of --cache-schema unless --infer-len is 0.
                           [default: 0]
    --no-optimizations     Disable non-default join optimizations. This will make joins slower.
                           Only use this when you get join errors.
    --ignore-errors        Ignore errors when parsing CSVs. If set, rows with errors
                           will be skipped. If not set, the query will fail.
                           Only use this when debugging queries, as polars does batched
                           parsing and will skip the entire batch where the error occurred.
                           To get more detailed error messages, set the environment variable
                           POLARS_BACKTRACE_IN_ERR=1 before running the join.
    --decimal-comma        Use comma as the decimal separator when parsing & writing CSVs.
                           Otherwise, use period as the decimal separator.
                           Note that you'll need to set --delimiter to an alternate delimiter
                           other than the default comma if you are using this option.

                           ASOF JOIN OPTIONS:
    --asof                 Do an 'asof' join. This is similar to a left inner
                           join, except we match on nearest key rather than
                           equal keys (see --allow-exact-matches).
                           Particularly useful for time series data.
                           Note that both CSV data sets will be SORTED on the join columns
                           by default, unless --no-sort is set.
    --no-sort              Do not sort the CSV data sets on the join columns by default.
                           Note that asof joins REQUIRE the join keys to be sorted,
                           so this option should only be used as a performance optimization
                           when you know the CSV join keys are already sorted.
                           If the CSV join keys are not sorted, the asof join will fail or
                           return incorrect results.
    --left_by <arg>        Do an 'asof_by' join - a special implementation of the asof
                           join that searches for the nearest keys within a subgroup
                           set by the asof_by columns. This specifies the column/s for
                           the left CSV. Columns are referenced by name. Specify
                           multiple columns by separating them with a comma.
    --right_by <arg>       Do an 'asof_by' join. This specifies the column/s for
                           the right CSV.
    --strategy <arg>       The strategy to use for the asof join:
                             backward - For each row in the first CSV data set,
                                        we find the last row in the second data set
                                        whose key is less than the key in the first
                                        data set (or <= with --allow-exact-matches).
                             forward -  For each row in the first CSV data set,
                                        we find the first row in the second data set
                                        whose key is greater than the key in the
                                        first data set (or >= with --allow-exact-matches).
                             nearest -  selects the last row in the second data set
                                        whose value is nearest to the value in the
                                        first data set.
                           [default: backward]
    --tolerance <arg>      The tolerance for the nearest asof join. This is only
                           used when the nearest strategy is used. The
                           tolerance is a positive integer that specifies
                           the maximum number of rows to search for a match.

                           If the join is done on a column of type Date, Time or
                           DateTime, then the tolerance is interpreted using
                           the following language:
                                1d - 1 day
                                1h - 1 hour
                                1m - 1 minute
                                1s - 1 second
                                1ms - 1 millisecond
                                1us - 1 microsecond
                                1ns - 1 nanosecond
                                1w - 1 week
                                1mo - 1 month
                                1q - 1 quarter
                                1y - 1 year
                                1i - 1 index count
                             Or combine them: “3d12h4m25s” # 3 days, 12 hours,
                             4 minutes, and 25 seconds
                             Suffix with “_saturating” to indicate that dates too
                             large for their month should saturate at the largest date
                             (e.g. 2022-02-29 -> 2022-02-28) instead of erroring.
   -X, --allow-exact-matches  When set, the asof join will allow exact matches.
                              (i.e. less-than-or-equal-to or greater-than-or-equal-to)
                              Otherwise, the asof join will only allow nearest matches
                              (strictly less-than or greater-than) by default.

                             OUTPUT FORMAT OPTIONS:
   --sql-filter <SQL>        The SQL expression to apply against the join result.
                             Used to select columns and filter rows AFTER running the join.
                             Be sure to select from the "join_result" table when formulating
                             the SQL expression.
                             (e.g. "select c1, c2 as colname from join_result where c2 > 20")
   --datetime-format <fmt>   The datetime format to use writing datetimes.
                             See https://docs.rs/chrono/latest/chrono/format/strftime/index.html
                             for the list of valid format specifiers.
   --date-format <fmt>       The date format to use writing dates.
   --time-format <fmt>       The time format to use writing times.
   --float-precision <arg>   The number of digits of precision to use when writing floats.
                             (default: 6)
   --null-value <arg>        The string to use when writing null values.
                             (default: <empty string>)

                             JOIN KEY TRANSFORMATION OPTIONS:
                             Note that transformations are applied to TEMPORARY
                             join key columns. The original columns are not modified
                             and the TEMPORARY columns are removed after the join.

-i, --ignore-case            When set, joins are done case insensitively.
-z, --ignore-leading-zeros   When set, joins are done ignoring leading zeros.
                             Note that this is only applied to the join keys for
                             both numeric and string columns. Also note that
                             Polars will automatically remove leading zeros from
                             numeric columns when it infers the schema.
                             To force the schema to be all String types,
                             set --cache-schema to -1 or -2.
-N, --norm-unicode <arg>     When set, join keys are Unicode normalized.
                             Valid values are:
                               nfc - Normalization Form C
                               nfd - Normalization Form D
                               nfkc - Normalization Form KC
                               nfkd - Normalization Form KD
                               none - No normalization is performed.
                             [default: none]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading/writing CSV data.
                           Must be a single character. (default: ,)
    -q, --quiet            Do not return join shape to stderr.
```
## qsv json

```text
Convert JSON to CSV.

The JSON data is expected to be non-empty and non-nested as either:

1. An array of objects where:
   A. All objects are non-empty, have non-empty and unique keys, and the same keys are in each object.
   B. Values are not objects or arrays.
2. An object where values are not objects or arrays and the object is as described above.

Objects with duplicate keys are not recommended as only one key and its values may be used.

If your JSON data is not in the expected format and/or is nested or complex, try using
the --jaq option to pass a jq-like filter before parsing with the above constraints.
Learn more about jaqhere: https://github.com/01mf02/jaq

As an example, say we have the following JSON data in a file fruits.json:

[
    {
        "fruit": "apple",
        "price": 2.50,
        "calories": 95
    },
    {
        "fruit": "banana",
        "price": 3.00,
        "calories": 105
    }
]

To convert it to CSV format run:

  $ qsv json fruits.json

And the following is printed to the terminal:

fruit,price,calories
apple,2.5,95
banana,3.0,105

IMPORTANT:
  The order of the columns in the CSV file will be the same as the order of the keys in the first JSON object.
  The order of the rows in the CSV file will be the same as the order of the objects in the JSON array.

  Additional keys not present in the first JSON object will be appended as additional columns in the
  output CSV in the order they appear.

For example, say we have the following JSON data in a file fruits2.json:

[
    {
        "fruit": "apple",
        "cost": 1.75,
        "price": 2.50,
        "calories": 95
    },
    {
        "fruit": "mangosteen",
        "price": 5.00,
        "calories": 56
    },
    {
        "fruit": "starapple",
        "rating": 9,
        "price": 4.50,
        "calories": 95,
    },
    {
        "fruit": "banana",
        "price": 3.00,
        "calories": 105
    }
]

If we run the following command:

  $ qsv json fruits2.json | qsv table

The output CSV will have the following columns:

fruit       cost  price  calories  rating
apple       1.75  2.5    95
mangosteen        5.0    56
starapple         4.5    95        9
banana            3.0    105

Note that the "rating" column is added as an additional column in the output CSV,
though it appears as the 2nd column in the third JSON object for "starapple".

If you want to select/reorder/drop columns in the output CSV, use the --select option, for example:

  $ qsv json fruits.json --select price,fruit

The following is printed to the terminal:

price,fruit
2.5,apple
3.0,banana

Note: Trailing zeroes in decimal numbers from the input data are truncated (2.50 becomes 2.5)
because JSON decimals (numbers with a fractional part or exponent) round-trip through f64.
Plain integer tokens are preserved exactly (serde_json parses them as i64/u64). With --jaq,
integers that don't fit i64/u64 are emitted verbatim as strings to avoid silent precision
loss, and decimal literals written inside the --jaq filter expression itself are passed
through verbatim (2.50 stays 2.50, scientific notation is kept as written).

If the JSON data was provided using stdin then either use - or do not provide a file path.
For example you may copy the JSON data above to your clipboard then run:

  $ qsv clipboard | qsv json

Again, when JSON data is nested or complex, try using the --jaq option and provide a filter value.

For example we have a .json file with a "data" key and the value being the same array as before:

{
    "data": [...]
}

We may run the following to select the JSON file and convert the nested array to CSV:

  $ qsv prompt -F json | qsv json --jaq .data

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_json.rs.
See also https://github.com/dathere/qsv/wiki/Conversion-and-IO#json

Usage:
    qsv json [options] [<input>]
    qsv json --help

json options:
    --jaq <filter>         Filter JSON data using jaq syntax (https://github.com/01mf02/jaq),
                           which is identical to the popular JSON command-line tool - jq.
                           https://jqlang.github.io/jq/
                           Note that the filter is applied BEFORE converting JSON to CSV
    -s, --select <cols>    Select, reorder or drop columns for output.
                           Otherwise, all the columns will be output in the same order as
                           the first object's keys in the JSON data.
                           See 'qsv select --help' for the full syntax.
                           Note however that <cols> NEED to be a comma-delimited list
                           of column NAMES and NOT column INDICES.
                           [default: 1- ]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
```
## qsv jsonl

```text
Convert newline-delimited JSON (JSONL/NDJSON) to CSV.

The command tries to do its best but since it is not possible to
straightforwardly convert JSON lines to CSV, the process might lose some complex
fields from the input.

Also, it will fail if the JSON documents are not consistent with one another,
as the first JSON line will be used to infer the headers of the CSV output.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_jsonl.rs.
See also https://github.com/dathere/qsv/wiki/Conversion-and-IO#jsonl

Usage:
    qsv jsonl [options] [<input>]
    qsv jsonl --help

jsonl options:
    --ignore-errors        Skip malformed input lines.
    -j, --jobs <arg>       The number of jobs to run in parallel.
                           When not set, the number of jobs is set to the
                           number of CPUs detected.
    -b, --batch <size>     The number of rows per batch to load into memory,
                           before running in parallel. Set to 0 to load all
                           rows in one batch. [default: 50000]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The delimiter to use when writing CSV data.
                           Must be a single character. (default: ,)
```
## qsv lens

```text
Explore tabular data files interactively using the csvlens (https://github.com/YS-L/csvlens) engine.

If the polars feature is enabled, lens can browse tabular data in Arrow, Avro/IPC, Parquet, JSON (JSON Array)
and JSONL files. It also automatically decompresses csv/tsv/tab/ssv files using the gz,zlib & zst
compression formats (e.g. data.csv.gz, data.tsv.zlib, data.tab.gz & data.ssv.zst).

If the polars feature is not enabled, lens can only browse CSV dialects (CSV, TSV, Tab, SSV) and
its snappy-compressed variants (CSV.sz, TSV.sz, Tab.sz & SSV.sz).

Press 'q' to exit. Press '?' for help.

See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#lens

Usage:
    qsv lens [options] [<input>]
    qsv lens --help

Examples:
Automatically choose delimiter based on the file extension
  $ qsv lens data.csv // comma-separated
  $ qsv lens data.tsv // Tab-separated
  $ qsv lens data.tab // Tab-separated
  $ qsv lens data.ssv // Semicolon-separated
  # custom delimiter
  $ qsv lens --delimiter '|' data.csv

Auto-decompresses several compression formats:
  $ qsv lens data.csv.sz // Snappy-compressed CSV
  $ qsv lens data.tsv.sz // Snappy-compressed Tab-separated

  # additional compression formats below require polars feature
  $ qsv lens data.csv.gz // Gzipped CSV
  $ qsv lens data.tsv.zlib // Zlib-compressed Tab-separated
  $ qsv lens data.tab.zst // Zstd-compressed Tab-separated
  $ qsv lens data.ssv.zst // Zstd-compressed Semicolon-separated

Explore tabular data in other formats (if polars feature is enabled)
  $ qsv lens data.parquet // Parquet
  $ qsv lens data.jsonl // JSON Lines
  $ qsv lens data.json // JSON - will only work with a JSON Array
  $ qsv lens data.avro // Avro

Prompt the user to select a column to display. Once selected,
exit with the value of the City column for the selected row sent to stdout
  $ qsv lens --prompt 'Select City:' --echo-column 'City' data.csv

Only show rows that contain "NYPD"
  $ qsv lens --filter NYPD data.csv
  # Show rows that contain "nois" case insensitive (for noise, noisy, noisier, etc.)
  $ qsv lens --filter nois --ignore-case data.csv

Find and highlight matches in the data
  $ qsv lens --find 'New York' data.csv

Find and highlight cells that have all numeric values in a column.
  $ qsv lens --find '^\d+$' data.csv

lens options:
  -d, --delimiter <char>           Delimiter character (comma by default)
                                   "auto" to auto-detect the delimiter
  -t, --tab-separated              Use tab separation. Shortcut for -d '\t'
      --no-headers                 Do not interpret the first row as headers

      --columns <regex>            Use this regex to select columns to display by default.
                                   e.g. "col1|col2|col3" to select columns "col1", "col2" and "col3"
                                   and also columns like "col1_1", "col22" and "col3-more".
      --filter <regex>             Use this regex to filter rows to display by default.
                                   The regex is matched against each cell in every column.
                                   e.g. "val1|val2" filters rows with any cells containing "val1", "val2"
                                   or text like "my_val1" or "val234".
      --find <regex>               Use this regex to find and highlight matches by default.
                                   Automatically sets --monochrome to true so the matches are easier to see.
                                   The regex is matched against each cell in every column.
                                   e.g. "val1|val2" highlights text containing "val1", "val2" or
                                   longer text like "val1_ok" or "val2_error".

  -i, --ignore-case                Searches ignore case. Ignored if any uppercase letters
                                   are present in the search string
  -f, --freeze-columns <num>       Freeze the first N columns
                                   [default: 1]
  -m, --monochrome                 Disable color output
  -W, --wrap-mode <mode>           Set the wrap mode for the output.
                                   Valid modes are:
                                     "words": Wrap at word boundaries
                                     "chars": Wrap at character boundaries
                                     "disabled": No wrapping
                                   For convenience, the first character can be used as a shortcut:
                                     qsv lens -W w data.csv // wrap at word boundaries
                                   [default: disabled]
  -A, --auto-reload                Automatically reload the data when the file changes.
  -S, --streaming-stdin            Enable streaming stdin (load input as it's being piped in)
                                   NOTE: This option only applies to stdin input.

  -P, --prompt <prompt>            Set a custom prompt in the status bar. Normally paired w/ --echo-column:
                                     qsv lens --prompt 'Select City:' --echo-column 'City'
                                   Supports ANSI escape codes for colored or styled text. When using
                                   escape codes, ensure it's properly escaped. For example, in bash/zsh,
                                   the $'...' syntax is used to do so:
                                     qsv lens --prompt $'\033[1;5;31mBlinking red, bold text\033[0m'
                                   see https://en.wikipedia.org/wiki/ANSI_escape_code#Colors or
                                   https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
                                   for more info on ANSI escape codes.
                                   Typing a complicated prompt on the command line can be tricky.
                                   If the prompt starts with "file:", it's interpreted as a filepath
                                   from which to load the prompt, e.g.
                                     qsv lens --prompt "file:prompt.txt"
      --echo-column <column_name>  Print the value of this column to stdout for the selected row

      --debug                      Show stats for debugging

Common options:
    -h, --help      Display this message
```
## qsv luau

```text
Create multiple new computed columns, filter rows or compute aggregations by
executing a Luau 0.740 script for every row (SEQUENTIAL MODE) or for
specified rows (RANDOM ACCESS MODE) of a CSV file.

Luau is not just another qsv command. It is qsv's Domain-Specific Language (DSL)
for data-wrangling. 👑

The executed Luau has 3 ways to reference row columns (as strings):
  1. Directly by using column name (e.g. Amount), can be disabled with --no-globals
  2. Indexing col variable by column name: col.Amount or col["Total Balance"]
  3. Indexing col variable by column 1-based index: col[1], col[2], etc.
     This is only available with the --colindex or --no-headers options.

Of course, if your input has no headers, then 3. will be the only available
option.

It has two subcommands:
  map     - Create new columns by mapping the result of a Luau script for each row.
  filter  - Filter rows by executing a Luau script for each row. Rows that return
            true are kept, the rest are filtered out.

Some examples:

  Sum numeric columns 'a' and 'b' and call new column 'c'
  $ qsv luau map c "a + b"
  $ qsv luau map c "col.a + col['b']"
  $ qsv luau map c --colindex "col[1] + col[2]"

  There is some magic in the previous example as 'a' and 'b' are passed in
  as strings (not numbers), but Luau still manages to add them up.
  A more explicit way of doing it, is by using the tonumber() function.
  See https://luau-lang.org/library for a list of built-in functions.
  $ qsv luau map c "tonumber(a) + tonumber(b)"

  Add running total column for Amount
  $ qsv luau map Total "tot = (tot or 0) + Amount; return tot"

  Or use the --begin and --end options to compute the running & grand totals
  $ qsv luau map Total --begin "tot = 0; gtotal = 0" \
        "tot = tot + Amount; gtotal = gtotal + tot; return tot" --end "return gtotal"

  Add running total column for Amount when previous balance was 900
  $ qsv luau map Total "tot = (tot or 900) + Amount; return tot"

  Use the qsv_cumsum() helper function to compute the running total.
  See https://github.com/dathere/qsv/wiki/Luau-Helper-Functions-Examples for more examples.

  $ qsv luau map Total "qsv_cumsum(Amount)"

  Convert Amount to always-positive AbsAmount and Type (debit/credit) columns
  $ qsv luau map Type \
        "if tonumber(Amount) < 0 then return 'debit' else return 'credit' end" | \
    qsv luau map AbsAmount "math.abs(tonumber(Amount))"

  Map multiple new columns in one pass
  $ qsv luau map newcol1,newcol2,newcol3 "{cola + 1, colb + 2, colc + 3}"

  Filter some rows based on numerical filtering
  $ qsv luau filter "tonumber(a) > 45"
  $ qsv luau filter "tonumber(a) >= tonumber(b)"

PATTERN MATCHING WITH string.find AND OTHER STRING FUNCTIONS:
  Lua/Luau string functions like string.find, string.match, string.gsub use
  PATTERN MATCHING by default, where certain characters have special meanings:
    ( ) . % + - * ? [ ] ^ $

  If you need to search for these characters literally, you have two options:

  1. Escape special characters with % (percent sign):
     $ qsv luau filter "string.find(Name, 'John %(Jr%)')"
     $ qsv luau map dots "string.gsub(col.text, '%%.', '')"

  2. Use plain text mode (4th parameter = true):
     $ qsv luau filter "string.find(Name, 'John (Jr)', 1, true)"
     $ qsv luau map match "string.find(col.text, 'Mr.', 1, true)"

  Common gotchas:
  - Parentheses in names like "Jane (Smith)" need escaping or plain mode
  - Dots in email addresses, URLs, or decimal numbers
  - Hyphens in phone numbers or dates

  For more on Lua patterns: https://www.lua.org/manual/5.4/manual.html#6.4.1

  Typing long scripts on the command line gets tiresome rather quickly. Use the
  "file:" prefix or the ".lua/.luau" file extension to read non-trivial scripts
  from the filesystem.

  In the following example, both the BEGIN and END scripts have the lua/luau file
  extension so they are read from the filesystem.  With the debitcredit.script file,
  we use the "file:" prefix to read it from the filesystem.

  $ qsv luau map Type -B init.lua file:debitcredit.script -E end.luau

With "luau map", if the MAIN script is invalid for a row, "<ERROR>" followed by a
detailed error message is returned for that row.
With "luau filter", if the MAIN script is invalid for a row, that row is not filtered.

If any row has an invalid result, an exitcode of 1 is returned and an error count
is logged.

SPECIAL VARIABLES:
  "_IDX" - a READ-only variable that is zero during the BEGIN script and
       set to the current row number during the MAIN & END scripts.

       It is primarily used in SEQUENTIAL MODE when the CSV has no index or you
       wish to process the CSV sequentially.

  "_INDEX" - a READ/WRITE variable that enables RANDOM ACCESS MODE when used in
       a script. Using "_INDEX" in a script switches qsv to RANDOM ACCESS MODE
       where setting it to a row number will change the current row to the
       specified row number. It will only work, however, if the CSV has an index.

       When using _INDEX, the MAIN script will keep looping and evaluate the row
       specified by _INDEX until _INDEX is set to an invalid row number
       (e.g. <= zero or to a value greater than _ROWCOUNT).

       If the CSV has no index, qsv will abort with an error unless "qsv_autoindex()"
       is called in the BEGIN script to create an index.

  "_ROWCOUNT" - a READ-only variable which is zero during the BEGIN & MAIN scripts,
       and set to the rowcount during the END script when the CSV has no index
       (SEQUENTIAL MODE).

       When using _INDEX and the CSV has an index, _ROWCOUNT will be set to the
       rowcount of the CSV file, even from the BEGINning
       (RANDOM ACCESS MODE).

  "_LASTROW" - a READ-only variable that is set to the last row number of the CSV.
       Like _INDEX, it will also trigger RANDOM ACCESS MODE if used in a script.

       Similarly, if the CSV has no index, qsv will also abort with an error unless
       "qsv_autoindex()" is called in the BEGIN script to create an index.

For security and safety reasons as a purpose-built embeddable interpreter,
Luau's standard library is relatively minimal (https://luau-lang.org/library).
That's why qsv bundles & preloads LuaDate v2.2.1 as date manipulation is a common task.
See https://tieske.github.io/date/ on how to use the LuaDate library.

Additional libraries can be loaded using Luau's "require" function.
See https://github.com/LewisJEllis/awesome-lua for a list of other libraries.

With the judicious use of "require", the BEGIN script & special variables, one can
create variables, tables, arrays & functions that can be used for complex aggregation
operations in the END script.

SCRIPT DEVELOPMENT TIPS:
When developing Luau scripts, be sure to take advantage of the "qsv_log" function to
debug your script. It will log messages at the level (INFO, WARN, ERROR, DEBUG, TRACE)
specified by the QSV_LOG_LEVEL environment variable (see docs/Logging.md for details).

At the DEBUG level, the log messages will be more verbose to facilitate debugging.
It will also skip precompiling the MAIN script to bytecode so you can see more
detailed error messages with line numbers.

Bear in mind that qsv strips comments from Luau scripts before executing them.
This is done so qsv doesn't falsely trigger on special variables mentioned in comments.
When checking line numbers in DEBUG mode, be sure to refer to the comment-stripped
scripts in the log file, not the original commented scripts.

There are more Luau helper functions in addition to "qsv_log", notably the powerful
"qsv_register_lookup" which allows you to "lookup" values against other
CSVs on the filesystem, a URL, datHere's lookup repo or CKAN instances.

Detailed descriptions of these helpers can be found in the "setup_helpers" section at
the bottom of this file and on the Wiki (https://github.com/dathere/qsv/wiki)

For more detailed examples, see https://github.com/dathere/qsv/blob/master/tests/test_luau.rs.
See also https://github.com/dathere/qsv/wiki/Scripting-Luau-Python#luau

Usage:
    qsv luau map [options] -n <main-script> [<input>]
    qsv luau map [options] <new-columns> <main-script> [<input>]
    qsv luau filter [options] <main-script> [<input>]
    qsv luau map --help
    qsv luau filter --help
    qsv luau --help

Luau arguments:

    All <script> arguments/options can either be the Luau code, or if it starts with
    "file:" or ends with ".luau/.lua" - the filepath from which to load the script.

    Instead of using the --begin and --end options, you can also embed BEGIN and END
    scripts in the MAIN script by using the "BEGIN { ... }!" and "END { ... }!" syntax.

    The BEGIN script is embedded in the MAIN script by adding a BEGIN block at the
    top of the script. The BEGIN block must start at the beginning of the line.
    It can contain multiple statements.

    The MAIN script is the main Luau script to execute. It is executed for EACH ROW of
    the input CSV. It can contain multiple statements and should end with a "return" stmt.
    In map mode, the return value is/are the new value/s of the mapped column/s.
    In filter mode, the return value is a boolean indicating if the row should be filtered.

    The END script is embedded in the MAIN script by adding an END block at the bottom
    of the script. The END block must start at the beginning of the line.
    It can contain multiple statements.

    <new-columns> is a comma-separated list of new computed columns to add to the CSV
    when using "luau map". The new columns are added to the CSV after the existing
    columns, unless the --remap option is used.

Luau options:
  -g, --no-globals        Don't create Luau global variables for each column,
                          only `col`. Useful when some column names mask standard
                          Luau globals and to increase PERFORMANCE.
                          Note: access to Luau globals thru _G remains even with -g.
  --colindex              Create a 1-based column index. Useful when some column names
                          mask standard Luau globals. Automatically enabled with --no-headers.
  -r, --remap             Only the listed new columns are written to the output CSV.
                          Only applies to "map" subcommand.
  -B, --begin <script>    Luau script/file to execute in the BEGINning, before
                          processing the CSV with the main-script.
                          Typically used to initialize global variables.
                          Takes precedence over an embedded BEGIN script.
                          If <script> begins with "file:" or ends with ".luau/.lua",
                          it's interpreted as a filepath from which to load the script.
  -E, --end <script>      Luau script/file to execute at the END, after processing the
                          CSV with the main-script.
                          Typically used for aggregations.
                          The output of the END script is sent to stderr.
                          Takes precedence over an embedded END script.
                          If <script> begins with "file:" or ends with ".luau/.lua",
                          it's interpreted as a filepath from which to load the script.
  --max-errors <count>    The maximum number of errors to tolerate before aborting.
                          Set to zero to disable error limit.
                          [default: 10]
  --timeout <seconds>     Timeout for downloading lookup_tables using
                          the qsv_register_lookup() helper function.
                          [default: 60]
  --ckan-api <url>        The URL of the CKAN API to use for downloading lookup_table
                          resources using the qsv_register_lookup() helper function
                          with the "ckan://" scheme.
                          If the QSV_CKAN_API envvar is set, it will be used instead.
                          [default: https://data.dathere.com/api/3/action]
  --ckan-token <token>    The CKAN API token to use. Only required if downloading
                          private resources.
                          If the QSV_CKAN_TOKEN envvar is set, it will be used instead.
  --cache-dir <dir>       The directory to use for caching downloaded lookup_table
                          resources using the qsv_register_lookup() helper function.
                          If the directory does not exist, qsv will attempt to create it.
                          If the QSV_CACHE_DIR envvar is set, it will be used instead.
                          [default: ~/.qsv-cache]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. Automatically enables --colindex option.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -p, --progressbar      Show progress bars. Not valid for stdin.
                           Ignored in qsvdp.
                           In SEQUENTIAL MODE, the progress bar will show the
                           number of rows processed.
                           In RANDOM ACCESS MODE, the progress bar will show
                           the position of the current row being processed.
                           Enabling this option will also suppress stderr output
                           from the END script.
```
## qsv log

```text
Logs an MCP tool invocation entry to qsvmcp.log. Only intended for internal use by the
qsv MCP server, not for general CLI use and only available from the qsvmcp binary variant.

This command is used internally by the MCP server to create an audit trail of
tool invocations. Each entry includes the tool name, a prefixed invocation UUID
(with a "s-" prefix for start, "e-" for end), and context (agent's reason or result).

The log file (qsvmcp.log) is written in the current working directory of the
process. When invoked by the MCP server, this is the server's configured working
directory (set via qsv_set_working_dir). Ensure the CWD is consistent to avoid
logs being scattered across directories.

Usage:
    qsv log <tool-name> <invocation-id> [<message>...]
    qsv log --help

Common options:
    -h, --help     Display this message
```
## qsv moarstats

```text
Add dozens of additional statistics, including extended outlier, robust & bivariate
statistics to an existing stats CSV file. It also maps the field type to the most specific
W3C XML Schema Definition (XSD) datatype (https://www.w3.org/TR/xmlschema-2/).

IMPORTANT:
  The `moarstats` command is designed to be run AFTER the `stats` command, as it relies
  on the baseline statistics computed by `stats` to calculate "moar" statistics.

The `moarstats` command extends an existing stats CSV file (created by the `stats` command)
by computing "moar" (https://www.dictionary.com/culture/slang/moar) statistics that can be
derived from existing stats columns and by scanning the original CSV file.

It looks for the `<FILESTEM>.stats.csv` file for a given CSV input. If the stats CSV file
does not exist, it will first run the `stats` command with configurable options to establish
the baseline stats, to which it will add more stats columns.

If the `.stats.csv` file is found, it will skip running stats and just append the additional
stats columns. However, if its `.stats.csv.json` metadata records a different qsv version,
the baseline stats are recomputed and the additional stats columns are added afresh, so
a stats file extended by an older qsv release never keeps its outdated values.

Currently computes the following 40 additional univariate statistics:
 1. Pearson's Second Skewness Coefficient: 3 * (mean - median) / stddev
    Measures asymmetry of the distribution.
    Positive values indicate right skew, negative values indicate left skew.
    https://en.wikipedia.org/wiki/Skewness
 2. Range to Standard Deviation Ratio: range / stddev
    Normalizes the spread of data.
    Higher values indicate more extreme outliers relative to the variability.
 3. Quartile Coefficient of Dispersion: (Q3 - Q1) / (Q3 + Q1)
    Measures relative variability using quartiles.
    Useful for comparing dispersion across different scales.
    https://en.wikipedia.org/wiki/Quartile_coefficient_of_dispersion
 4. Z-Score of Mode: (mode - mean) / stddev
    Indicates how typical the mode is relative to the distribution.
    Values near 0 suggest the mode is near the mean.
 5. Relative Standard Error: sem / mean
    Measures precision of the mean estimate relative to its magnitude.
    Lower values indicate more reliable estimates.
 6. Z-Score of Min: (min - mean) / stddev
    Shows how extreme the minimum value is.
    Large negative values indicate outliers or heavy left tail.
 7. Z-Score of Max: (max - mean) / stddev
    Shows how extreme the maximum value is.
    Large positive values indicate outliers or heavy right tail.
 8. Median-to-Mean Ratio: median / mean
    Indicates skewness direction.
    Ratio < 1 suggests right skew, > 1 suggests left skew, = 1 suggests symmetry.
 9. IQR-to-Range Ratio: iqr / range
    Measures concentration of data.
    Higher values (closer to 1) indicate more data concentrated in the middle 50%.
10. MAD-to-StdDev Ratio: mad / stddev
    Compares robust vs non-robust spread measures.
    Higher values suggest presence of outliers affecting stddev.
11. Trimean: (Q1 + 2*median + Q3) / 4
    Tukey's trimean - a robust estimator of central tendency combining the median
    with the midhinge. More robust than mean, more efficient than median alone.
    https://en.wikipedia.org/wiki/Trimean
12. Midhinge: (Q1 + Q3) / 2
    Midpoint of the middle 50% of data. A robust central tendency measure
    that complements the mean and median.
    https://en.wikipedia.org/wiki/Midhinge
13. Robust CV: MAD / |median|
    Robust Coefficient of Variation using MAD and the magnitude of the median.
    Always non-negative. Resistant to outliers, useful for comparing variability.
    https://en.wikipedia.org/wiki/Robust_measures_of_scale
14. Normalized MAD: MAD / 0.6745 (≈ 1.4826 * MAD)
    Robust estimate of the standard deviation, consistent with stddev for normal data.
    https://en.wikipedia.org/wiki/Median_absolute_deviation
15. Normalized IQR: IQR / 1.349
    Robust estimate of the standard deviation, consistent with stddev for normal data.
16. Robust Z-Score of Min: 0.6745 * (min - median) / MAD
    Iglewicz-Hoaglin modified z-score of the minimum.
    Values beyond ±3.5 are commonly flagged as potential outliers.
17. Robust Z-Score of Max: 0.6745 * (max - median) / MAD
    Iglewicz-Hoaglin modified z-score of the maximum.
18. Kelly Skewness: (P90 + P10 - 2*median) / (P90 - P10)
    Percentile-based skewness. Less sensitive to extreme tails than moment skewness,
    and uses more of the distribution than quartile skewness.
    Requires the 10th & 90th percentiles (included in the default percentile list).
19. P90/P10 Ratio: P90 / P10
    Common spread/inequality ratio. Only computed when P10 > 0.
20. Zero Share: n_zero / (n_zero + n_positive + n_negative)
    Share of non-null numeric values that are exactly zero (zero-inflation).
21. Berger-Parker Dominance: mode_occurrences / row count
    Share of rows taken by the most frequent value (NULL counts as a value, as in mode).
    Works for all field types. Not meaningful on weighted stats.
    https://en.wikipedia.org/wiki/Diversity_index#Berger%E2%80%93Parker_index
22. Moment Skewness: adjusted Fisher-Pearson standardized moment coefficient (G1).
    Moment-based counterpart to the quantile-based `skewness` from stats.
    Positive values indicate right skew, negative values indicate left skew.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Skewness#Sample_skewness
23. Kurtosis: Measures the "tailedness" of the distribution (sample excess kurtosis, G2).
    Positive values indicate heavy tails, negative values indicate light tails.
    Values near 0 indicate a normal distribution.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Kurtosis
24. Bimodality Coefficient: Measures whether a distribution has two modes (peaks) or is unimodal.
    BC > 0.555 (the value for a uniform distribution) suggests bimodal/multimodal.
    Computed as (G1² + 1) / (G2 + 3(n-1)² / ((n-2)(n-3))), using moment skewness and kurtosis.
    Heavily skewed unimodal data can also exceed 0.555.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Bimodality
25. Jarque-Bera Test: (n/6) * (S² + K²/4)
    Standard test for normality, where S and K are the (biased) moment skewness and
    excess kurtosis.
    Also computes jarque_bera_pvalue (from chi-squared distribution with 2 df).
    Low p-values (< 0.05) indicate the data is NOT normally distributed.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Jarque%E2%80%93Bera_test
26. Gini Coefficient: Measures inequality/dispersion in the distribution.
    Values range from 0 (perfect equality) to 1 (maximum inequality).
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Gini_coefficient
27. Atkinson Index: Measures inequality in the distribution with a sensitivity parameter.
    Values range from 0 (perfect equality) to 1 (maximum inequality).
    The Atkinson Index is a more general form of the Gini coefficient that allows for
    different sensitivity to inequality. Sensitivity is configurable via --epsilon.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Atkinson_index
28. Theil Index: (1/n) * Σ((x_i / mean) * ln(x_i / mean))
    Measures inequality/concentration. Unlike Gini, it is decomposable into
    within-group and between-group components. Only computed for positive values.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Theil_index
29. Mean Absolute Deviation (from mean): (1/n) * Σ|x_i - mean|
    Average absolute distance from the mean. Different from MAD (which uses median).
    Less robust but more statistically efficient than MAD.
    Requires --advanced flag.
30. Hoover Index: Σ|x_i - mean| / (2 * Σx_i)
    Share of the total that would have to be redistributed to reach equality (0 to 1).
    Only computed for non-negative numeric data. Requires --advanced flag.
    https://en.wikipedia.org/wiki/Hoover_index
31. L-CV: λ2 / λ1
    Coefficient of L-variation - a robust, bounded analogue of the CV based on
    L-moments (linear combinations of order statistics). Only computed for numeric data
    with a positive mean; 0 for a constant column. Requires --advanced flag.
    https://en.wikipedia.org/wiki/L-moment
32. L-Skewness: τ3 = λ3 / λ2
    Robust analogue of skewness, bounded in [-1, 1]; exists whenever the mean does.
    Requires --advanced flag.
33. L-Kurtosis: τ4 = λ4 / λ2
    Robust analogue of kurtosis. About 0.1226 for a normal distribution. The population
    value lies in [-1/4, 1], but the sample estimate can fall below -1/4 for small n
    (e.g. 0,0,6,6 gives -1.5). Requires --advanced flag.
34. Lag-1 Autocorrelation: Σ(x_t - mean)(x_{t+1} - mean) / Σ(x_t - mean)²
    Correlation between consecutive non-null values in file order. Values near 1 indicate
    a trend, drift or clustered/sorted data; near 0 no serial dependence; negative values
    alternation. Requires --advanced flag.
    https://en.wikipedia.org/wiki/Autocorrelation
35. Benford MAD: mean absolute deviation between the first-significant-digit
    proportions and Benford's law. Nigrini's thresholds: < 0.006 close conformity,
    < 0.012 acceptable, < 0.015 marginal, otherwise nonconformity - a data quality or
    fabrication signal. Only computed for numeric data with at least 100 non-zero values
    spanning at least two orders of magnitude. Requires --advanced flag.
    https://en.wikipedia.org/wiki/Benford%27s_law
36. Shannon Entropy: Measures the information content/uncertainty in the distribution.
    Higher values indicate more diversity, lower values indicate more concentration.
    Values range from 0 (all values identical) to log2(n) where n is the number of unique values.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Entropy_(information_theory)
37. Normalized Entropy: Normalized version of Shannon Entropy scaled to [0, 1].
    Values range from 0 (all values identical) to 1 (all values equally distributed).
    Computed as shannon_entropy / log2(cardinality).
    Requires shannon_entropy (from --advanced flag) and cardinality (from base stats).
38. Simpson's Diversity Index: 1 - Σ(p_i²)
    Probability that two randomly chosen values are different.
    Ranges from 0 (all identical) to 1 (all unique). More intuitive than entropy.
    Requires --advanced flag (computed alongside entropy from frequency data).
    https://en.wikipedia.org/wiki/Diversity_index#Simpson_index
39. Winsorized Mean: Replaces values below/above thresholds with threshold values, then computes mean.
    All values are included in the calculation, but extreme values are capped at thresholds.
    https://en.wikipedia.org/wiki/Winsorized_mean
    Also computes (<PCT> is the threshold suffix of the mean column, e.g. 25pct or 5pct):
    winsorized_stddev_<PCT>, winsorized_variance_<PCT>, winsorized_cv_<PCT>,
    winsorized_range_<PCT>, and winsorized_<PCT>_stddev_ratio
    (winsorized stddev / overall stddev). Note the ratio column interpolates <PCT>
    before _stddev_ratio, unlike the others.
40. Trimmed Mean: Excludes values outside thresholds, then computes mean.
    Only values within thresholds are included in the calculation.
    https://en.wikipedia.org/wiki/Truncated_mean
    Also computes (<PCT> is the threshold suffix of the mean column, e.g. 25pct or 5pct):
    trimmed_stddev_<PCT>, trimmed_variance_<PCT>, trimmed_cv_<PCT>, trimmed_range_<PCT>,
    and trimmed_<PCT>_stddev_ratio (trimmed stddev / overall stddev). Note the ratio
    column interpolates <PCT> before _stddev_ratio, unlike the others.
    By default, uses Q1 and Q3 as thresholds (25% winsorization/trimming).
    With --use-percentiles, uses configurable percentiles (e.g., 5th/95th) as thresholds
    with --pct-thresholds.

In addition, it computes the following univariate outlier statistics (24 outlier statistics total).
https://en.wikipedia.org/wiki/Outlier
(requires --quartiles or --everything in stats):

Outlier Counts (7 statistics):
  - outliers_extreme_lower_cnt: Count of values below the lower outer fence
  - outliers_mild_lower_cnt: Count of values between lower outer and inner fences
  - outliers_normal_cnt: Count of values between inner fences (non-outliers)
  - outliers_mild_upper_cnt: Count of values between upper inner and outer fences
  - outliers_extreme_upper_cnt: Count of values above the upper outer fence
  - outliers_total_cnt: Total count of all outliers (sum of extreme and mild outliers)
  - outliers_percentage: Percentage of values that are outliers

Outlier Descriptive Statistics (6 statistics):
  - outliers_mean: Mean value of outliers
  - non_outliers_mean: Mean value of non-outliers
  - outliers_to_normal_mean_ratio: Ratio of outlier mean to non-outlier mean
  - outliers_min: Minimum value among outliers
  - outliers_max: Maximum value among outliers
  - outliers_range: Range of outlier values (max - min)

Outlier Variance/Spread Statistics (7 statistics):
  - outliers_stddev: Standard deviation of outlier values
  - outliers_variance: Variance of outlier values
  - non_outliers_stddev: Standard deviation of non-outlier values
  - non_outliers_variance: Variance of non-outlier values
  - outliers_cv: Coefficient of variation for outliers (stddev / mean)
  - non_outliers_cv: Coefficient of variation for non-outliers (stddev / mean)
  - outliers_normal_stddev_ratio: Ratio of outlier stddev to non-outlier stddev

Outlier Impact Statistics (2 statistics):
  - outlier_impact: Difference between overall mean and non-outlier mean
  - outlier_impact_ratio: Relative impact (outlier_impact / non_outlier_mean)

Outlier Boundary Statistics (2 statistics):
  - lower_outer_fence_zscore: Z-score of the lower outer fence boundary
  - upper_outer_fence_zscore: Z-score of the upper outer fence boundary

  These outlier statistics require reading the original CSV file and comparing each
  value against the fence thresholds.
  Fences are computed using the IQR method:
    inner fences at Q1/Q3 ± 1.5*IQR, outer fences at Q1/Q3 ± 3.0*IQR.

These univariate statistics are only computed for numeric and date/datetime columns
where the required base univariate statistics (mean, median, stddev, etc.) are available.
Univariate outlier statistics additionally require that quartiles (and thus fences) were
computed when generating the stats CSV.
Winsorized/trimmed means require either Q1/Q3 or percentiles to be available.
The --advanced statistics (Moment Skewness, Kurtosis, Gini, Atkinson, L-moments, etc.)
require reading the original CSV file to collect all values for computation.

BIVARIATE STATISTICS:

The `moarstats` command also computes the following 9 bivariate statistics:
 1. Pearson's correlation
    Measures linear correlation between two numeric/date fields.
    Values range from -1 (perfect negative correlation) to +1 (perfect positive correlation).
    0 indicates no linear correlation.
    https://en.wikipedia.org/wiki/Pearson_correlation_coefficient
 2. Spearman's rank correlation
    Measures monotonic correlation between two numeric/date fields.
    Values range from -1 (perfect negative correlation) to +1 (perfect positive correlation).
    0 indicates no monotonic correlation.
    https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient
 3. Kendall's tau
    Measures monotonic correlation between two numeric/date fields.
    Values range from -1 (perfect negative correlation) to +1 (perfect positive correlation).
    0 indicates no monotonic correlation.
    https://en.wikipedia.org/wiki/Kendall_rank_correlation_coefficient
 4. Covariance
    Measures the linear relationship between two numeric/date fields.
    Values range from negative infinity to positive infinity.
    0 indicates no linear relationship.
    https://en.wikipedia.org/wiki/Covariance
 5. Mutual Information
    Measures the amount of information obtained about one field by observing another.
    Values range from 0 (independent) to positive infinity.
    https://en.wikipedia.org/wiki/Mutual_information
 6. Normalized Mutual Information
    Normalized version of mutual information, scaled by the geometric mean of individual entropies.
    Values range from 0 (independent) to 1 (perfectly dependent).
    https://en.wikipedia.org/wiki/Mutual_information#Normalized_variants
 7. Theil's U (uncertainty coefficient)
    Directed measure of how much knowing one field reduces uncertainty about the other.
    Asymmetric, so two columns are emitted: u_field2_given_field1 and u_field1_given_field2.
    Values range from 0 (no reduction) to 1 (fully determined).
    Selected with `u` in --bivariate-stats (or via "all").
    https://en.wikipedia.org/wiki/Uncertainty_coefficient
 8. Cramér's V: sqrt(χ² / (n * (min(r, c) - 1)))
    Chi-squared based association between two fields of any type, from the same
    joint frequency table as mutual information. Ranges from 0 (independent) to 1.
    Selected with `cramersv` in --bivariate-stats (or via "all").
    https://en.wikipedia.org/wiki/Cram%C3%A9r%27s_V
 9. Linear Regression: ordinary least-squares fit of field2 on field1
    Emits regression_slope, regression_intercept and r_squared (the coefficient of
    determination; empty when field2 is constant) for numeric/date field pairs, from the
    same streaming state as Pearson's correlation. Selected with `regression` in --bivariate-stats (or via "all").
    https://en.wikipedia.org/wiki/Simple_linear_regression

These bivariate statistics are computed when the `--bivariate` flag is used
and require an indexed CSV file (index will be auto-created if missing).
Bivariate statistics are output to a separate file: `<FILESTEM>.stats.bivariate.csv`.
The file is always rewritten - with just a header row if no field pair produced a statistic -
so it never holds stale results from an earlier run. A header name that repeats in the input is
written as name, name_2, name_3, ... (the `safenames` convention), so each column's pairs stay
distinguishable.

The correlation statistics (pearson, spearman, kendall, covariance & regression) only use
numeric, date and boolean fields. String fields only feed the frequency-based statistics
(mi, nmi, u & cramersv).
All-unique fields (cardinality >= row count, e.g. continuous measurements and IDs) keep
their correlation statistics, but their frequency-based statistics are left empty, as
mutual information against an all-unique field just saturates at log(n). Read ID column
correlations with care: a sequential ID correlates with a creation date simply because
IDs are issued in order.

Bivariate statistics require reading the entire CSV file and are computationally VERY expensive.
For large files (>= 10k records), parallel chunked processing is used when an index is available.
For smaller files or when no index exists, sequential processing is used.

MULTI-DATASET BIVARIATE STATISTICS:

When using the `--join-inputs` flag, multiple datasets can be joined internally before
computing bivariate statistics. This allows analyzing bivariate statistics across datasets
that share common join keys. The joined dataset is saved as a temporary file that is
automatically deleted after computing the bivariate statistics.
The bivariate statistics are saved to `<FILESTEM>.stats.bivariate.joined.csv`.

Non-finite numeric tokens ("NaN", "Infinity", "-Infinity", and their case variants) are
excluded from moarstats computations — the parser in moarstats filters them out before they
reach correlation, variance and mean calculations, preventing a single bad cell from silently
poisoning the results. Note that the baseline `stats` command may still count these tokens
as Float observations, so the `type`/`null_count` columns in `<FILESTEM>.stats.csv` are not
affected by this filter.

Examples:

  # Add moar stats to existing stats file
  qsv moarstats data.csv

  # Generate baseline stats first with custom options, then add moar stats
  qsv moarstats data.csv --stats-options "--everything --infer-dates"

  # Compute bivariate statistics between fields
  qsv moarstats data.csv --bivariate

  # Compute even more bivariate statistics
  qsv moarstats data.csv --bivariate --bivariate-stats pearson,spearman,kendall,mi,nmi,covariance

  # Join multiple datasets and compute bivariate statistics
  qsv moarstats data.csv --bivariate --join-inputs customers.csv,products.csv --join-keys cust_id,prod_id

  # Join multiple datasets and compute bivariate statistics with different join type
  qsv moarstats data.csv --bivariate --join-inputs customers.csv,products.csv --join-keys cust_id,prod_id --join-type left

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_moarstats.rs.
See also https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#moarstats

Usage:
    qsv moarstats [options] [<input>]
    qsv moarstats --help

moarstats options:
    --advanced             Compute Moment Skewness, Kurtosis, Shannon Entropy,
                           Bimodality Coefficient, Jarque-Bera, Gini Coefficient,
                           Atkinson Index, Theil Index, Mean Absolute Deviation,
                           Hoover Index, L-moment ratios, Lag-1 Autocorrelation,
                           Benford MAD and Simpson's Diversity Index.
                           These advanced statistics computations require reading the
                           original CSV file to collect all values
                           for computation and are computationally expensive.
                           Further, Entropy computation requires the frequency command
                           to be run with --limit 0 to collect all frequencies.
                           An index will be auto-created for the original CSV file
                           if it doesn't already exist to enable parallel processing.
    -e, --epsilon <n>      The Atkinson Index Inequality Aversion parameter.
                           Epsilon controls the sensitivity of the Atkinson Index to inequality.
                           The higher the epsilon, the more sensitive the index is to inequality.
                           Typical values are 0.5 (standard in economic research),
                           1.0 (natural boundary), or 2.0 (useful for poverty analysis).
                           [default: 1.0]
    --stats-options <arg>  Options to pass to the stats command if baseline stats need
                           to be generated. The options are passed as a single string
                           that will be split by whitespace.
                           [default: --infer-dates --infer-boolean --cardinality --mode --mad --quartiles --percentiles --force --stats-jsonl]
    --round <n>            Round statistics to <n> decimal places. Rounding follows
                           Midpoint Nearest Even (Bankers Rounding) rule.
                           [default: 4]
    --use-percentiles      Use percentiles instead of Q1/Q3 for winsorization/trimming.
                           Requires percentiles to be computed in the stats CSV.
   --pct-thresholds <arg>  Comma-separated percentile pair (e.g., "10,90") to use
                           for winsorization/trimming when --use-percentiles is set.
                           Both values must truncate to whole percentiles between
                           1 and 100, and lower < upper. The thresholds are
                           automatically merged into the --percentile-list of the
                           stats run, and an existing stats CSV computed with a
                           percentile list that lacks them is recomputed.
                           [default: 5,95]
 --xsd-gdate-scan <mode>   Gregorian XSD date type detection mode.
                           "quick": Fast detection using min/max values.
                                    Produces types with ?? suffix (less confident).
                           "thorough": Comprehensive detection checking all percentile values.
                                     Slower but ensures all values match the pattern.
                                     Produces types with ? suffix (more confident).
                           [default: quick]

                           BIVARIATE STATISTICS OPTIONS:
    -B, --bivariate        Enable bivariate statistics computation.
                           Requires indexed CSV file (index will be auto-created if missing).
                           Computes the pairwise statistics selected with --bivariate-stats
                           between columns (pearson & covariance by default). The bivariate
                           statistics are saved to a separate file in the same directory as the input:
                           <FILESTEM>.stats.bivariate.csv.
    -S, --bivariate-stats <stats>
                           Comma-separated list of bivariate statistics to compute.
                           Options: pearson, spearman, kendall, covariance, mi (mutual information),
                           nmi (normalized mutual information), u (Theil's directed uncertainty
                           coefficient; emits u_field2_given_field1 and u_field1_given_field2),
                           cramersv (Cramér's V) and regression (slope, intercept & r_squared).
                           Use "all" to compute all statistics or "fast" to compute only
                           pearson & covariance, which is much faster as it doesn't require storing
                           all values and uses streaming algorithms.
                           [default: fast]
    -C, --cardinality-threshold <n>
                           Skip mutual information (mi/nmi/u) and cramersv for field pairs
                           where either field's cardinality exceeds this threshold. Such pairs
                           also skip building their joint-frequency table, which is the
                           dominant memory cost of --bivariate-stats all.
                           Defaults to half the row count, floored at 1000, so it stays inert
                           on small inputs and scales with large ones. Mutual information
                           between near-unique columns saturates at log(n) and is noise
                           regardless of how efficiently it is computed.
                           All-unique fields always skip these statistics,
                           regardless of this threshold.
    --bivariate-batch <n>  Process at most <n> field pairs per pass over the input,
                           bounding peak memory at the cost of extra passes.
                           Peak memory is otherwise O(columns^2) regardless of row
                           count - a 160-column, 100k-row (60 MB) input needs ~21 GiB
                           with mi/nmi/u enabled. Extra passes are cheap, so prefer
                           the largest <n> that fits.
                           Only applies to indexed input with >= 10,000 rows.
                           Set to 0 to process all pairs in one pass.
                           [default: 0]
    -J, --join-inputs <files>
                           Additional datasets to join. Comma-separated list of CSV files to join
                           with the primary input.
                           e.g.: --join-inputs customers.csv,products.csv
    -K, --join-keys <keys>
                           Join keys for each dataset. Comma-separated list of join key column names,
                           one per dataset. Must specify same number of keys as datasets (primary + addl).
                           e.g.: --join-keys customer_id,customer_id,product_id
    -T, --join-type <type>
                           Join type when using --join-inputs.
                           Valid values: inner, left, right, full
                           [default: inner]
    -p, --progressbar      Show progress bars when computing bivariate statistics.

Common options:
    --force                Force recomputing stats even if valid precomputed stats
                           cache exists.
    -j, --jobs <arg>       The number of jobs to run in parallel.
                           This works only when the given CSV has an index.
                           Note that a file handle is opened for each job.
                           When not set, the number of jobs is set to the
                           number of CPUs detected.
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of overwriting the stats CSV file.
```
## qsv partition

```text
Partitions the given CSV data into chunks based on the value of a column.

See `split` command to split a CSV data by row count, by number of chunks or
by kb-size.

The files are written to the output directory with filenames based on the
values in the partition column and the `--filename` flag.

Note: To account for case-insensitive file system collisions (e.g. macOS APFS
and Windows NTFS), the command will add a number suffix to the filename if the
value is already in use.

EXAMPLE:

Partition nyc311.csv file into separate files based on the value of the
"Borough" column in the current directory:
  $ qsv partition Borough . --filename "nyc311-{}.csv" nyc311.csv

will create the following files, each containing the data for each borough:
    nyc311-Bronx.csv
    nyc311-Brooklyn.csv
    nyc311-Manhattan.csv
    nyc311-Queens.csv
    nyc311-Staten_Island.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_partition.rs.
See also https://github.com/dathere/qsv/wiki/Joins-and-Set-Ops#partition

Usage:
    qsv partition [options] <column> <outdir> [<input>]
    qsv partition --help

partition arguments:
    <column>                 The column to use as a key for partitioning.
                             You can use the `--select` option to select
                             the column by name or index, but only one
                             column can be used for partitioning.
                             See `select` command for more details.
    <outdir>                 The directory to write the output files to.
    <input>                  The CSV file to read from. If not specified, then
                             the input will be read from stdin.

partition options:
    --filename <filename>    A filename template to use when constructing the
                             names of the output files.  The string '{}' will
                             be replaced by a value based on the partition column,
                             but sanitized for shell safety.
                             [default: {}.csv]
    -p, --prefix-length <n>  Truncate the partition column after the
                             specified number of bytes when creating the
                             output file.
    --drop                   Drop the partition column from results.
    --limit <n>              Limit the number of simultaneously open files.
                             Useful for partitioning large datasets with many
                             unique values to avoid "too many open files" errors.
                             Data is processed in batches until all unique values
                             are processed.
                             If not set, it will be automatically set to the
                             system limit with a 10% safety margin.
                             If set to 0, it will process all data at once,
                             regardless of the system's open files limit.

Common options:
    -h, --help               Display this message
    -n, --no-headers         When set, the first row will NOT be interpreted
                             as column names. Otherwise, the first row will
                             appear in all chunks as the header row.
    -d, --delimiter <arg>    The field delimiter for reading CSV data.
                             Must be a single character. (default: ,)
```
## qsv pivotp

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
See also https://github.com/dathere/qsv/wiki/SQL-and-Polars#pivotp

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
                  Stdin is not supported. A snappy-compressed (.sz) input is
                  decompressed first, and an --output ending in .sz is
                  snappy-compressed. Lines starting with QSV_COMMENT_CHAR are
                  skipped. QSV_POLARS_FLOAT_PRECISION and QSV_OUTPUT_BOM apply
                  to the output, as in sqlp and joinp.

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
                              quantile@<p> - Quantile at probability p in [0, 1] using linear interpolation.
                                             Alias: q@<p>. Examples: quantile@0.95, q@0.5
                                             (q@0.5 is equivalent to median for even-length groups).
                              len - Count of values
                              item - Get single value from group. Raises error if there are multiple values.
                              smart - use value column data type & statistics to pick an aggregation.
                                      Always uses type, cardinality, sparsity, CV, sign
                                      distribution (n_negative/n_positive), and sort_order
                                      from streaming stats.
                                      High variability means a CV above 100% (stddev > mean).
                                      When the stats cache includes non-streaming stats (from a
                                      prior `stats --everything` or `stats --mode`), also uses
                                      mode_count.
                                      With a single --values column, smart first runs
                                      moarstats --advanced to enrich the input's stats cache
                                      (writing <stem>.stats.csv, .stats.csv.json and
                                      .stats.csv.data.jsonl beside it) unless the cache already
                                      has those stats. This one-time pass reads the whole file;
                                      skip it with --no-moarstats. It is also skipped with an
                                      explicit --delimiter, stdin and special formats.
                                      The moarstats stats used are outlier profile, Pearson
                                      skewness, MAD/stddev ratio, median/mean ratio and quartile
                                      coefficient of dispersion (the two ratios only for
                                      positive data), moment skewness (|G1| >= 1 picks median;
                                      Pearson skewness is the fallback), kurtosis, bimodality
                                      (bimodality coefficient >= 0.60 with negative excess
                                      kurtosis), entropy and Gini coefficient.
                                      A single-value column uses first.
                                      The choice depends on the data, so pass an explicit --agg
                                      to pin a result across qsv versions.
                                      For Date/DateTime values, checks sparsity and sort order.
                                      Will only work if there is one value column, otherwise
                                      it falls back to `first`
                            [default: smart]
    --sort-columns          Sort the transposed columns by name. (pivot mode only)
    --maintain-order        Accepted for compatibility. Output is always in first-appearance
                            order: rows follow their index values' first appearance and
                            pivoted columns their <on-cols> values' first appearance.
    --col-separator <arg>   The separator in generated column names in case of multiple --values columns.
                            (pivot mode only; ignored in group-by mode) [default: _]
    --validate              Report the pivot column(s)' cardinality before pivoting. Informational
                            only - it does not refuse a pivot; --max-columns does that.
                            (pivot mode only)
    --max-columns <n>       Maximum number of columns the pivot may create before it is refused.
                            Guards against pivoting on a high-cardinality column, which can
                            exhaust memory. Unlike --validate, this ALWAYS runs.
                            Set to 0 for no limit, for a deliberately wide pivot.
                            (pivot mode only; ignored in group-by mode) [default: 100000]
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
    --no-moarstats          For smart aggregation, do not run moarstats --advanced to
                            enrich the stats cache. Smart aggregation then uses whatever
                            stats are already cached (or basic `stats --cardinality` stats).

Common options:
    -h, --help              Display this message
    -o, --output <file>     Write output to <file> instead of stdout.
    -d, --delimiter <arg>   The field delimiter for reading/writing CSV data.
                            Must be a single character. If not set, QSV_DEFAULT_DELIMITER
                            is used, else ','. A .tsv/.tab (tab) or .ssv (semicolon)
                            extension on the input or --output file sets that file's
                            delimiter. (default: ,)
    -q, --quiet             Do not return smart aggregation chosen nor pivot result shape to stderr.
```
## qsv pragmastat

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
  * Date/DateTime pairs: ratio is suppressed for --twosample and --compare2
    because it depends on the arbitrary 1970 epoch origin and isn't meaningful
    for dates. shift, disparity, and their bounds remain populated.
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
  https://github.com/AndreyAkinshin/pragmastat/releases/download/v14.0.1/pragmastat-v14.0.1.pdf
  https://pragmastat.dev/ (latest version)

See also https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#pragmastat

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
## qsv pro

```text
Interact with qsv pro API. Learn more about qsv pro at: https://qsvpro.dathere.com.

- qsv pro must be running for this command to work as described.
- Some features of this command require a paid plan of qsv pro and may require an Internet connection.

The qsv pro command has subcommands:
    lens:     Run csvlens on a local file in a new Alacritty terminal emulator window (Windows only).
    workflow: Import a local file into the qsv pro Workflow (Workflow must be open).

See also https://github.com/dathere/qsv/wiki/Integrations#qsv-pro-bridge

Usage:
    qsv pro lens [options] [<input>]
    qsv pro workflow [options] [<input>]
    qsv pro --help

pro arguments:
    <input>               The input file path to send to the qsv pro API.
                          This must be a local file path, not stdin.
                          Workflow supports: CSV, TSV, SSV, TAB, XLSX, XLS, XLSB, XLSM, ODS.

Common options:
    -h, --help            Display this message
```
## qsv profile

```text
Profile a CSV (local path or URL) and emit a `.metadata.json` file carrying
five top-level blocks:

  `dpp`        — inferred dataset signals: lat/lon/date columns, file size,
                 row count, encoding, etc. (the legacy datapusher-plus
                 inference block).
  `stats`      — per-column summary statistics from `qsv stats`.
  `frequency`  — per-column value counts from `qsv frequency`.
  `ckan`       — a CKAN-shaped block (package + resources) that
                 datapusher-plus consumes to prepopulate CKAN packages.
  `projection` — the dataset re-expressed in the active profile's metadata
                 vocabulary. Default is DCAT-US v3, emitted in its canonical
                 form: plain JSON with unprefixed keys and no `@context`,
                 validating against the schemas data.gov's own validator at
                 https://harvest.data.gov/validate/ runs. Bundled alternates are
                 dcat-ap-v3 (EU portals), croissant (ML/AI registries) and
                 geoconnex (water-data federations). Consumable directly by
                 data.gov harvesters, EU DCAT-AP catalogs, mlcommons /
                 Hugging Face / Kaggle, and Internet of Water tooling.

Behind the scenes qsv runs the same statistical + frequency analysis
datapusher-plus (DP+) runs in CKAN, builds a Jinja2 evaluation context from
the results, and — when an optional CKAN scheming YAML spec is supplied —
evaluates the spec's `formula` / `suggestion_formula` templates against that
context. Jinja2 helpers and filters are a native Rust port of DP+'s
`jinja2_helpers.py`, built on `minijinja`.

For DCAT-US v3 the projection also COMPUTES properties that are tedious to
author by hand, from the same statistics: temporal coverage and resolution
(an exact xsd:duration: a regular series' step, else recording precision),
spatial bounding box (excluding out-of-range and (0, 0) placeholder
coordinates) and resolution - from latitude/longitude columns or, without
them, a WKT `POINT (longitude latitude)` column - an update schedule (only for
a regular calendar series), the content language, DQV quality measurements
(completeness, plus duplicate rows and CSV/UTF-8 validity with `--validate`),
and a CSVW table schema with per-column constraints (required, ranges,
lengths, enumerations, primary key). Values
that are generated, detected or estimated rather than measured (a
description, the language, the schedule, the temporal and spatial resolution)
form an "inferred" tier that the publisher's own metadata replaces;
`projection_provenance` lists them (and LLM column annotations, which only an
override replaces). A generated
description carries a disclosure and a review warning, so it never passes
for a human-authored one.

When the input is a URL whose response carries DCAT markup (HTTP
`Link: rel=describedBy`), qsv discovers the publisher's stated metadata and
merges it as a base layer beneath the inferred projection.

For an example CKAN scheming YAML spec, see:
  https://github.com/dathere/datapusher-plus/blob/main/ckanext/datapusher_plus/dataset-druf.yaml

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_profile.rs.
See also https://github.com/dathere/qsv/wiki/Metadata-Profiling

Examples:

  # Quick: dpp/stats/frequency + default DCAT-US v3 projection.
  $ qsv profile data.csv

  # Pipe stdin; output defaults to `stdin.metadata.json`.
  $ cat data.csv | qsv profile

  # URL input: discover the publisher's DCAT markup and merge it as a base layer.
  $ qsv profile https://data.example.gov/datasets/sample.csv

  # Seed publisher/contact info from a JSON file; write to a chosen output path.
  $ qsv profile data.csv --initial-context publisher.json -o data.metadata.json

  # data.gov-style harvest: validate against DCAT-US v3 JSON Schema, abort on
  # mandatory-field violations, wrap in a Catalog envelope.
  $ qsv profile data.csv --validate --strict --catalog -o data.metadata.json

  # DCAT-AP v3 for EU data portals; `pyshacl` validates the bundled SHACL shapes.
  $ qsv profile open-data.csv --profile dcat-ap-v3 --validate --strict

  # Croissant JSON-LD for an ML dataset; `mlcroissant` validates the output.
  $ qsv profile train.csv --profile croissant --validate -o train.croissant.json

  # Geoconnex JSON-LD for hydrologic data (qsv built with the `geoconnex` feature).
  $ qsv profile gages.csv --profile geoconnex --validate --strict

  # Evaluate a CKAN scheming spec: Jinja2 formulas compute spatial/temporal
  # extents, accrual periodicity, and other derived fields.
  $ qsv profile data.csv --spec dataset-druf.yaml -o data.metadata.json

  # CKAN-only output: drop the `projection` block, keep dpp/stats/frequency/ckan.
  $ qsv profile data.csv --no-projection --spec dataset-druf.yaml

  # Custom YAML profile from disk (embedded names always win over same-named
  # files, so use a non-clashing name for custom profiles).
  $ qsv profile data.csv --profile ./my-org-dcat.yaml --validate

Usage:
    qsv profile [options] [<input>]
    qsv profile --help

profile argument:
    <input>                   Path or URL to the CSV to profile. When `-` or
                              omitted, reads from stdin.
                              When the URL has DCAT markup, qsv will attempt to
                              discover and ingest it as a base layer of metadata
                              (unless --no-dcat-discovery is set). See --no-dcat-discovery
                              and --dcat-discovery-timeout for details and opt-out.

profile options:
    --spec <yaml>             CKAN scheming YAML spec file. If omitted, only the
                              inferred `dpp` block (lat/lon/date columns, dataset
                              stats) is emitted; no formulas are evaluated.
    --initial-context <json>  JSON file providing seed values for the package /
                              resource dicts plus optional JSON-Pointer
                              overrides for the final projection block. Replaces
                              the older --package-meta / --resource-meta
                              flags. Top-level keys: `package`, `resource`,
                              `dataset_info`. Each leaf value may be wrapped
                              as {"value": ..., "force": true} to mark it as
                              overriding any value discovered from URL DCAT
                              markup AND any value qsv inferred. Force is
                              honored across all three subtrees: dataset_info
                              entries override their target path verbatim;
                              package / resource entries route through the
                              active profile's `field_mappings:` table (e.g.
                              `package.title force=true` lands at
                              `/projection/title`, beating inference and
                              discovery). Forced values for slots the profile
                              does not surface are silently dropped (no-op).
                              See tests/resources/profile/dcat-init-context.README.md
                              for a fully-populated example.
    --no-projection           Skip the metadata projection block (dcat/croissant/
                              geoconnex, depending on the active profile).
    --no-ckan                 Skip the CKAN-shape block.
    --croissant-frequency     Embed per-column value-frequency distributions in
                              the metadata projection. The croissant profile
                              renders them as inline cr:RecordSets (one
                              `<col>-frequency` RecordSet of {value, count,
                              percentage} rows per column), per the spec's
                              "distribution of values is a statistic on the
                              field" guidance. Off by default (keeps the
                              projection compact); the raw counts always remain
                              in the top-level `frequency` block regardless.
                              Other bundled profiles ignore this flag.
    --locate <mode>           Name the places the data covers, as DCAT-US v3
                              `spatial` Locations, by looking up the densest
                              coordinate cells (up to 40, row-weighted) with
                              `qsv geocode`. <mode> is one of:
                                geonames - label the bounding box with the
                                           place, admin1 or country that 80%
                                           of the sampled rows share (offline
                                           Geonames index).
                                census   - add each US state and county
                                           holding at least 5% of the sampled
                                           rows (the heaviest state always;
                                           up to 10 counties), keyed by
                                           Census GEOID (US
                                           Census Geocoder: online, keyless,
                                           cached). State and county
                                           columns, when they resolve, supply
                                           these instead, with or without
                                           coordinates, as they name every
                                           row exactly: states as USPS, FIPS
                                           or names; counties as names or
                                           GEOIDs, matched exactly within each
                                           row's state (TIGERweb county
                                           names). A name several counties
                                           share is noted, not guessed.
                                both     - geonames and census.
                              Also adds the coordinates' centroid. A lookup
                              that cannot run is noted in projection_warnings;
                              the bounding box is kept. Default: off.
    --describegpt <json>      Use a `qsv describegpt --format json` result as
                              LLM-inferred metadata (see also --infer). Its
                              Description becomes the description, its Tags
                              the keywords and its Dictionary labels and
                              descriptions annotate the CSVW columns - all as
                              inferred values, which supplied or discovered
                              metadata replaces. describegpt's attribution
                              footer moves to the `llm_attribution` block and
                              the description gets a one-line disclosure.
    --infer                   Run `qsv describegpt --all` on the input and use
                              its result as with --describegpt. The LLM is
                              configured through describegpt's QSV_LLM_*
                              environment variables. If it cannot run, a
                              warning is added and the statistics-based
                              description is used.
    --tag-vocab <file>        With --describegpt or --infer: a local
                              `tag,description` CSV (the format describegpt
                              uses for its own tag vocabulary). Only tags in it are
                              kept - describegpt only asks the LLM to keep to
                              the vocabulary - and they also become `theme`
                              Concepts carrying the vocabulary's description.
    --dcat-legacy-license     Also emit `license` on the Dataset, alongside
                              the Distribution-level copy. Both are valid
                              DCAT-US v3 (the Dataset-level property was
                              added upstream), but the migration guide
                              directs publishers to put license on each
                              Distribution, so that is what qsv emits by
                              default. Default: off.
    --no-dcat-discovery       Skip DCAT-markup discovery on URL inputs.
                              Discovery sniffs HTTP Link: rel=describedBy
                              (and, in future, sibling .metadata.json /
                              JSON-LD <script> blocks) to use the
                              publisher's stated metadata as a base layer.
    --dcat-discovery-timeout <secs>  Per-request timeout for DCAT-markup
                              discovery probes. Default: 5.
    --validate                Validate the emitted projection block against
                              the active profile's declared validators. For
                              dcat-us-v3 that's the vendored GSA JSON Schema
                              bundle (see resources/dcat-us-v3/); for
                              dcat-ap-v3 / geoconnex it's pyshacl over the
                              bundled SHACL shapes; for croissant it's
                              mlcroissant. Catches missing mandatory fields,
                              cardinality issues, and shape violations.
                              Violations append to projection_warnings by
                              default. Also runs `qsv validate` over the
                              input (CSV structure + UTF-8), so a passing
                              file is declared UTF-8 encoded and its
                              syntactic validity is recorded as a
                              quality measurement.
    --strict                  With --validate, fail the command on
                              Required-severity schema violations, or on
                              non-Info external-validator findings,
                              instead of just warning. Severity comes
                              from the DCAT-US v3 schema's own
                              requirementLevel annotations, so a missing
                              mandatory property aborts while a
                              recommended-field advisory does not.
                              Note:
                              RFC4180 structural failures from
                              `qsv validate` (emitted when a spec
                              declares `validators`) are always
                              appended as warnings, regardless of this
                              flag.
    --allow-external-validator
                              Opt in to spawning the validator binary
                              declared by `validation.external` when the
                              profile was loaded from an arbitrary YAML
                              file. Bundled profiles (dcat-us-v3,
                              dcat-ap-v3, croissant, geoconnex) always run
                              their declared external validators because
                              the profile content is vetted at qsv release
                              time. Without this flag, file-loaded
                              profiles emit a Recommended-severity
                              warning instead of running the binary, so
                              an untrusted YAML can't silently execute
                              arbitrary commands. Default: off.
    --catalog                 Wrap the emitted DCAT-US v3 Dataset inside a
                              Catalog envelope (Catalog{dataset:[...]}).
                              Useful for federation harvesters (data.gov,
                              CKAN ingest) that expect Catalog-shaped
                              top-level metadata. Default: off
                              (Dataset-only, backwards-compatible).
    --profile <name|path>     Metadata projection profile to use. Embedded
                              names: dcat-us-v3 (default), dcat-ap-v3,
                              croissant; geoconnex (when built with the
                              `geoconnex` feature, which no prebuilt binary
                              includes: build qsv with
                              `-F feature_capable,geoconnex`, or qsvdp
                              with `-F datapusher_plus,geoconnex`).
                              A path to a custom YAML profile is also
                              accepted; embedded names always win over
                              same-named files. See
                              resources/profiles/README.md for the schema
                              and authoring guide.
    --force                   Force recomputing cardinality and unique values
                              even if a stats cache file exists.
    -j, --jobs <arg>          The number of jobs to run in parallel for the
                              underlying stats/frequency passes. When not set,
                              the number of jobs is set to the number of CPUs
                              detected.
    -o, --output <file>       Output JSON path. Default: <input>.metadata.json.

Common options:
    -h, --help                Display this message
    -n, --no-headers          When set, the first row will not be interpreted
                              as headers. Namely, it will be processed with the
                              rest of the rows. Otherwise, the first row will
                              always appear as the header row in the output.
    -d, --delimiter <arg>     The field delimiter for reading CSV data.
                              Must be a single character.
    --memcheck                Check if there is enough memory to load the entire
                              CSV into memory using CONSERVATIVE heuristics.
```
## qsv prompt

```text
Open a file dialog to pick a file as input or save to an output file.

Examples:

  # Pick a single file as input to qsv stats using an INPUT file dialog,
  # pipe into qsv stats using qsv prompt, and browse the stats using qsv lens:
  qsv prompt | qsv stats | qsv lens

  # If you want to save the output of a command to a file using a save file OUTPUT dialog,
  # pipe into qsv prompt using the --fd-output flag:
  qsv prompt -m 'Pick a CSV file to summarize' | qsv stats -E | qsv prompt --fd-output

  # Prompt for a spreadsheet, and export to CSV using a save file dialog:
  qsv prompt -m 'Select a spreadsheet to export to CSV' -F xlsx,xls,ods | \
      qsv excel - | qsv prompt -m 'Save exported CSV to...' --fd-output

See also https://github.com/dathere/qsv/wiki/Conversion-and-IO#prompt

Usage:
    qsv prompt [options]
    qsv prompt --help

prompt options:
    -m, --msg <arg>        The prompt message to display in the file dialog title.
                           When not using --fd-output, the default is "Select a File".
                           When using --fd-output, the default is "Save File As".
    -F, --filters <arg>    The filter to use for the INPUT file dialog. Set to "None" to
                           disable filters. Filters are comma-delimited file extensions.
                           Defaults to csv,tsv,tab,ssv,xls,xlsx,xlsm,xlsb,ods.
                           If the polars feature is enabled, it adds avro,arrow,ipc,parquet,
                           json,jsonl,ndjson & gz,zst,zlib compressed files to the filter.
    -d, --workdir <dir>    The directory to start the file dialog in.
                           [default: .]
    -f, --fd-output        Write output to a file by using a save file dialog.
                           Used when piping into qsv prompt. Mutually exclusive with --output.
    --save-fname <file>    The filename to save the output as when using --fd-output.
                           [default: output.csv]
    --base-delay-ms <ms>   The base delay in milliseconds to use when opening INPUT dialog.
                           This is to ensure that the INPUT dialog is shown before/over the
                           OUTPUT dialog when using the prompt command is used in both INPUT
                           and OUTPUT modes in a single pipeline.
                           [default: 200]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> without showing a save dialog.
                           Mutually exclusive with --fd-output.
    -q, --quiet            Do not print --fd-output message to stderr.
```
## qsv pseudo

```text
Pseudonymise the value of a given column by replacing it with an
incremental identifier. See https://en.wikipedia.org/wiki/Pseudonymization

Once a value is pseudonymised, it will always be replaced with the same
identifier. This means that the same value will always be replaced with
the same identifier, even if it appears in different rows.

The incremental identifier is generated by using the given format string
and the starting number and increment.

EXAMPLE:

Pseudonymise the value of the "Name" column by replacing it with an
incremental identifier starting at 1000 and incrementing by 5:

  $ qsv pseudo Name --start 1000 --increment 5 --fmtstr "ID-{}" data.csv

If run on the following CSV data:

```csv
Name,Color
Mary,yellow
John,blue
Mary,purple
Sue,orange
John,magenta
Mary,cyan
```

will replace the value of the "Name" column with the following values:

```csv
Name,Color
ID-1000,yellow
ID-1005,blue
ID-1000,purple
ID-1010,orange
ID-1005,magenta
ID-1000,cyan
```

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_pseudo.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#pseudo

Usage:
    qsv pseudo [options] <column> [<input>]
    qsv pseudo --help

pseudo arguments:
    <column>                The column to pseudonymise. You can use the `--select`
                            option to select the column by name or index.
                            See `select` command for more details.
    <input>                 The CSV file to read from. If not specified, then
                            the input will be read from stdin.

Common options:
    -h, --help              Display this message
    --start <number>        The starting number for the incremental identifier.
                            [default: 0]
    --increment <number>    The increment for the incremental identifier.
                            Must be greater than 0.
                            [default: 1]
    --formatstr <template>  The format string for the incremental identifier.
                            The format string must contain a single "{}" which
                            will be replaced with the incremental identifier.
                            [default: {}]
    -o, --output <file>     Write output to <file> instead of stdout.
    -n, --no-headers        When set, the first row will not be interpreted
                            as headers.
    -d, --delimiter <arg>   The field delimiter for reading CSV data.
                            Must be a single character. (default: ,)
```
## qsv readstat

```text
Convert SAS, Stata & SPSS files to CSV.

EXPERIMENTAL: the readers this command is built on are young. Spot-check the
output against your source files before relying on a conversion, and please
report anything that looks wrong.

Supported input formats:
    SAS     .sas7bdat, .xpt, .xpt5, .xpt8
    Stata   .dta
    SPSS    .sav, .zsav, .por

Coded values are written as their underlying codes, not their labels, so the
conversion is lossless. SPSS durations (DTIME) are written as their number of
seconds, as SPSS stores them. Use --value-labels to decode them instead. SAS keeps
its value labels in a separate .sas7bcat format catalog, which --value-labels
finds next to the data file, or --sas7bcat names.

User-defined missing values ("sentinels") - SAS's .A to .Z & ._, Stata's .a
to .z, SPSS's declared missing codes - become empty cells by default, like any
other missing value. Use --sentinels-as to keep them. Without it, a warning
says how many sentinels were dropped & where. Counting them reads files on a
single thread, and SPSS files whole (see --batch), so it is skipped when the
option --jobs is above 1, and for SPSS files holding over about 128 MB of
data. As SPSS files declare their missing values, the warning then names the
variables that do instead. SAS & Stata files don't, so they get no warning.

The variable metadata these formats carry - variable labels, value labels,
missing-value codes, measure & display settings - can be dumped instead of the
data with --metadata. Or --dictionary writes it alongside the data, as a JSON
Schema data dictionary of the CSV written: variable labels become titles,
value labels an enum (when they cover every value written), and the rest is
kept under "x-qsv". It has the shape 'qsv describegpt --dictionary' writes, so
'qsv validate' & 'qsv viz smart --dictionary' read it - without an LLM.

Only part of a file can be read: --select picks variables, which the readers
skip over without decoding, and --offset, --limit & --sample pick rows. Stata,
uncompressed SPSS & SAS transport files jump straight to the --offset. SAS
datasets & compressed SPSS files still pass over the rows before it (decoding
them, for a SAS dataset at --jobs > 1), and .por files are read whole. Reading
stops once --limit is reached.

  Convert a SAS dataset to CSV:
    qsv readstat data.sas7bdat > data.csv

  Convert an SPSS file, decoding coded values to their labels:
    qsv readstat --value-labels survey.sav -o survey.csv

  Keep the sentinel codes of a SAS dataset, in a <name>_null column after each
  numeric variable:
    qsv readstat --sentinels-as value data.sas7bdat

  Keep them in the variables' own columns instead:
    qsv readstat --sentinels-as value --sentinels-embedded data.sas7bdat

  Keep the sentinels of two SPSS variables as their labels, leaving the other
  values as codes:
    qsv readstat --sentinels-as label --sentinels-columns q1,q2 survey.sav

  Read three variables & the first 1000 rows of a wide SPSS file:
    qsv readstat --select id,age,income --limit 1000 survey.sav

  Read every variable from "q1" to "q20", in file order:
    qsv readstat --select q1-q20 survey.sav

  Read every variable except two (a leading ! excludes those listed):
    qsv readstat --select '!notes,comments' survey.sav

  Take a reproducible random sample of 500 rows, in file order:
    qsv readstat --sample 500 --seed 42 data.sas7bdat

  Convert an SPSS file & write its data dictionary, then chart it with the
  variable labels as titles:
    qsv readstat --dictionary survey.schema.json survey.sav -o survey.csv
    qsv viz smart --dictionary survey.schema.json survey.csv

  Dump the variable dictionary of a Stata file:
    qsv readstat --metadata pretty-json panel.dta

  Dump the metadata of just two variables:
    qsv readstat --metadata json --select age,income panel.dta

  Pipe straight into another qsv command:
    qsv readstat data.sas7bdat | qsv stats

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_readstat.rs.

Usage:
    qsv readstat [options] [<input>]
    qsv readstat --help

readstat options:
    --metadata <fmt>       Dump variable metadata instead of the data.
                           Valid values: none, csv, json, pretty-json.
                           For SAS, the value labels are included when a
                           format catalog is used (see --value-labels).
                           [default: none]
    --value-labels         Decode coded values to their label strings
                           (e.g. 1 becomes "Male") instead of writing the
                           underlying codes. For SAS .sas7bdat files, the
                           labels come from the format catalog: the file
                           named by --sas7bcat, else <name>.sas7bcat or
                           formats.sas7bcat next to the data file. Not
                           supported for .xpt files.
    --sas7bcat <file>      The SAS format catalog (.sas7bcat) holding the
                           value labels of a .sas7bdat file, for use by
                           the options --value-labels, --sentinels-as label
                           & --metadata. It only names the catalog, so the
                           data needs one of the first two.
    --dictionary <file>    Also write a JSON Schema data dictionary of the
                           CSV written to <file>. Name it <stem>.schema.json
                           after the CSV & 'qsv viz smart' finds it on its
                           own. It describes the data as written, so the
                           other options shape it too: the types follow
                           the option --compress-numeric, the enums
                           follow --value-labels, & so on.
    --compress-numeric     Write float variables that only ever hold whole
                           numbers as integers, without the ".0" (e.g. 3.0
                           becomes 3). SPSS stores every number as a float, so
                           this matters most for SPSS files. It is decided per
                           variable, over the rows written: one value like 2.5
                           keeps the ".0" on every row of that variable. The
                           file is read twice - once to check the values.
                           With sentinel labels embedded, a variable with a
                           label that reads as a number (e.g. "1.0") keeps its
                           ".0", so the label is not rewritten.
    --sentinels-as <what>  Keep sentinels instead of writing them as empty
                           cells. Each eligible variable gets a <name>_null
                           column right after it, holding the sentinel of each
                           row that has one & empty otherwise.
                           Valid values: none, value, label.
                             none  - write them as empty cells, without the
                                     check & its warning.
                             value - the sentinel's code (e.g. .A or 99).
                             label - the sentinel's value label if it has one,
                                     else its code.
                           label labels only the sentinels: other values stay
                           codes unless --value-labels is also given.
                           SAS takes its sentinel labels from the format
                           catalog, found as for --value-labels. For SPSS,
                           value cannot be combined with --value-labels.
                           Not supported for .xpt & .por files. Tracking
                           sentinels reads files on a single thread, so the
                           option --jobs has no effect, and reads SPSS .sav
                           & .zsav files whole (see --batch).
    --sentinels-embedded   Write each sentinel into its variable's own column
                           instead of a <name>_null column. Those columns then
                           mix numbers & sentinels. Requires --sentinels-as.
    --sentinels-columns <list>  Comma-separated variables to keep sentinels
                           for. Requires --sentinels-as. By default, every
                           eligible variable: the numeric ones for SAS &
                           Stata, those with declared missing values for SPSS.
    --select <cols>        The variables to read, in the order given, using
                           qsv's select syntax: names, 1-based indices,
                           ranges (q1-q20) & /regex/, or a leading ! to
                           read every variable except those listed. See
                           'qsv select --help' for the full syntax. Variables
                           left out are skipped by the reader. Also applies
                           to the option --metadata, which then lists only
                           these variables.
    --offset <n>           Skip the first <n> rows. [default: 0]
    --limit <n>            Write at most <n> rows, counted after the
                           rows skipped by --offset.
    --sample <n>           Write a random sample of <n> rows, in file order,
                           drawn from the rows --offset & --limit select.
                           If there are no more than <n> such rows, all of
                           them are written.
    --seed <number>        Seed the random number generator of --sample,
                           so the same sample is drawn every time.
    -j, --jobs <arg>       Number of reader threads. [default: 1]
                           Raising it speeds up large uncompressed files at the
                           cost of memory, as out-of-order chunks have to be
                           buffered to keep the rows in source order. Row order
                           is preserved either way.
    -b, --batch <size>     Number of rows to read into memory at a time.
                           Does not apply to SPSS portable (.por) files - they
                           have no chunked reader upstream, so they are read
                           whole & memory scales with the file. Nor does it
                           apply to .sav & .zsav files while their sentinels
                           are tracked, which also reads them whole: with
                           the option --sentinels-as value or label, or by
                           the sentinel check when a variable declares
                           missing values & the file holds at most about
                           128 MB of data (see --sentinels-as none).
                           [default: 50000]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The delimiter to use when writing CSV data.
                           Must be a single character. (default: ,)
```
## qsv rename

```text
Rename the columns of a CSV efficiently. It has two modes of operation:

Positional mode (default):
The new column names are given as a comma-separated list of names.
The number of column names given MUST match the number of columns in the
CSV unless "_all_generic" is used.

Pairwise mode:
The new column names are given as a comma-separated list of pairs of old and new
column names. The format is "old1,new1,old2,new2,...".

Examples:
  Change the column names of a CSV with three columns:
  $ qsv rename id,name,title

  Rename only specific columns using pairs:
  $ qsv rename --pairwise oldname,newname,oldcol,newcol

  Replace the column names with generic ones (_col_N):
  $ qsv rename _all_generic

  Add generic column names to a CSV with no headers:
  $ qsv rename _all_generic --no-headers

  Use column names that contains commas and conflict with the separator:
  $ qsv rename '"Date - Opening","Date - Actual Closing"'

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_rename.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#rename

Usage:
    qsv rename [options] [--] <headers> [<input>]
    qsv rename --help

rename arguments:
    <headers>              The new headers to use for the CSV.
                           Separate multiple headers with a comma.
                           If "_all_generic" is given, the headers will be renamed
                           to generic column names, where the column name uses
                           the format "_col_N" where N is the 1-based column index.
                           Alternatively, specify pairs of old,new column names
                           to rename only specific columns.
    --pairwise             Invoke pairwise renaming.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the header will be inserted on top.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv replace

```text
Replace occurrences of a pattern across a CSV file.

You can of course match groups using parentheses and use those in
the replacement string. But don't forget to escape your $ in bash by using a
backslash or by wrapping the replacement string into single quotes:

  $ qsv replace 'hel(lo)' 'hal$1' file.csv
  $ qsv replace "hel(lo)" "hal\$1" file.csv

Returns exitcode 0 when replacements are done, returning number of replacements to stderr.
Returns exitcode 1 when no replacements are done, unless the '--not-one' flag is used.

When the CSV is indexed, a faster parallel replace is used.
If there were any replacements, the index will be refreshed.

Examples:

Replace all occurrences of 'hello' with 'world' in the file.csv file.

  $ qsv replace 'hello' 'world' file.csv

Replace all occurrences of 'hello' with 'world' in the file.csv file
and save the output to the file.out file.

  $ qsv replace 'hello' 'world' file.csv -o file.out

Replace all occurrences of 'hello' case insensitive with 'world'
in the file.csv file.

  $ qsv replace 'hello' 'world' file.csv -i

Replace all valid email addresses (using a regex)
with '<EMAIL>' in the file.csv file.

  $ qsv replace '([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})' \
   '<EMAIL>' file.csv


For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_replace.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#replace

Usage:
    qsv replace [options] <pattern> <replacement> [<input>]
    qsv replace --help

replace arguments:
    <pattern>              Regular expression pattern to match. Uses Rust regex syntax.
                           See https://docs.rs/regex/latest/regex/index.html#syntax
                           or https://regex101.com with the Rust flavor for more info.
    <input>                The CSV file to read. If not given, reads from stdin.
    <replacement>          Replacement string. Set to '<NULL>' if you want to
                           replace matches with ''.
replace options:
    -i, --ignore-case      Case insensitive search. This is equivalent to
                           prefixing the regex with '(?i)'.
    --literal              Treat the regex pattern as a literal string. This allows you
                           to search for matches that contain regex special characters.
    --exact                Match the ENTIRE field exactly. Treats the pattern
                           as a literal string (like --literal) and automatically
                           anchors it to match the complete field value (^pattern$).
    -s, --select <arg>     Select the columns to search. See 'qsv select -h'
                           for the full syntax.
    -u, --unicode          Enable unicode support. When enabled, character classes
                           will match all unicode word characters instead of only
                           ASCII word characters. Decreases performance.
    --size-limit <mb>      Set the approximate size limit (MB) of the compiled
                           regular expression. If the compiled expression exceeds this
                           number, then a compilation error is returned.
                           [default: 50]
    --dfa-size-limit <mb>  Set the approximate size of the cache (MB) used by the regular
                           expression engine's Discrete Finite Automata.
                           [default: 10]
    --not-one              Use exit code 0 instead of 1 for no replacement found.
    -j, --jobs <arg>       The number of jobs to run in parallel when the given CSV data has
                           an index. Note that a file handle is opened for each job.
                           When not set, defaults to the number of CPUs detected.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -p, --progressbar      Show progress bars. Not valid for stdin.
    -q, --quiet            Do not print number of replacements to stderr.
```
## qsv reverse

```text
Reverses rows of CSV data.

Useful for cases when there is no column that can be used for sorting in reverse order,
or when keys are not unique and order of rows with the same key needs to be preserved.

Note that if the CSV is not indexed, this operation will require reading all of the
CSV data into memory

See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#reverse

Usage:
    qsv reverse [options] [<input>]
    qsv reverse --help

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. Namely, it will be reversed with the rest
                           of the rows. Otherwise, the first row will always
                           appear as the header row in the output.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
```
## qsv safenames

```text
Modify headers of a CSV to only have "safe" names - guaranteed "database-ready" names
(optimized specifically for PostgreSQL column identifiers).

Fold to lowercase. Trim leading & trailing whitespaces. Replace whitespace/non-alphanumeric
characters with _. If name starts with a number & check_first_char is true, prepend the unsafe prefix.
If a header with the same name already exists, append a sequence suffix (e.g. col, col_2, col_3).
Names are limited to 60 bytes in length (snapped to UTF-8 char boundary, including any
duplicate-disambiguation suffix). Empty names are replaced with the unsafe prefix.

In addition, specifically because of CKAN Datastore requirements:
- Headers with leading underscores are replaced with "unsafe_" prefix.
- Headers that are named "_id" are renamed to "reserved__id".

These CKAN Datastore options can be configured via the --prefix & --reserved options, respectively.

In Always (a) and Conditional (c) mode, returns number of modified headers to stderr,
and sends CSV with safe headers output to stdout.

In Verify (v) mode, returns number of unsafe headers to stderr.
In Verbose (V) mode, returns number of headers; duplicate count and unsafe & safe headers to stderr.
No stdout output is generated in Verify and Verbose mode.

In JSON (j) mode, returns Verbose mode info in minified JSON to stdout.
In Pretty JSON (J) mode, returns Verbose mode info in pretty printed JSON to stdout.

Given data.csv:
 c1,12_col,Col with Embedded Spaces,,Column!@Invalid+Chars,c1
 1,a2,a3,a4,a5,a6

  $ qsv safenames data.csv
  c1,unsafe_12_col,col_with_embedded_spaces,unsafe_,column__invalid_chars,c1_2
  1,a2,a3,a4,a5,a6
  stderr: 5

  Conditionally rename headers, allowing "quoted identifiers":
  $ qsv safenames --mode c data.csv
  c1,unsafe_12_col,Col with Embedded Spaces,unsafe_,column__invalid_chars,c1_2
  1,a2,a3,a4,a5,a6
  stderr: 4

  Verify how many "unsafe" headers are found:
  $ qsv safenames --mode v data.csv
  stderr: 4

  Verbose mode:
  $ qsv safenames --mode V data.csv
  stderr: 6 header/s
  1 duplicate/s: "c1:2"
  4 unsafe header/s: ["12_col", "Col with Embedded Spaces", "", "Column!@Invalid+Chars"]
  1 safe header/s: ["c1"]

  "Safer" (s) mode - like always, but collapses runs of non-alphanumeric
  characters into a single _ (note "column_invalid_chars", not "column__invalid_chars"):
  $ qsv safenames --mode s data.csv
  c1,unsafe_12_col,col_with_embedded_spaces,unsafe_,column_invalid_chars,c1_2
  1,a2,a3,a4,a5,a6
  stderr: 5

  "Safer" with unicode (S) mode - same as s, but preserves unicode letters & numbers.
  Given a header "Café #5", "--mode S" yields "café_5", whereas the ASCII
  "--mode s" strips the accent, yielding "caf_5":
  $ qsv safenames --mode S data.csv

  The --collapse & --unicode flags can be combined with ANY mode, including the
  verify & JSON modes, so the report reflects the "safer" rewrite:
  $ qsv safenames --mode j --collapse --unicode data.csv

Note that even if "Col with Embedded Spaces" is technically safe, it is generally discouraged.
Though it can be created as a "quoted identifier" in PostgreSQL, it is still marked "unsafe"
by default, unless mode is set to "conditional."

It is discouraged because the embedded spaces can cause problems later on.
(see https://lerner.co.il/2013/11/30/quoting-postgresql/ for more info).

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_safenames.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#safenames

Usage:
    qsv safenames [options] [<input>]
    qsv safenames --help

safenames options:
    --mode <mode>          Rename header names to "safe" names — guaranteed
                           "database-ready" names. Mode is selected by the FIRST
                           character: c/C conditional, a/A always, s safer,
                           S Safer (unicode), v verify, V Verbose, j JSON,
                           J pretty JSON (case matters for s vs S, v vs V and
                           j vs J; --mode verbose maps to 'v', NOT V).
                           Mode details:
                             c, C  - conditional. Check first before renaming;
                                     preserves "quoted identifiers" (mixed case
                                     with embedded spaces).
                             a, A  - always. Rename every header, even safe ones.
                             s     - safer. Like always, but collapses runs of
                                     non-alphanumeric characters into a single _
                                     (ASCII-only). Same as always + collapse.
                             S     - Safer (unicode). Like s, but preserves
                                     unicode letters & numbers instead of
                                     stripping to ASCII. Same as always +
                                     collapse + unicode.
                             v     - verify. Count unsafe headers; result to stderr.
                             V     - Verbose. Like verify, but also lists header
                                     count, duplicates, unsafe & safe headers.
                             j     - JSON. Verbose data as minified JSON to stdout.
                             J     - Pretty JSON. Verbose data as pretty-printed JSON.
                           Quoted identifiers are only treated as safe in
                           conditional mode; verify, Verbose, and the JSON modes
                           flag them as unsafe.
                           [default: Always]
    --reserved <list>      Comma-delimited list of additional case-insensitive reserved names
                           that should be considered "unsafe." If a header name is found in
                           the reserved list, it will be prefixed with "reserved_".
                           [default: _id]
    --prefix <string>      Certain systems do not allow header names to start with "_" (e.g. CKAN Datastore).
                           This option allows the specification of the unsafe prefix to use when a header
                           starts with "_". [default: unsafe_]
    --collapse             Collapse consecutive runs of non-alphanumeric characters into a
                           single _. Composes with ALL modes (including verify & JSON modes).
                           Implied by --mode s and --mode S.
    --unicode              Preserve unicode letters & numbers instead of stripping to ASCII.
                           Composes with ALL modes (including verify & JSON modes).
                           Implied by --mode S.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
                           Note that no output is generated for Verify and
                           Verbose modes.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv sample

```text
Randomly samples CSV data.

It supports ten sampling methods:
* RESERVOIR: the default sampling method when NO INDEX is present and no sampling method
  is specified. Visits every CSV record exactly once, using MEMORY PROPORTIONAL to the
  sample size (k) - O(k).
  https://en.wikipedia.org/wiki/Reservoir_sampling

* INDEXED: the default sampling method when an INDEX is present and no sampling method
  is specified. Uses random I/O to sample efficiently, as it only visits records selected
  by random indexing, using MEMORY PROPORTIONAL to the sample size (k) - O(k).
  https://en.wikipedia.org/wiki/Random_access

* BERNOULLI: the sampling method when the --bernoulli option is specified.
  Each record has an independent probability p of being selected, where p is
  specified by the <sample-size> argument. For example, if p=0.1, then each record
  has a 10% chance of being selected, regardless of the other records. The final
  sample size is random and follows a binomial distribution. Uses CONSTANT MEMORY - O(1).
  When sampling from a remote URL, processes the file in chunks without downloading it
  entirely, making it especially efficient for sampling large remote files.
  https://en.wikipedia.org/wiki/Bernoulli_sampling

* SYSTEMATIC: the sampling method when the --systematic option is specified.
  Selects every nth record from the input, where n is the integer part of <sample-size>
  and the fraction part is the percentage of the population to sample.
  For example, if <sample-size> is 10.5, it will select every 10th record and 50% of the
  population. If <sample-size> is a whole number (no fractional part), it will select
  every nth record for the whole population. Uses CONSTANT memory - O(1). The starting
  point can be specified as "random" or "first". Useful for time series data or when you
  want evenly spaced samples.
  https://en.wikipedia.org/wiki/Systematic_sampling

* STRATIFIED: the sampling method when the --stratified option is specified.
  Stratifies the population by the specified column and then samples from each stratum.
  Particularly useful when a population has distinct subgroups (strata) that are
  heterogeneous within but homogeneous between in terms of the variable of interest.
  For example, if you want to sample 1,000 records from a population of 100,000 across the US,
  you can stratify the population by US state and then sample 20 records from each stratum.
  This will ensure that you have a representative sample from each of the 50 states.
  The sample size must be a whole number. Uses MEMORY PROPORTIONAL to the
  number of strata (s) and samples per stratum (k) as specified by <sample-size> - O(s*k).
  https://en.wikipedia.org/wiki/Stratified_sampling

* WEIGHTED: the sampling method when the --weighted option is specified.
  Samples records with probabilities proportional to values in a specified weight column.
  Records with higher weights are more likely to be selected. For example, if you have
  sales data and want to sample transactions weighted by revenue, high-value transactions
  will have a higher chance of being included. Non-numeric weights are treated as zero.
  The weights are automatically normalized using the maximum weight in the dataset.
  Specify the desired sample size with <sample-size>. Uses MEMORY PROPORTIONAL to the
  sample size (k) - O(k).
  "Weighted random sampling with a reservoir" https://doi.org/10.1016/j.ipl.2005.11.003

* VAROPT: the sampling method when the --varopt option is specified.
  Variance-bounded weighted reservoir sampling using the A-ExpJ keying scheme of
  Efraimidis and Spirakis (2006). For each record, computes a key u^(1/w) and
  retains the <sample-size> items with the largest keys. Unlike the --weighted
  method, it does NOT require a stats cache, runs in a single pass, and supports
  merge across partitions through the --sketch-out and --sketch-in options.
  Suitable for heavy-tailed weight distributions where bounded-variance
  estimators are needed. Uses MEMORY PROPORTIONAL to the sample size (k) - O(k).
  This is a native Rust implementation written from the original paper; the
  analogous VarOpt sketches in the Apache DataSketches library use the same
  family of algorithms but are NOT used here.
  Algorithm: "Weighted random sampling with a reservoir"
  doi 10.1016/j.ipl.2005.11.003

* MERGEABLE-RESERVOIR: the sampling method when the --mergeable-reservoir flag is set.
  Uniform reservoir sample using Vitter's Algorithm R. Same statistical
  distribution as the default RESERVOIR method, but the sampler state is
  mergeable: a sketch written by one run can be combined with sketches from
  other runs via the --sketch-out and --sketch-in options, producing a uniform
  sample of the combined stream WITHOUT re-reading the input files. Useful
  for sharded or incremental sampling pipelines. Uses MEMORY PROPORTIONAL to
  the sample size (k) - O(k). Native Rust implementation; the analogous
  ReservoirItemsSketch in the Apache DataSketches library implements the same
  algorithm but is NOT used here.
  See en.wikipedia.org/wiki/Reservoir_sampling

* CLUSTER: the sampling method when the --cluster option is specified.
  Samples entire groups of records together based on a cluster identifier column.
  The number of clusters is specified by the <sample-size> argument.
  Useful when records are naturally grouped (e.g., by household, neighborhood, etc.).
  For example, if you have records grouped by neighborhood and specify a sample size of 10,
  it will randomly select 10 neighborhoods and include ALL records from those neighborhoods
  in the output. This ensures that natural groupings in the data are preserved.
  Uses MEMORY PROPORTIONAL to the number of clusters (c) - O(c).
  https://en.wikipedia.org/wiki/Cluster_sampling

* TIMESERIES: the sampling method when the --timeseries option is specified.
  Samples records based on time intervals from a time-series dataset. Groups records by
  time windows (e.g., hourly, daily, weekly) and selects one record per interval.
  Supports adaptive sampling (e.g., prefer business hours or weekends) and aggregation
  (e.g., mean, sum, min, max) within each interval. The starting point can be "first"
  (earliest), "last" (most recent), or "random". Particularly useful for time-series data
  where simple row-based sampling would always return the same records due to sorting.
  Uses MEMORY PROPORTIONAL to the number of records - O(n).

Supports sampling from CSVs on remote URLs. Note that the entire file is downloaded first
to a temporary file before sampling begins for all sampling methods except Bernoulli, which
streams the file as it samples it, stopping when the desired sample size is reached or the
end of the file is reached.

Sampling from stdin is also supported for all sampling methods, copying stdin to a in-memory
buffer first before sampling begins.

If a stats cache is available, it will be used to do extra checks on systematic,
weighted and cluster sampling, and to speed up sampling in general.

This command is intended to provide a means to sample from a CSV data set that
is too big to fit into memory (for example, for use with commands like
'qsv stats' with the '--everything' option).

Examples:

  # Take a sample of 1000 records from data.csv using RESERVOIR or INDEXED sampling
  # depending on whether an INDEX is present.
  qsv sample 1000 data.csv

  # Take a sample of approximately 10% of the records from data.csv using RESERVOIR
  # or INDEXED sampling depending on whether an INDEX is present.
  qsv sample 0.1 data.csv

  # Take a sample using BERNOULLI sampling where each record has a 5% chance of being selected
  qsv sample --bernoulli 0.05 data.csv

  # Take a sample using SYSTEMATIC sampling where every 10th record is selected
  # and approximately 50% of the population is sampled, starting from a random point.
  qsv sample --systematic random 10.5 data.csv

  # Take a sample using STRATIFIED sampling where 20 records are sampled from each
  # stratum defined by the 'State' column.
  qsv sample --stratified State 20 data.csv

  # Take a sample using WEIGHTED sampling where records are sampled with probabilities
  # proportional to the 'Revenue' column, for a total sample size of 1000 records.
  qsv sample --weighted Revenue 1000 data.csv

  # Take a sample using CLUSTER sampling where 10 clusters defined by the
  # 'Neighborhood' column are randomly selected and all records from those clusters
  # are included in the sample.
  qsv sample --cluster Neighborhood 10 data.csv

  # Take a sample using VAROPT (A-ExpJ weighted reservoir) sampling, weighted by
  # the 'Revenue' column, for a sample size of 1000 records. Unlike --weighted,
  # this does NOT require a stats cache.
  qsv sample --varopt Revenue 1000 data.csv

  # Sample two shards and merge their sketches into a single uniform sample
  # without re-reading the inputs.
  qsv sample --mergeable-reservoir --sketch-out a.sk 1000 shard_a.csv
  qsv sample --mergeable-reservoir --sketch-out b.sk 1000 shard_b.csv
  qsv sample --sketch-in a.sk,b.sk 1000 -o merged.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_sample.rs.
See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#sample

Usage:
    qsv sample [options] <sample-size> [<input>]
    qsv sample --help

sample arguments:
    <input>                The CSV file to sample. This can be a local file,
                           stdin, or a URL (http and https schemes supported).

    <sample-size>          When using INDEXED, RESERVOIR or WEIGHTED sampling, the sample size.
                             Can either be a whole number or a value between value between 0 and 1.
                             If a fraction, specifies the sample size as a percentage of the population.
                             (e.g. 0.15 - 15 percent of the CSV)
                           When using BERNOULLI sampling, the probability of selecting each record
                             (between 0 and 1).
                           When using SYSTEMATIC sampling, the integer part is the interval between
                             records to sample & the fractional part is the percentage of the
                             population to sample. When there is no fractional part, it will
                             select every nth record for the entire population.
                           When using STRATIFIED sampling, the stratum sample size.
                           When using CLUSTER sampling, the number of clusters.
                           When using TIMESERIES sampling, the interval number (treated as hours
                             by default, e.g., 1 = 1 hour). Use --ts-interval for custom intervals
                             like "1d" (daily), "1w" (weekly), "1m" (monthly), "1y" (yearly), etc.

sample options:
    --seed <number>        Random Number Generator (RNG) seed.
    --rng <kind>           The Random Number Generator (RNG) algorithm to use.
                           Three RNGs are supported:
                            * standard: Use the standard RNG.
                              1.5 GB/s throughput.
                            * faster: Use faster RNG using the Xoshiro256Plus algorithm.
                              8 GB/s throughput.
                            * cryptosecure: Use cryptographically secure HC128 algorithm.
                              Recommended by eSTREAM (https://www.ecrypt.eu.org/stream/).
                              2.1 GB/s throughput though slow initialization.
                           [default: standard]

                           SAMPLING METHODS:
    --bernoulli            Use Bernoulli sampling instead of indexed or reservoir sampling.
                           When this flag is set, <sample-size> must be between
                           0 and 1 and represents the probability of selecting each record.
    --systematic <arg>     Use systematic sampling (every nth record as specified by <sample-size>).
                           If <arg> is "random", the starting point is randomly chosen between 0 & n.
                           If <arg> is "first", the starting point is the first record.
                           The sample size must be a whole number. Uses CONSTANT memory - O(1).
    --stratified <col>     Use stratified sampling. The strata column is specified by <col>.
                           Can be either a column name or 0-based column index.
                           The sample size must be a whole number. Uses MEMORY PROPORTIONAL to the
                           number of strata (s) and samples per stratum (k) - O(s*k).
    --weighted <col>       Use weighted sampling. The weight column is specified by <col>.
                           Can be either a column name or 0-based column index.
                           The column will be parsed as a number. Records with non-number weights
                           will be skipped.
                           Uses MEMORY PROPORTIONAL to the sample size (k) - O(k).
    --varopt <col>         Use VAROPT weighted reservoir sampling (A-ExpJ keying).
                           The weight column is specified by <col> (column name or 0-based index).
                           Variance-bounded, single-pass, no stats-cache required, mergeable
                           via --sketch-out / --sketch-in. Records with non-positive or
                           non-numeric weights are silently skipped.
                           Uses MEMORY PROPORTIONAL to the sample size (k) - O(k).
    --mergeable-reservoir  Use a mergeable Algorithm-R reservoir sampler. Distribution is
                           identical to the default RESERVOIR method, but the resulting sketch
                           is mergeable via --sketch-out / --sketch-in. Cannot be combined
                           with another sampling-method flag.
    --cluster <col>        Use cluster sampling. The cluster column is specified by <col>.
                           Can be either a column name or 0-based column index.
                           Uses MEMORY PROPORTIONAL to the number of clusters (c) - O(c).
    --timeseries <col>     Use time-series sampling. The time column is specified by <col>.
                           Can be either a column name or 0-based column index.
                           Sorts records by the specified time column and then groups by time intervals
                           and selects one record per interval.
                           Supports various date formats (19 formats recognized by qsv-dateparser).
                           Uses MEMORY PROPORTIONAL to the number of records - O(n).

                           TIME-SERIES SAMPLING OPTIONS:
    --ts-interval <intvl>  Time interval for grouping records. Format: <number><unit>
                           where unit is h (hour), d (day), w (week), m (month), y (year).
                           Examples: "1h", "1d", "1w", "2d" (every 2 days).
                           If not specified, <sample-size> is treated as hours.
    --ts-start <mode>      Starting point for time-series sampling.
                           Options: "first" (earliest timestamp, default), "last" (most recent timestamp),
                           "random" (random starting point).
                           [default: first]
    --ts-adaptive <mode>   Adaptive sampling mode for time-series data.
                           Options: "business-hours" (prefer 9am-5pm Mon-Fri),
                           "weekends" (prefer weekends), "business-days" (prefer weekdays),
                           "both" (combine business-hours and weekends).
    --ts-aggregate <func>  Aggregation function to apply within each time interval.
                           Options: "first", "last", "mean", "sum", "count", "min", "max", "median".
                           When specified, aggregates all records in each interval instead of selecting a single record.
    --ts-input-tz <tz>     Timezone for parsing input timestamps. Can be an IANA timezone name or "local" for the local timezone.
                           [default: UTC]
    --ts-prefer-dmy        Prefer to parse dates in dmy format. Otherwise, use mdy format.

                           SKETCH OPTIONS:
    --sketch-out <file>    After sampling, also write a binary sketch describing the internal
                           sampler state to <file>. The blob can later be merged into another
                           run via --sketch-in. Only valid with --varopt or --mergeable-reservoir.
                           The format is qsv-specific and is not interoperable with serialized
                           sketches from other tools.
    --sketch-in <files>    Comma-separated list of sketch files produced by --sketch-out.
                           CSV input is NOT read; the listed sketches (which must all be of
                           the same sampler kind) are merged and the resulting sample is
                           emitted as CSV. <sample-size> may be used to cap the merged sample
                           below the sketches' own k.

                           REMOTE FILE OPTIONS:
    --user-agent <agent>   Specify custom user agent to use when the input is a URL.
                           It supports the following variables -
                           $QSV_VERSION, $QSV_TARGET, $QSV_BIN_NAME, $QSV_KIND and $QSV_COMMAND.
                           Try to follow the syntax here -
                           https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
    --timeout <secs>       Inactivity timeout for downloading URLs in seconds. Aborts only if
                           no data is received from the server for this long. If 0, no timeout.
                           [default: 30]
    --max-size <mb>        Maximum size of the file to download in MB before sampling.
                           Will download the entire file if not specified.
                           If the CSV is partially downloaded, the sample will be taken
                           only from the downloaded portion.
    --force                Do not use stats cache, even if its available.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will be considered as part of
                           the population to sample from. (When not set, the
                           first row is the header row and will always appear
                           in the output.)
    -d, --delimiter <arg>  The field delimiter for reading/writing CSV data.
                           Must be a single character. (default: ,)
```
## qsv schema

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
## qsv search

```text
Filters CSV data by whether the given regex matches a row.

The regex is applied to selected field in each row, and if any field matches,
then the row is written to the output, and the number of matches to stderr.

The columns to search can be limited with the '--select' flag (but the full row
is still written to the output if there is a match).

Returns exitcode 0 when matches are found.
Returns exitcode 1 when no match is found, unless the '--not-one' flag is used.
Use --count to also write the number of matches to stderr (suppressed by --quiet and --json).

When --quick is enabled, no output is produced and exitcode 0 is returned on
the first match.

When the CSV is indexed, a faster parallel search is used.

Examples:

  # Search for rows where any field contains the regex 'foo.*bar' (case sensitive)
  qsv search 'foo.*bar' data.csv

  # Case insensitive search for 'error' in the 'message' column
  qsv search -i 'error' -s message data.csv

  # Search for exact matches of 'completed' in the 'status' column
  qsv search --exact 'completed' -s status data.csv

  # Search for literal string 'a.b*c' in all columns
  qsv search --literal 'a.b*c' data.csv

  # Invert match: select rows that do NOT match the regex 'test'
  qsv search --invert-match 'test' data.csv

  # Flag matched rows in a new column named 'match_flag'
  qsv search --flag match_flag 'pattern' data.csv

  # Quick search: return on first match of 'urgent' in the 'subject' column
  qsv search --quick 'urgent' -s subject data.csv

  # Preview the first 5 matches of 'warning' in all columns
  qsv search --preview-match 5 'warning' data.csv

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_search.rs.
See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#search

Usage:
    qsv search [options] <regex> [<input>]
    qsv search --help

search arguments:
    <regex>                Regular expression to match. Uses Rust regex syntax.
                           See https://docs.rs/regex/latest/regex/index.html#syntax
                           or https://regex101.com with the Rust flavor for more info.
    <input>                The CSV file to read. If not given, reads from stdin.

search options:
    -i, --ignore-case      Case insensitive search. This is equivalent to
                           prefixing the regex with '(?i)'.
    --literal              Treat the regex as a literal string. This allows you to
                           search for matches that contain regex special characters.
    --exact                Match the ENTIRE field exactly. Treats the pattern
                           as a literal string (like --literal) and automatically
                           anchors it to match the complete field value (^pattern$).
    -s, --select <arg>     Select the columns to search. See 'qsv select -h'
                           for the full syntax.
    -v, --invert-match     Select only rows that did not match
    -u, --unicode          Enable unicode support. When enabled, character classes
                           will match all unicode word characters instead of only
                           ASCII word characters. Decreases performance.
    -f, --flag <column>    If given, the command will not filter rows
                           but will instead flag every row in a new column
                           named <column>, set to the row number for matched
                           rows and "0" for non-matched rows.
                           SPECIAL: if <column> is exactly "M", only matched
                           rows are returned AND only the M column is written
                           (all other columns are dropped). To use a literal
                           column name "M" without this behavior, rename it
                           afterward (e.g., with `qsv rename`).
    -Q, --quick            Return on first match with an exitcode of 0, returning
                           the row number of the first match to stderr.
                           Return exit code 1 if no match is found.
                           No output is produced.
    --preview-match <arg>  Preview the first N matches OR all matches found
                           within N milliseconds, whichever occurs first.
                           NOTE: the same numeric value is used for BOTH the
                           match count AND the millisecond timeout - choose a
                           value where one bound effectively dominates (e.g.,
                           a small count for "first N" preview, or a large
                           count for "all within N ms").
                           Returns the preview to stderr; output is still
                           written to stdout or --output as usual.
                           Forces a sequential search, even if the CSV is indexed.
    -c, --count            Write the number of matches to stderr.
                           Suppressed by --quiet and --json.
    --size-limit <mb>      Set the approximate size limit (MB) of the compiled
                           regular expression. If the compiled expression exceeds this
                           number, then a compilation error is returned.
                           Modify this only if you're getting regular expression
                           compilation errors. [default: 50]
    --dfa-size-limit <mb>  Set the approximate size of the cache (MB) used by the regular
                           expression engine's Discrete Finite Automata.
                           Modify this only if you're getting regular expression
                           compilation errors. [default: 10]
    --json                 Output the result as JSON. Fields are written
                           as key-value pairs. The key is the column name.
                           The value is the field value. The output is a
                           JSON array. If --no-headers is set, then
                           the keys are the column indices (zero-based).
                           Automatically sets --quiet (also suppresses --count).
    --not-one              Use exit code 0 instead of 1 for no match found.
    -j, --jobs <arg>       The number of jobs to run in parallel when the given CSV data has
                           an index. Note that a file handle is opened for each job.
                           When not set, defaults to the number of CPUs detected.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -p, --progressbar      Show progress bars. Not valid for stdin.
                           Disabled when running parallel search (i.e., when
                           the CSV is indexed and --jobs > 1). Sequential
                           search on an indexed CSV (--jobs 1) still shows
                           the progress bar.
    -q, --quiet            Do not write the match count (--count) or the
                           first match row number reported by --quick to stderr.
```
## qsv searchset

```text
Filters CSV data by whether the given regex set matches a row.

Unlike the search operation, this allows regex matching of multiple regexes
in a single pass.

The regexset-file is a plain text file with multiple regexes, with a regex on
each line. Lines starting with '#' (optionally preceded by whitespace) are
treated as comments and ignored. For an example scanning for common Personally Identifiable Information (PII) -
SSN, credit cards, email, bank account numbers & phones, see
https://github.com/dathere/qsv/blob/master/resources/examples/searchset/pii_regexes.txt

The regex set is applied to each field in each row, and if any field matches,
then the row is written to the output, and the number of matches to stderr.

The columns to search can be limited with the '--select' flag (but the full row
is still written to the output if there is a match).

Returns exitcode 0 when matches are found.
Returns exitcode 1 when no match is found, unless the '--not-one' flag is used.
Use --count to also write the number of matches to stderr (suppressed by --quiet).
With --json, a JSON summary is always written to stderr instead.

When --quick is enabled, no output is produced and exitcode 0 is returned on
the first match.

When the CSV is indexed, a faster parallel search is used.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_searchset.rs.
See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#searchset

Usage:
    qsv searchset [options] (<regexset-file>) [<input>]
    qsv searchset --help

searchset arguments:
    <regexset-file>            The file containing regular expressions to match, with a
                               regular expression on each line.
                               See https://docs.rs/regex/latest/regex/index.html#syntax
                               or https://regex101.com with the Rust flavor for regex syntax.
    <input>                    The CSV file to read. If not given, reads from stdin.

searchset options:
    -i, --ignore-case          Case insensitive search. This is equivalent to
                               prefixing the regex with '(?i)'.
    --literal                  Treat the regex as a literal string. This allows you to
                               search for matches that contain regex special characters.
    --exact                    Match the ENTIRE field exactly. Treats the pattern
                               as a literal string (like --literal) and automatically
                               anchors it to match the complete field value (^pattern$).
    -s, --select <arg>         Select the columns to search. See 'qsv select -h'
                               for the full syntax.
    -v, --invert-match         Select only rows that did not match
    -u, --unicode              Enable unicode support. When enabled, character classes
                               will match all unicode word characters instead of only
                               ASCII word characters. Decreases performance.

    -f, --flag <column>        If given, the command will not filter rows
                               but will instead flag the found rows in a new
                               column named <column>. For each found row, <column>
                               is set to the row number of the row, followed by a
                               semicolon, then a list of the matching regexes.
    --flag-matches-only        When --flag is enabled, only rows that match are
                               sent to output. Rows that do not match are filtered.
    --unmatched-output <file>  When --flag-matches-only is enabled, output the rows
                               that did not match to <file>.

    -Q, --quick                Return on first match with an exitcode of 0, returning
                               the row number of the first match to stderr.
                               Return exit code 1 if no match is found.
                               No output is produced. Ignored if --json is enabled.
    -c, --count                Write the number of matches to stderr.
                               Suppressed by --quiet. Ignored if --json is enabled.
    -j, --json                 Return number of matches, number of rows with matches,
                               and number of rows to stderr in JSON format.
    --size-limit <mb>          Set the approximate size limit (MB) of the compiled
                               regular expression. If the compiled expression exceeds this
                               number, then a compilation error is returned.
                               Modify this only if you're getting regular expression
                               compilation errors. [default: 50]
    --dfa-size-limit <mb>      Set the approximate size of the cache (MB) used by the regular
                               expression engine's Discrete Finite Automata.
                               Modify this only if you're getting regular expression
                               compilation errors. [default: 10]
    --not-one                  Use exit code 0 instead of 1 for no match found.
    --jobs <arg>               The number of jobs to run in parallel when the given CSV data has
                               an index. Note that a file handle is opened for each job.
                               When not set, defaults to the number of CPUs detected.

Common options:
    -h, --help                 Display this message
    -o, --output <file>        Write output to <file> instead of stdout.
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. (i.e., They are not searched, analyzed,
                               sliced, etc.)
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character. (default: ,)
    -p, --progressbar          Show progress bars. Not valid for stdin.
    -q, --quiet                Do not write the match count (--count) or the
                               first match row number reported by --quick to stderr.
                               Does not suppress the --json summary.
```
## qsv select

```text
Select columns from CSV data efficiently.

This command lets you manipulate the columns in CSV data. You can re-order,
duplicate, reverse or drop them. Columns can be referenced by index or by
name if there is a header row (duplicate column names can be disambiguated with
more indexing). Column ranges can also be specified. Finally, columns can be
selected using regular expressions.

Examples:

  # Select the first and fourth columns
  qsv select 1,4

  # Select the first 4 columns (by index)
  qsv select 1-4

  # Select the first 4 columns (by name)
  qsv select Header1-Header4

  # Ignore the first 2 columns (by range)
  qsv select 3-

  # Ignore the first 2 columns (by index)
  qsv select '!1-2'

  # Select the third column named 'Foo':
  qsv select 'Foo[2]'

  # Select the first and last columns, _ is a special character for the last column:
  qsv select 1,_

  # Reverse the order of columns:
  qsv select _-1

  # select columns starting with 'a' (regex)
  qsv select /^a/

  # select columns with a digit (regex)
  qsv select '/^.*\d.*$/'

  # remove SSN, account_no and password columns (regex)
  qsv select '!/SSN|account_no|password/'

  # Sort the columns lexicographically (i.e. by their byte values)
  qsv select 1- --sort

  # Select some columns and then sort them
  qsv select 1,4,5-7 --sort

  # Randomly shuffle the columns:
  qsv select 1- --random

  # Randomly shuffle the columns with a seed
  qsv select 1- --random --seed 42

  # Select some columns and then shuffle them with a seed:
  qsv select 1,4,5-7 --random --seed 42

  # Re-order and duplicate columns arbitrarily using different types of selectors
  qsv select 3-1,Header3-Header1,Header1,Foo[2],Header1

  # Quote column names that conflict with selector syntax:
  qsv select '\"Date - Opening\",\"Date - Actual Closing\"'

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_select.rs.
See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#select

Usage:
    qsv select [options] [--] <selection> [<input>]
    qsv select --help

select arguments:
    <selection>            The columns to select.
                           You can select columns by index, by name, by range, by regex and
                           any combination of these. If the first character is '!', the
                           selection will be inverted. If the selection contains embedded
                           spaces or characters that conflict with selector syntax, it must
                           be quoted. See examples above.

select options:
These options only apply to the `select` command, not the `--select` option in other commands.

    -R, --random           Randomly shuffle the columns in the selection.
    --seed <number>        Seed for the random number generator.

    -S, --sort             Sort the selected columns lexicographically,
                           i.e. by their byte values.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv slice

```text
Returns the rows in the range specified (starting at 0, half-open interval).
The range does not include headers.

If the start of the range isn't specified, then the slice starts from the first
record in the CSV data.

If the end of the range isn't specified, then the slice continues to the last
record in the CSV data.

This operation can be made much faster by creating an index with 'qsv index'
first. With an index, the command requires parsing just the rows that are
sliced. Without an index, all rows up to the first row in the slice must be
parsed.

Examples:

  # Slice from the 3rd record to the end
  qsv slice --start 2 data.csv

  # Slice the first three records
  qsv slice --start 0 --end 2 data.csv

  # Slice the first three records (using --len)
  qsv slice --len 3 data.csv

  # Slice the last record
  qsv slice -s -1 data.csv

  # Slice the last 10 records
  qsv slice -s -10 data.csv

  # Get everything except the last 10 records
  qsv slice -s -10 --invert data.csv

  # Slice the first three records of the last 10 records
  qsv slice -s -10 -l 3 data.csv

  # Slice the second record
  qsv slice --index 1 data.csv

  # Slice from the second record, two records
  qsv slice -s 1 --len 2 data.csv

  # Slice records 10 to 19 as JSON (--end is exclusive)
  qsv slice --start 9 --end 19 --json data.csv

  # Slice records 1 to 9 and 20 to the end as JSON
  qsv slice --start 9 --len 10 --invert --json data.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_slice.rs.
See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#slice

Usage:
    qsv slice [options] [<input>]
    qsv slice --help

slice options:
    -s, --start <arg>      The index of the record to slice from.
                           If negative, starts from the last record.
    -e, --end <arg>        The index of the record to slice to.
    -l, --len <arg>        The length of the slice (can be used instead
                           of --end).
    -i, --index <arg>      Slice a single record (shortcut for -s N -l 1).
                           If negative, starts from the last record.
    --json                 Output the result as JSON. Fields are written
                           as key-value pairs. The key is the column name.
                           The value is the field value. The output is a
                           JSON array. If --no-headers is set, then
                           the keys are the column indices (zero-based).
    --invert               slice all records EXCEPT those in the specified range.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. Otherwise, the first row will always
                           appear in the output as the header row.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv snappy

```text
Does streaming compression/decompression of the input using the Snappy framing format.
https://github.com/google/snappy/blob/main/framing_format.txt

It has four subcommands:
    compress:   Compress the input (multithreaded).
    decompress: Decompress the input (single-threaded).
    check:      Quickly check if the input is a Snappy file by inspecting the
                first 50 bytes of the input is valid Snappy data.
                Returns exitcode 0 if the first 50 bytes is valid Snappy data,
                exitcode 1 otherwise.
    validate:   Validate if the ENTIRE input is a valid Snappy file.
                Returns exitcode 0 if valid, exitcode 1 otherwise.

Note that most qsv commands already automatically decompresses Snappy files if the
input file has an ".sz" extension. It will also automatically compress the output
file (though only single-threaded) if the --output file has an ".sz" extension.

This command's multithreaded compression is 5-6x faster than qsv's automatic
single-threaded compression.

Also, this command is not specific to CSV data, it can compress/decompress ANY file.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_snappy.rs.
See also https://github.com/dathere/qsv/wiki/Conversion-and-IO#snappy

Usage:
    qsv snappy compress [options] [<input>]
    qsv snappy decompress [options] [<input>]
    qsv snappy check [options] [<input>]
    qsv snappy validate [options] [<input>]
    qsv snappy --help

snappy arguments:
    <input>               The input file to compress/decompress. This can be a local file, stdin,
                          or a URL (http and https schemes supported).

snappy options:
    --user-agent <agent>  Specify custom user agent to use when the input is a URL.
                          It supports the following variables -
                          $QSV_VERSION, $QSV_TARGET, $QSV_BIN_NAME, $QSV_KIND and $QSV_COMMAND.
                          Try to follow the syntax here -
                          https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
    --timeout <secs>      Timeout for downloading URLs in seconds.
                          [default: 60]

Common options:
    -h, --help            Display this message
    -o, --output <file>   Write output to <output> instead of stdout.
    -j, --jobs <arg>      The number of jobs to run in parallel when compressing.
                          When not set, its set to the number of CPUs - 1
    -q, --quiet           Suppress status messages to stderr.
    -p, --progressbar     Show download progress bars. Only valid for URL input.
```
## qsv sniff

```text
Quickly sniff the first n rows and infer CSV metadata (delimiter, header row, number of
preamble rows, quote character, flexible, is_utf8, average record length, number of records,
content length and estimated number of records if sniffing a URL, file size, number of fields,
field names & data types).

`sniff` is also a mime type detector, returning the detected mime type, file size and
last modified date. If --no-infer is enabled, it doesn't even bother to infer the CSV's schema.
This makes it useful for accelerated CKAN harvesting and for checking stale/broken resource URLs.

When qsv is compiled with the optional `magika` feature, it uses Magika - Google's AI-powered
content detection library to identify file types with high accuracy. Magika detects over
200 content types including CSV, parquet, MS Office/Open Document files, JSON, PDF, PNG, JPEG & more.
See https://opensource.googleblog.com/2025/11/announcing-magika-10-now-faster-smarter.html.

When the `magika` feature is not enabled in a build (e.g., MUSL builds, qsvlite, qsvdp), it falls back
to the file-format library which provides basic MIME type detection.

NOTE: This command "sniffs" a CSV's schema by sampling the first n rows (default: 1000)
of a file. Its inferences are sometimes wrong if the the file is too small to infer a pattern
or if the CSV has unusual formatting - with atypical delimiters, quotes, etc.

In such cases, selectively use the --sample, --delimiter and --quote options to improve
the accuracy of the sniffed schema.

If you want more robust, guaranteed schemata, use the "schema" or "stats" commands
instead as they scan the entire file. However, they only work on local files and well-formed
CSVs, unlike `sniff` which can work with remote files, various CSV dialects and is very fast
regardless of file size.

Examples:

  # Sniff a local CSV file
  qsv sniff data.csv

  # Sniff a remote TSV file over HTTPS
  qsv sniff https://example.com/data.tsv

  # Get the mime type of a remote file without inferring the CSV schema
  qsv sniff --no-infer https://example.com/data.xlsx

  # Sniff the first 20 percent of a SSV file
  qsv sniff --sample 0.20 data.ssv

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_sniff.rs.
See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#sniff

Usage:
    qsv sniff [options] [<input>]
    qsv sniff --help

sniff arguments:
    <input>                  The file to sniff. This can be a local file, stdin or a
                             URL (http and https schemes supported).

                             Note that when input is a URL and is a CSV candidate,
                             sniff will automatically download a sample to a temporary
                             file and sniff it.

                             If the file sample is not a CSV, sniff will return as an error
                             - the detected mime type, file size & last modified date.

                             When --no-infer is enabled, sniff will not bother to infer the
                             CSV schema and just work as a general mime type detector -
                             returning the detected mime type, file size and last modified date.

                             When sniffing a local file, it will scan the file to detect the mime type.
                             When sniffing a URL, it will only download the first chunk of the file if
                             the --quick option is enabled, otherwise it will download the entire file.

sniff options:
    --sample <size>          First n rows to sample to sniff out the metadata.
                             When sample size is between 0 and 1 exclusive,
                             it is treated as a percentage of the CSV to sample
                             (e.g. 0.20 is 20 percent).
                             When it is zero, the entire file will be sampled.
                             When the input is a URL, the sample size dictates
                             how many lines to sample without having to
                             download the entire file. Ignored when --no-infer is enabled.
                             When sniffing a local file that has a CSV index, the
                             sample budget is instead drawn as a DISTRIBUTED sample
                             (the first & last 5 rows, 5 rows each around the 25th,
                             50th & 75th percentiles, and the rest random across the
                             whole file) rather than just the first n rows. This
                             improves type/date inference for values that only appear
                             late in the file. Run `qsv index` to create an index.
                             [default: 1000]
    --prefer-dmy             Prefer to parse dates in dmy format. Otherwise, use mdy format.
                             Ignored when --no-infer is enabled.
    -d, --delimiter <arg>    The delimiter for reading CSV data.
                             Specify this when the delimiter is known beforehand,
                             as the delimiter inferencing algorithm can sometimes fail.
                             Must be a single ascii character.
    --quote <arg>            The quote character for reading CSV data.
                             Specify this when the quote character is known beforehand,
                             as the quote char inferencing algorithm can sometimes fail.
                             Must be a single ascii character - typically, double quote ("),
                             single quote ('), or backtick (`).
    --json                   Return results in JSON format.
    --pretty-json            Return results in pretty JSON format.
    --save-urlsample <file>  Save the URL sample to a file.
                             Valid only when input is a URL.
    --timeout <secs>         Timeout when sniffing URLs in seconds. If 0, no timeout is used.
                             [default: 30]
    --user-agent <agent>     Specify custom user agent to use when sniffing a CSV on a URL.
                             It supports the following variables - $QSV_VERSION, $QSV_TARGET,
                             $QSV_BIN_NAME, $QSV_KIND and $QSV_COMMAND. Try to follow the syntax here -
                             https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
    --stats-types            Use the same data type names as `stats`.
                             (Unsigned, Signed => Integer, Text => String, everything else the same)
    --no-infer               Do not infer the schema. Only return the file's mime type, size and
                             last modified date. Use this to use sniff as a general mime type detector.
                             Note that CSV and TSV files will only be detected as mime type plain/text
                             in this mode.
    --just-mime              Only return the file's mime type. Use this to use sniff as a general
                             mime type detector. Synonym for --no-infer.
    -Q, --quick              When sniffing a non-CSV remote file, only download the first chunk of the file
                             before attempting to detect the mime type. This is faster but less accurate as
                             some mime types cannot be detected with just the first downloaded chunk.
    --harvest-mode           This is a convenience flag when using sniff in CKAN harvesters.
                             It is equivalent to --quick --timeout 10 --stats-types --json
                             and --user-agent "CKAN-harvest/$QSV_VERSION ($QSV_TARGET; $QSV_BIN_NAME)"

Common options:
    -h, --help               Display this message
    -p, --progressbar        Show progress bars. Only valid for URL input.
```
## qsv sort

```text
Sorts CSV data in lexicographical, natural, numerical, reverse, unique or random order.

Note that this requires reading all of the CSV data into memory. If
you need to sort a large file that may not fit into memory, use the
extsort command instead.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_sort.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#sort

Usage:
    qsv sort [options] [<input>]
    qsv sort --help

sort options:
    -s, --select <arg>      Select a subset of columns to sort.
                            See 'qsv select --help' for the format details.
    -N, --numeric           Compare according to string numerical value
    --natural               Compare strings using natural sort order
                            (treats numbers within strings as actual numbers, e.g.
                            "data1.txt", "data2.txt", "data10.txt", as opposed to
                            "data1.txt", "data10.txt", "data2.txt" when sorting
                            lexicographically)
                            https://en.wikipedia.org/wiki/Natural_sort_order
                            When combined with --numeric, --natural takes precedence.
    -R, --reverse           Reverse order
    -i, --ignore-case       Compare strings disregarding case.
                            Has no effect when numeric comparison is selected
                            (i.e. when --numeric is used without --natural).
    -u, --unique            When set, identical consecutive lines will be dropped
                            to keep only one line per sorted value. The same
                            comparison mode used to sort the input is also used
                            here, so unique-equality always agrees with the sort.

                            RANDOM SORTING OPTIONS:
    --random                Randomize (scramble) the data by row.
                            When set, the numeric, natural, and
                            ignore-case comparison flags still apply
                            to unique-filtering (if --unique is also
                            set). The reverse flag has no effect on
                            unique-filter equality and is ignored for
                            the shuffle itself.
    --seed <number>         Random Number Generator (RNG) seed to use if --random is set
    --rng <kind>            The RNG algorithm to use if --random is set.
                            Three RNGs are supported:
                            * standard: Use the standard RNG.
                              1.5 GB/s throughput.
                            * faster: Use faster RNG using the Xoshiro256Plus algorithm.
                              8 GB/s throughput.
                            * cryptosecure: Use cryptographically secure HC128 algorithm.
                              Recommended by eSTREAM (https://www.ecrypt.eu.org/stream/).
                              2.1 GB/s throughput though slow initialization.
                            [default: standard]


    -j, --jobs <arg>        The number of jobs to run in parallel.
                            When not set, the number of jobs is set to the
                            number of CPUs detected.
    --faster                When set, the sort will be faster. This is done by
                            using a faster sorting algorithm that is not "stable"
                            (i.e. the order of identical values is not guaranteed
                            to be preserved). It has the added side benefit that the
                            sort will also be in-place (i.e. does not allocate),
                            which is useful for sorting large files that will
                            otherwise NOT fit in memory using the default allocating
                            stable sort.

Common options:
    -h, --help              Display this message
    -o, --output <file>     Write output to <file> instead of stdout.
    -n, --no-headers        When set, the first row will not be interpreted
                            as headers. Namely, it will be sorted with the rest
                            of the rows. Otherwise, the first row will always
                            appear as the header row in the output.
    -d, --delimiter <arg>   The field delimiter for reading CSV data.
                            Must be a single character. (default: ,)
    --memcheck              Check if there is enough memory to load the entire
                            CSV into memory using CONSERVATIVE heuristics.
                            Ignored if --random or --faster is set.
```
## qsv sortcheck

```text
Check if a CSV is sorted. The check is done on a streaming basis (i.e. constant memory).
With the --json options, also retrieve record count, sort breaks & duplicate count.

This command can be used in tandem with other qsv commands that sort or require sorted data
to ensure that they also work on a stream of data - i.e. without loading an entire CSV into memory.

For instance, a naive `dedup` requires loading the entire CSV into memory to sort it
first before deduping. However, if you know a CSV is sorted beforehand, you can invoke
`dedup` with the --sorted option, and it will skip loading entire CSV into memory to sort
it first. It will just immediately dedupe on a streaming basis.

`sort` also requires loading the entire CSV into memory. For very large CSV files that will
not fit in memory, `extsort` - a multi-threaded streaming sort that can work with arbitrarily
large files - can be used instead.

Use --numeric or --natural to verify the file matches the order produced by `sort --numeric`
or `sort --natural` before piping into a downstream command (e.g. `dedup --numeric --sorted`).
When multiple comparison flags are set, --natural takes precedence over --numeric, which takes
precedence over --ignore-case (matching `sort` and `dedup` semantics).

Simply put, sortcheck allows you to make informed choices on how to compose pipelines that
require sorted data.

STATS-CACHE AWARE: when checking a single column with the default lexicographic or --numeric
comparison and a valid stats cache exists (see `qsv stats --stats-jsonl`), sortcheck answers
"is it sorted?" instantly from the cached sort order instead of scanning the file. This applies
only to the exit-code path; --json/--pretty-json always do a full scan for exact counts.
Disable with QSV_STATSCACHE_MODE=none.

Returns exit code 0 if a CSV is sorted, and exit code 1 otherwise.

Examples:

  # Check if file.csv is lexicographically sorted on all columns:
  qsv sortcheck file.csv

  # Check column "name" only, ignoring case:
  qsv sortcheck --select name --ignore-case file.csv

  # Verify file.csv is sorted numerically before piping into `dedup --numeric --sorted`:
  qsv sortcheck --numeric file.csv && qsv dedup --numeric --sorted file.csv

  # Check natural order (e.g. item1, item2, item10) and emit JSON stats:
  qsv sortcheck --natural --json file.csv

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_sortcheck.rs.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#sortcheck

Usage:
    qsv sortcheck [options] [<input>]
    qsv sortcheck --help

sort options:
    -s, --select <arg>      Select a subset of columns to check for sort.
                            See 'qsv select --help' for the format details.
    -N, --numeric           Compare according to string numerical value.
    --natural               Compare using natural sort order (e.g. item1 < item2 < item10).
                            Takes precedence over --numeric. Composes with --ignore-case.
    -i, --ignore-case       Compare strings disregarding case. Ignored under pure
                            numeric comparison (i.e. --numeric without --natural),
                            since numeric comparison is case-insensitive by definition.
    --all                   Check all records. Do not stop/short-circuit the check
                            on the first unsorted record.
    --json                  Return results in JSON format, scanning --all records.
                            The JSON result has the following properties -
                            sorted (boolean), record_count (number),
                            unsorted_breaks (number) & dupe_count (number).
                            Unsorted breaks count the number of times two consecutive
                            rows are unsorted (i.e. n row > n+1 row).
                            Dupe count is the number of times two consecutive
                            rows are equal. Note that dupe count does not apply
                            if the file is not sorted and is set to -1.
    --pretty-json           Same as --json but in pretty JSON format.

Common options:
    -h, --help              Display this message
    -n, --no-headers        When set, the first row will not be interpreted
                            as headers. That is, it will be sorted with the rest
                            of the rows. Otherwise, the first row will always
                            appear as the header row in the output.
    -d, --delimiter <arg>   The field delimiter for reading CSV data.
                            Must be a single character. (default: ,)
    -p, --progressbar       Show progress bars. Not valid for stdin.
```
## qsv split

```text
Splits the given CSV data into chunks. It has three modes: by size (rowcount),
by number of chunks and by kb-size.

See `partition` command for splitting by a column value.

When splitting by size, the CSV data is split into chunks of the given number of
rows. The last chunk may have fewer rows if the number of records is not evenly
divisible by the given rowcount.

When splitting by number of chunks, the CSV data is split into the given number of
chunks. The number of rows in each chunk is determined by the number of records in
the CSV data and the number of desired chunks. If the number of records is not evenly
divisible by the number of chunks, the last chunk will have fewer records.

When splitting by kb-size, the CSV data is split into chunks of the given size in kilobytes.
The number of rows in each chunk may vary, but the size of each chunk will not exceed the
desired size.

Uses multithreading to go faster if the CSV has an index when splitting by size or
by number of chunks. Splitting by kb-size is always done sequentially with a single thread.

The default is to split by size with a chunk size of 500.

The files are written to the directory given with the name '{start}.csv',
where {start} is the index of the first record of the chunk (starting at 0).

Examples:
  # Create files with names like chunk_0.csv, chunk_100.csv, etc.
  # in the directory 'outdir', creating the directory if it does not exist.
  qsv split outdir --size 100 --filename chunk_{}.csv input.csv

  # Create files with names like chunk_00000.csv, chunk_00100.csv, etc.
  # in the directory 'outdir/subdir', creating the directories if they do not exist.
  qsv split outdir/subdir -s 100 --filename chunk_{}.csv --pad 5 input.csv

  # Create files like 0.csv, 100.csv, etc. in the current directory.
  qsv split . -s 100 input.csv

  # Create files with names like 0.csv, 994.csv, etc. in the directory
  # 'outdir', creating the directory if it does not exist. Each file will be close
  # to 1000KB in size.
  qsv split outdir --kb-size 1000 input.csv

  # Read from stdin and create files like 0.csv, 1000.csv, etc. in the directory
  # 'mysplitoutput', creating it if it does not exist.
  cat in.csv | qsv split mysplitoutput -s 1000

  # Split into 10 chunks. Files are named with the zero-based starting row index
  # of each chunk (e.g. 0.csv, N.csv, 2N.csv, ...) in the directory 'outdir'.
  qsv split outdir --chunks 10 input.csv

  # Same, using 4 parallel jobs. Note that the input CSV must have an index.
  qsv split splitoutdir -c 10 -j 4 input.csv

  # This will create files with names like 0.csv, 100.csv, etc. in the directory
  # 'outdir', and then run the command "gzip" on each chunk.
  qsv split outdir -s 100 --filter "gzip $FILE" input.csv

  # WINDOWS: This will create files with names like 0.zip, 100.zip, etc. in the directory
  # 'outdir', and then run the command "Compress-Archive" on each chunk.
  qsv split outdir --filter "powershell Compress-Archive -Path $FILE -Destination {}.zip" input.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_split.rs.
See also https://github.com/dathere/qsv/wiki/Joins-and-Set-Ops#split

Usage:
    qsv split [options] (--size <arg> | --chunks <arg> | --kb-size <arg>) <outdir> [<input>]
    qsv split --help

split arguments:
    <outdir>              The directory where the output files will be written.
                          If it does not exist, it will be created.
    <input>               The CSV file to read. If not given, input is read from
                          STDIN.

split options:
    -s, --size <arg>       The number of records to write into each chunk.
                           [default: 500]
    -c, --chunks <arg>     The number of chunks to split the data into.
                           This option is mutually exclusive with --size.
                           The number of rows in each chunk is determined by
                           the number of records in the CSV data and the number
                           of desired chunks. If the number of records is not evenly
                           divisible by the number of chunks, the last chunk will
                           have fewer records.
    -k, --kb-size <arg>    The size of each chunk in kilobytes. The number of rows
                           in each chunk may vary, but the size of each chunk will
                           not exceed the desired size.
                           This option is mutually exclusive with --size and --chunks.

    -j, --jobs <arg>       The number of splitting jobs to run in parallel.
                           This only works when the given CSV data has
                           an index already created. Note that a file handle
                           is opened for each job.
                           When not set, the number of jobs is set to the
                           number of CPUs detected.
    --filename <filename>  A filename template to use when constructing
                           the names of the output files.  The string '{}'
                           will be replaced by the zero-based row number
                           of the first row in the chunk.
                           [default: {}.csv]
    --pad <arg>            The zero padding width that is used in the
                           generated filename.
                           [default: 0]

                            FILTER OPTIONS:
    --filter <command>      Run the specified command on each chunk after it is written.
                            The command should use the FILE environment variable
                            ($FILE on Linux/macOS, %FILE% on Windows), which is
                            set to the path of the output file for each chunk.
                            The string '{}' in the command will be replaced by the
                            zero-based row number of the first row in the chunk.
    --filter-cleanup        Cleanup the original output filename AFTER the filter command
                            is run successfully for EACH chunk. If the filter command is not
                            successful, the original filename is not removed.
                            Only valid when --filter is used.
    --filter-ignore-errors  Ignore errors when running the filter command.
                            Only valid when --filter is used.

Common options:
    -h, --help             Display this message
    -n, --no-headers       When set, the first row will NOT be interpreted
                           as column names. Otherwise, the first row will
                           appear in all chunks as the header row.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -q, --quiet            Do not display an output summary to stderr.
```
## qsv scoresql

```text
Analyze a SQL query against CSV file caches (stats, moarstats, frequency) to produce a
performance score with actionable optimization suggestions BEFORE running the query.

Accepts the same input/SQL arguments as sqlp. Outputs a human-readable performance report
(default) or JSON (--json). Supports Polars mode (default) and DuckDB mode (--duckdb).

Scoring factors include:
  * Query plan analysis (EXPLAIN output from Polars or DuckDB)
  * Type optimization (column types vs. usage in query)
  * Join key cardinality and data distribution
  * Filter selectivity from frequency cache
  * Query anti-pattern detection (SELECT *, missing LIMIT, cartesian joins, etc.)
  * Infrastructure checks (index files, cache freshness)

Caches are auto-generated when missing:
  * stats cache via `qsv stats --everything --stats-jsonl`
  * frequency cache via `qsv frequency --frequency-jsonl`

Examples:

  # Score a simple filter query against a single CSV file
  $ qsv scoresql data.csv "SELECT * FROM data WHERE col1 > 10"

  # Output the score report as JSON instead of the default human-readable format
  $ qsv scoresql --json data.csv "SELECT col1, col2 FROM data ORDER BY col1"

  # Score a join query across two CSV files
  $ qsv scoresql data.csv data2.csv "SELECT * FROM data JOIN data2 ON data.id = data2.id"

  # Use DuckDB for query plan analysis instead of Polars
  $ qsv scoresql --duckdb data.csv "SELECT * FROM data WHERE status = 'active'"

  # Use _t_N aliases just like sqlp (see sqlp documentation)
  $ qsv scoresql data.csv data2.csv "SELECT * FROM _t_1 JOIN _t_2 ON _t_1.id = _t_2.id"

  # Score a query from a SQL script file (only the last query is scored)
  $ qsv scoresql data.csv script.sql

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_scoresql.rs.
See also https://github.com/dathere/qsv/wiki/SQL-and-Polars#scoresql

Usage:
    qsv scoresql [options] <input>... <sql>
    qsv scoresql --help

scoresql arguments:
    input                     The CSV file/s to analyze. Use '-' for standard input.
                              If input is a directory, all files in the directory will
                              be read as input.
                              If the input is a file with a '.infile-list' extension,
                              the file will be read as a list of input files.

    sql                       The SQL query to score/analyze.
                              If the query ends with ".sql", it will be read as a
                              SQL script file, with single-line "--" comments stripped.
                              If the script has multiple queries separated by ";",
                              only the last non-empty query is scored.

scoresql options:
    --json                    Output results as JSON instead of human-readable report.
    --duckdb                  Use DuckDB for query plan analysis instead of Polars.
                              Uses the QSV_DUCKDB_PATH environment variable if set,
                              otherwise looks for "duckdb" in PATH.
    --try-parsedates          Automatically try to parse dates/datetimes and time.
    --infer-len <arg>         Number of rows to scan when inferring schema.
                              [default: 10000]
    --ignore-errors           Ignore errors when parsing CSVs.
    --truncate-ragged-lines   Truncate lines with more fields than the header.

Common options:
    -h, --help                Display this message
    -o, --output <file>       Write output to <file> instead of stdout.
    -d, --delimiter <arg>     The field delimiter for reading CSV data.
                              Must be a single character. (default: ,)
    -q, --quiet               Do not print informational messages to stderr.
```
## qsv sqlp

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

Examples:

  $ qsv sqlp data.csv 'select * from data where col1 > 10 order by all desc limit 20'

  $ qsv sqlp data.csv 'select col1, col2 as friendlyname from data' --format parquet --output data.parquet

  # enclose column names with spaces in double quotes
  $ qsv sqlp data.csv 'select "col 1", "col 2" from data'

  $ qsv sqlp data.csv data2.csv 'select * from data join data2 on data.colname = data2.colname'

  $ qsv sqlp data.csv data2.csv 'SELECT col1 FROM data WHERE col1 IN (SELECT col2 FROM data2)'

  # Use dollar-quoting to avoid escaping reserved characters in literals.
  https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-DOLLAR-QUOTING
  $ qsv sqlp data.csv "SELECT * FROM data WHERE col1 = $$O'Reilly$$"
  $ qsv sqlp data.csv 'SELECT * FROM data WHERE col1 = $SomeTag$Diane'\''s horse "Twinkle"$SomeTag$'

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

  # FILTER clause on aggregates (SQL-standard) — apply a per-aggregate predicate without
  # filtering the whole group. Useful for computing conditional sums/counts side by side
  # with the unconditional aggregate in a single GROUP BY query.
  # See https://github.com/pola-rs/polars/pull/27564.
  $ qsv sqlp sales.csv "SELECT region, SUM(amount) AS total, \
       SUM(amount) FILTER (WHERE amount > 100) AS total_over_100, \
       COUNT(*) FILTER (WHERE status = 'refunded') AS refund_count \
     FROM sales GROUP BY region ORDER BY region"

  $ qsv sqlp data.csv "select lower(col1), substr(col2, 2, 4) from data WHERE starts_with(col1, 'foo')"

  $ qsv sqlp data.csv "select COALESCE(NULLIF(col2, ''), 'foo') from data"

  $ qsv sqlp tbl1.csv "SELECT x FROM tbl1 WHERE x IN (SELECT y FROM tbl1)"

  # Natural Joins are supported too! (https://www.w3resource.com/sql/joins/natural-join.php)
  $ qsv sqlp data1.csv data2.csv data3.csv \
    "SELECT COLUMNS('^[^:]+$') FROM data1 NATURAL JOIN data2 NATURAL JOIN data3 ORDER BY COMPANY_ID"

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
  # mem-mapped CSV parser instead - making for dramatically faster queries.
  $ qsv sqlp SKIP_INPUT "select * from read_csv('data.csv') order by col1 desc limit 100"

  # read_csv() takes Polars' scan_csv options as named arguments (name => value), e.g. for a
  # semicolon-delimited file with comment lines and no header row:
  $ qsv sqlp SKIP_INPUT "select * from read_csv('data.csv', separator => ';', comment_prefix => '#', has_header => false)"

  # read_ndjson() takes Polars' scan_ndjson options the same way: schema, schema_overrides,
  # infer_schema_length, ignore_errors and include_file_paths.
  # Infer the schema from the whole file, so a key that first appears late isn't dropped
  # (by default, only the first 100 rows are used):
  $ qsv sqlp SKIP_INPUT "select * from read_ndjson('events.jsonl', infer_schema_length => NULL)"
  # Type a column, and read a nested object as its JSON text. CSV output can't hold nested
  # data, so this avoids the "CSV format does not support nested data" error:
  $ qsv sqlp SKIP_INPUT "select * from read_ndjson('events.jsonl', schema_overrides => {'date': 'DATE', 'payload': 'VARCHAR'})"
  # Use an explicit schema, turn values that don't fit it into nulls, and add a column with
  # each row's source file:
  $ qsv sqlp SKIP_INPUT "select * from read_ndjson('events.jsonl', schema => {'id': 'INT', 'name': 'VARCHAR'}, ignore_errors => true, include_file_paths => 'source')"

  # note that you can also use read_csv() to read compressed files directly
  # gzip, zstd and zlib automatic decompression are supported
  $ qsv sqlp SKIP_INPUT "select * from read_csv('data.csv.gz')"
  $ qsv sqlp SKIP_INPUT "select * from read_csv('data.csv.zst')"
  $ qsv sqlp SKIP_INPUT "select * from read_csv('data.csv.zlib')"

  # apart from using Polar's table functions, you can also use SKIP_INPUT when the SELECT
  # statement doesn't require an input file
  $ qsv sqlp SKIP_INPUT "SELECT 1 AS one, '2' AS two, 3.0 AS three"

  # generate_series(start, stop[, step]) and range(start, stop[, step]) generate a column of
  # integers. generate_series includes stop; range does not.
  $ qsv sqlp SKIP_INPUT "SELECT * FROM generate_series(1, 10, 2)"

  # use stdin as input
  $ cat data.csv | qsv sqlp - 'select * from stdin'
  $ cat data.csv | qsv sqlp - data2.csv 'select * from stdin join data2 on stdin.col1 = data2.col1'

  # automatic snappy decompression/compression
  $ qsv sqlp data.csv.sz 'select * from data where col1 > 10' --output result.csv.sz

  # explain query plan
  $ qsv sqlp data.csv 'explain select * from data where col1 > 10 order by col2 desc limit 20'

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_sqlp.rs.
See also https://github.com/dathere/qsv/wiki/SQL-and-Polars#sqlp

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
                                csv, json, jsonl, parquet, arrow, avro
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
                              Date columns in formats Polars can't parse are saved as String,
                              as are day-first dates unless QSV_PREFER_DMY is set.
                              Each schema file will have the same file stem as the corresponding
                              input file, with the extension ".pschema.json"
                              (data.csv's Polars schema file will be data.pschema.json)
                              NOTE: You can edit the generated schema files to change the Polars schema
                              and cast columns to the desired data type. Float columns are saved
                              as Float64. For example, to save memory you can narrow a Float64
                              column to Float32 by changing its "Float64" type to "Float32" in the
                              schema file, at the cost of precision (Float32 holds only about
                              7 significant digits).
                              You can also cast a Float to a Decimal with a desired precision and scale.
                              (e.g. instead of "Float64", use {"Decimal": [10, 3]})
                              The valid types are: `Boolean`, `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`,
                              `Int16`, `Int32`, `Int64`, `Float32`, `Float64`, `String`, `Date`, `Datetime`,
                              `Duration`, `Time`, `Null`, `Categorical`, `Decimal` and `Enum`.

    --streaming               Write the query result as it is computed, batch by batch, instead
                              of collecting the whole result in memory first. Use this when the
                              result is too big for memory. Works with the csv, jsonl, parquet
                              and arrow formats; json and avro output still collect the whole
                              result. Queries already run on Polars' streaming engine either way.
                              An --output file is written beside its target and only moved
                              into place if the query succeeds. Overwriting an existing file
                              copies the result into it, so it keeps its owner, group, mode
                              and links; that briefly needs disk space for two copies. On stdout, rows are sent as
                              they are computed, so a query that fails part-way leaves its
                              output cut short; check sqlp's exit code before using it.
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
    --compression <arg>       The compression codec to use when writing arrow, avro or parquet files.
                              The `zstd` default below applies to Arrow and Parquet. Avro does not
                              support zstd, so when `--compression` is omitted Avro silently falls
                              back to uncompressed unless you pass an Avro-supported codec.
                                For Arrow, valid values are: `zstd`, `lz4`, `uncompressed`.
                                For Avro, valid values are: `deflate`, `snappy`, `uncompressed`.
                                For Parquet, valid values are: `zstd`, `lz4raw`, `gzip`, `snappy`, `uncompressed`.
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
                           Must be a single character. (default: ,)
    -q, --quiet            Do not return result shape to stderr.
```
## qsv stats

```text
Compute summary statistics & infers data types for each column in a CSV.

IMPORTANT: `stats` is heavily optimized for speed. It ASSUMES the CSV is well-formed & UTF-8 encoded.
This allows it to employ numerous performance optimizations (skip repetitive UTF-8 validation, skip
bounds checks, cache results, etc.) that may result in undefined behavior if the CSV is not well-formed.
All these optimizations are GUARANTEED to work with well-formed CSVs.
If you encounter problems generating stats, use `qsv validate` FIRST to confirm the CSV is valid.

NOTE: For MAXIMUM PERFORMANCE, create an index for the CSV first with 'qsv index' to enable multithreading,
or set --cache-threshold option or set the QSV_AUTOINDEX_SIZE environment variable to automatically
create an index when the file size is greater than the specified size (in bytes).

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
It returns "*ALL" if all the values are unique (with --weight, if all the values are unique
AND have the same weight), and only returns a preview of the first
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
in <FILESTEM>.stats.csv & if the --stats-jsonl option is used, <FILESTEM>.stats.csv.data.jsonl
(e.g., qsv stats nyc311.csv will create nyc311.stats.csv; adding --stats-jsonl also creates
nyc311.stats.csv.data.jsonl).
The arguments used to generate the cached stats are saved in <FILESTEM>.stats.csv.json.

If stats have already been computed for the input file with similar arguments and the file
hasn't changed, the stats will be loaded from the cache instead of recomputing it.

These cached stats are also used by other qsv commands (currently `describegpt`, `frequency`,
`joinp`, `pivotp`, `schema`, `sqlp` & `tojsonl`) to work smarter & faster.
If the cached stats are not current (i.e., the input file is newer than the cached stats),
the cached stats will be ignored and recomputed.

Examples:

  # Compute "streaming" statistics for "nyc311.csv"
  qsv stats nyc311.csv

  # Compute all statistics for "nyc311.csv"
  qsv stats --everything nyc311.csv

  # Compute all statistics for "nyc311.tsv" (Tab-separated)
  qsv stats -E nyc311.tsv

  # Compute all stats for "nyc311.tsv", inferring dates using sniff to auto-detect date columns
  qsv stats -E --infer-dates nyc311.tsv

  # Compute all stats for "nyc311.tab", inferring dates only for columns
  #  with "_date" & "_dte" in the column names
  qsv stats -E --infer-dates --dates-whitelist _date,_dte nyc311.tab

  # Compute all stats, infer dates and boolean data types for "nyc311.ssv" file
  qsv stats -E --infer-dates --infer-boolean nyc311.ssv

  # In addition to basic "streaming" stats, also compute cardinality for "nyc311.csv"
  qsv stats --cardinality nyc311.csv

  # Prefer DMY format when inferring dates for the "nyc311.csv"
  qsv stats -E --infer-dates --prefer-dmy nyc311.csv

  # Infer data types only for the "nyc311.csv" file:
  qsv stats --typesonly nyc311.csv

  # Infer data types only, including boolean and date types for "nyc311.csv"
  $ qsv stats --typesonly --infer-boolean --infer-dates nyc311.csv

  # Automatically create an index for the "nyc311.csv" file to enable multithreading
  # if it's larger than 5MB and there is no existing index file:
  qsv stats -E --cache-threshold -5000000 nyc311.csv

  # Auto-create a TEMPORARY index for the "nyc311.csv" file to enable multithreading
  # if it's larger than 5MB and delete the index and the stats cache file after the stats run:
  qsv stats -E --cache-threshold -5000005 nyc311.csv

For more examples, see https://github.com/dathere/qsv/tree/master/resources/test
See also https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#stats

If the polars feature is enabled, support additional tabular file formats and
compression formats:
  $ qsv stats data.parquet // Parquet
  $ qsv stats data.avro // Avro
  $ qsv stats data.jsonl // JSON Lines
  $ qsv stats data.json (will only work with a JSON Array)
  $ qsv stats data.csv.gz // Gzipped CSV
  $ qsv stats data.tab.zlib // Zlib-compressed Tab-separated
  $ qsv stats data.ssv.zst // Zstd-compressed Semicolon-separated

For more info, see https://github.com/dathere/qsv/blob/master/docs/STATS_DEFINITIONS.md

Usage:
    qsv stats [options] [<input>]
    qsv stats --help

stats options:
    -s, --select <arg>        Select a subset of columns to compute stats for.
                              See 'qsv select --help' for the format details.
                              This is provided here because piping 'qsv select'
                              into 'qsv stats' will prevent the use of indexing.
    -E, --everything          Compute all statistics available.
                              On large files, mode & cardinality tracking dominates
                              memory use. See --mode-cardinality-cap for how to bound it.
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
    --zero-padded-numeric     Add a "zero_padded_numeric" column that is "true" when a column's
                              leading/padding zeros would be lost if it were cast to a number.
                              Qualifies when the inferred type is String AND every non-null value is
                              numeric (an all-digit integer or a zero-padded decimal code), with at
                              least one carrying a leading zero — e.g. US zip codes, barcodes,
                              zero-padded IDs, and zero-padded decimal codes like 007.1, 05.10 (as in
                              ICD-9, Dewey Decimal & Harmonized System classification codes).
                              qsv keeps all of these as text to preserve their leading zeros, so they
                              are not mistakenly loaded/cast as integer/float. Note that ordinary
                              fractions (0.5) and pure trailing-zero codes (7.10) are not flagged.
                              The cell is empty when the column is not zero-padded numeric.
                              Automatically enabled with --everything.

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
    --quantile-method <m>     Algorithm used to compute the median, quartiles and custom
                              percentiles. Choices:
                                exact  - load all values into memory and sort (current behavior).
                                         O(N) memory per numeric column, exact deterministic
                                         results.
                                approx - use t-digest (Apache DataSketches port, based on
                                         Dunning's MergingDigest). O(K) memory per numeric column
                                         (K~200 centroids), O(1) quantile reads. Approximate
                                         (~1% rank error, more accurate at the tails).
                                         Restrictions:
                                           * --mad is disabled with a warning under approx.
                                           * --weight is rejected; the upstream datasketches
                                             crate does not expose weighted-update.
                                           * Results may differ slightly across runs with
                                             different --jobs values.
                                           * Requires a little-endian target. Apache
                                             DataSketches does not support big-endian
                                             platforms (e.g., s390x); on those builds,
                                             this choice is rejected.
                              [default: exact]
    --cardinality-method <m>  Algorithm used to compute the --cardinality column. Choices:
                                exact  - track every unique value in a frequency map
                                         (current behavior). O(cardinality) memory per
                                         column. Subject to --mode-cardinality-cap, which
                                         emits the ">=<n>" sentinel on overflow.
                                approx - use HyperLogLog (Apache DataSketches port,
                                         lg_k=12). O(1) memory per column (~5KB),
                                         ~1.5% relative standard error.
                                         Notes:
                                           * --mode-cardinality-cap no longer affects the
                                             cardinality column under approx; the ">=<n>"
                                             sentinel is never emitted.
                                           * The cap STILL governs mode/antimode tracking
                                             (mode columns still emit "*HIGH_CARDINALITY"
                                             on overflow).
                                           * --infer-boolean forces exact (boolean
                                             inference needs cardinality == 2 exactness);
                                             a one-time warning is emitted.
                                           * When modes are computed (with --mode or
                                             with --everything) and no mode cardinality
                                             cap is set, the exact mode tracker counts every
                                             unique value, so that exact count is reported
                                             and no sketch is built. With a cap, the
                                             estimate is used only for columns whose
                                             tracker was dropped.
                                           * The estimate never exceeds the row count.
                                           * Reproducible across PARALLEL --jobs values:
                                             the HLL union used at merge time is
                                             associative and order-invariant, so chunk
                                             completion order does not affect the final
                                             estimate. --jobs 1 never reaches that union
                                             and so can report a different estimate than
                                             a parallel run - pin --jobs when comparing
                                             cardinality across runs.
                                           * Requires a little-endian target. Apache
                                             DataSketches does not support big-endian
                                             platforms (e.g., s390x); on those builds,
                                             this choice is rejected.
                              [default: exact]
    --mode-cardinality-cap <n>  Bound mode-tracking memory on high-cardinality columns.
                              When > 0, if a column's mode tracker grows past <n> UNIQUE
                              values (true cardinality, for both unweighted and weighted
                              runs), qsv drops it and emits sentinel values instead of
                              exact modes and cardinality. The cap is a direct memory
                              bound on the tracker, which stores one entry per unique
                              value.
                              Sentinel output:
                                * mode columns: "*HIGH_CARDINALITY"
                                * cardinality column: ">=<n>" (the ">=" prefix DOES break
                                  downstream parsers expecting a plain integer; cap is
                                  opt-in only).
                              Under --cardinality-method approx, the cardinality column
                              ignores this cap (HLL gives an approximate estimate at
                              fixed memory, ~1.5% RSE) — only mode/antimode columns
                              are gated.
                              Useful on wide tables with many ID/UUID/timestamp columns
                              where tracking exact cardinality is wasted work.
                              For large files, a cap of 10000 combined with
                              "--cardinality-method approx" keeps an approximate
                              cardinality for capped columns. On a 1M-row, 44-column
                              file this cut --everything's peak memory by ~65% and
                              its runtime by half. Parallel runs warn when mode &
                              cardinality tracking may not fit in available memory.
                              [default: 0]

    --round <decimal_places>  Round statistics to <decimal_places>. Rounding is done following
                              Midpoint Nearest Even (aka "Bankers Rounding") rule.
                              https://docs.rs/rust_decimal/latest/rust_decimal/enum.RoundingStrategy.html
                              If set to the sentinel value 9999, no rounding is done.
                              For dates - range, stddev & IQR are rounded to 1e-5 day precision
                              (sub-second), with trailing zeros trimmed in the displayed output.
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

                              Special values:
                              * "all" - inspect ALL fields for date/datetime types
                              * "sniff" - use `qsv sniff` to auto-detect date/datetime columns

                              Note that false positive date matches WILL most likely occur
                              when using "all" as unix epoch timestamps are just numbers.
                              Be sure to only use "all" if you know ALL the columns you're
                              inspecting are dates, boolean or string fields.

                              To avoid false positives, preprocess the file first
                              with the `datefmt` command to convert unix epoch timestamp
                              columns to RFC3339 format.

                              When set to "sniff", we do two-stage date inferencing.
                              First running sniff on the input file and then second,
                              only inferring dates for the columns that sniff identifies
                              as date/datetime candidates.
                              This is much faster than "all", and more convenient than
                              manually specifying patterns in the whitelist.
                              [default: sniff]
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
    --jsonl                   Emit the stats to stdout as JSON Lines (NDJSON) - one JSON object
                              per column - instead of CSV. This is the same per-column shape
                              the --stats-jsonl sidecar file uses, but streamed to stdout.
                              Respects --output (the NDJSON is written to the file instead).
                              Cannot be combined with --stats-jsonl or --pretty-json.
    --pretty-json             Like --jsonl, but emit a single pretty-printed JSON array of the
                              per-column objects instead of newline-delimited objects.
                              Cannot be combined with --stats-jsonl or --jsonl.
 -c, --cache-threshold <arg>  Controls the creation of stats cache files.
                                * when greater than 1, the threshold in milliseconds before caching
                                  stats results. If a stats run takes longer than this threshold,
                                  the stats results will be cached.
                                * 0 to suppress caching.
                                * 1 to force caching.
                                * a negative number to automatically create an index when
                                  the input file size is greater than abs(arg) in bytes.
                                  If the negative number ends with 5, it will delete the index
                                  file and the stats cache file after the stats run. Otherwise,
                                  the index file and the cache files are kept.
                              [default: 5000]
    --vis-whitespace          Visualize whitespace characters in the output.
                              See https://github.com/dathere/qsv/wiki/Aggregation-and-Statistics#whitespace-markers
                              for the list of whitespace markers.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will NOT be interpreted
                           as column names. i.e., They will be included
                           in statistics.
    -d, --delimiter <arg>  The field delimiter for READING CSV data.
                           Must be a single character. (default: ,)
    --flexible             Allow records with a varying number of fields.
                           Without this, a "ragged" record (one with more or
                           fewer fields than the header) is an error. With it,
                           extra fields are ignored and a SHORT record
                           contributes no value at all for its missing
                           columns (not even a null), so those columns are computed
                           over fewer observations. Note that field selection
                           stops at the first missing column, so an
                           out-of-order selection (e.g. `3,1`) makes a short
                           record skip columns that ARE present.
    --memcheck             Use CONSERVATIVE heuristics for the in-memory load
                           check (file size vs. available + free_swap × platform
                           factor − headroom), instead of the default NORMAL
                           check (file size vs. total memory − headroom). The
                           CONSERVATIVE check is stricter and trips OOM far
                           more readily. Ignored when computing default,
                           streaming statistics. (See also: QSV_MEMORY_CHECK
                           env var, equivalent to passing --memcheck.)
                           Independently of this flag, the in-memory load
                           check runs whenever stats takes the non-parallel
                           path with non-streaming columns. On OOM (in either
                           NORMAL or CONSERVATIVE mode), qsv auto-creates an
                           index when no index exists (skipped for stdin) AND
                           switches to approx quantile + approx cardinality
                           methods (DataSketches t-digest and HyperLogLog)
                           where compatible. The sketch fallback can also
                           fire when an index is already present and the OOM
                           still trips (e.g., when jobs is pinned to 1 on a
                           pre-indexed file). A wwarn is emitted listing the
                           auto-enabled estimators.
                           When modes are computed (with --mode or with the
                           everything option) and no mode cardinality cap is
                           set, approx cardinality is NOT auto-enabled: the exact
                           mode table is kept either way, so it would save
                           nothing. A wwarn suggests --mode-cardinality-cap,
                           which is what bounds that table.
```
## qsv synthesize

```text
Generates a synthetic CSV that is statistically faithful to a source CSV.

`synthesize` analyzes <input> with `stats` and `frequency`, then emits N rows of
fake data that reproduce the source's per-column attributes:

  * Categorical / low-cardinality columns are reproduced by frequency-weighted
    sampling of their *real* value set — cardinality, weights and repetition
    structure are preserved exactly.
  * Numeric and date/datetime columns are reproduced with quartile buckets, so
    the shape of the distribution (not just its [min,max] range) is preserved.
  * Null ratios are reproduced per column.

When a Data Dictionary is supplied (via --dictionary, or generated on the fly
with --infer-content-type), each column's semantic Content Type picks a
realistic faker (names, emails, addresses, UUIDs, etc.) for columns that are
NOT fully enumerated by `frequency`. For bounded-cardinality faker columns
(cardinality < requested rows and below an internal cap of 100,000), a fixed
pool of distinct fake values is pre-generated and sampled from, so the column's
cardinality is preserved. For very high cardinality columns above this cap, a
fresh fake value is generated per row instead — distinct count is approximate
in that case.

When `stats` provides string-length statistics (min_length / max_length /
avg_length / stddev_length) AND the column is routed to an unstructured text
generator (lorem_*, free_text, or the no-faker fallback), synthesized values
are truncated so their character lengths follow Normal(avg_length,
stddev_length) clamped to [min_length, max_length]. This applies to unstructured
pooled values as well — a low-cardinality free-text column still gets its
generated pool entries truncated. Structured semantic fakers (email, name,
uuid, phone, address parts, etc.) ignore these stats — truncating them would
corrupt their format, so their pools are reproduced verbatim. Frequency-
enumerated values are always reproduced verbatim and are never truncated.

When the Data Dictionary declares `relationships`, the named columns are
generated *jointly* so inter-column structure survives into each output row:

  * joint      — categorical / functional-dependency groups (e.g.
                 city/state/zip). Whole value-tuples are sampled from the
                 source by frequency, so only real co-occurring combinations
                 are emitted.
  * ordered    — columns that must keep a monotonic order within a row (e.g.
                 created_date <= closed_date). The anchor column is generated
                 from its own distribution; each later column is the anchor
                 plus a non-negative gap drawn from the gap distribution
                 learned from the source.
  * correlated — numeric columns whose correlation should be preserved. A
                 Gaussian copula couples the columns while leaving each
                 column's own distribution unchanged.

Relationships are read from the dictionary's `relationships` array — inferred
by `describegpt` or hand-authored. Columns not named by any relationship are
still generated independently. Pass --no-relationships to disable relationship
modeling entirely.

With --seed, output is fully reproducible.

Examples:

  # Pure statistical synthesis — no dictionary needed
  $ qsv synthesize data.csv -n 1000 --seed 42 > synthetic.csv

  # First, generate the Data Dictionary with describegpt
  $ qsv describegpt data.csv --dictionary --infer-content-type --format JSON -o dict.json
  # Then layer in semantic fakers from the dictionary
  $ qsv synthesize data.csv --dictionary dict.json -n 1000 > synthetic.csv

  # Let synthesize build the dictionary itself (needs an LLM API key)
  $ qsv synthesize data.csv --infer-content-type -n 1000 > synthetic.csv

  # Preserve inter-column relationships declared in the dictionary
  # (e.g. city/state/zip, created_date <= closed_date)
  $ qsv synthesize data.csv --dictionary dict.json -n 1000 > synthetic.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_synthesize.rs.
See also https://github.com/dathere/qsv/wiki/AI-and-Documentation#synthesize

Usage:
    qsv synthesize [options] <input>
    qsv synthesize --help

synthesize options:
    --dictionary <file>    Data Dictionary JSON file produced by
                           `describegpt --dictionary --infer-content-type --format JSON`.
                           Layers semantic Content Types onto generation. If
                           omitted, generation is purely type/frequency-based.
    --infer-content-type   Generate the Data Dictionary on the fly by invoking
                           `describegpt --dictionary --infer-content-type` on
                           <input>. Requires an LLM API key (QSV_LLM_APIKEY).
                           Ignored if --dictionary is given.
    -n, --rows <n>         Number of synthetic rows to generate. [default: 100]
    --seed <n>             RNG seed for fully reproducible output.
    --locale <loc>         Locale for faker-backed columns. Case-insensitive.
                           Supported: en, fr_fr, de_de, it_it, pt_br, pt_pt,
                           ja_jp, zh_cn, zh_tw, ar_sa, cy_gb, fa_ir, nl_nl,
                           tr_tr. Sparse locales (those without per-category
                           data in fake-rs) silently fall back to en data for
                           the missing categories — e.g. lorem text under a
                           non-en locale is still English, since only zh_cn
                           has localized lorem data. [default: en]
    --freq-limit <n>       Frequency pool depth passed to the internal `frequency`
                           run as --limit. A column is reproduced via exact
                           frequency-weighted sampling only when its cardinality
                           is fully captured within this limit; higher values
                           reproduce more columns verbatim. 0 means unlimited.
                           [default: 100]
    --stats-options <arg>  Extra options appended to the internal `stats` run.
                           Note: cardinality, quartiles and date inference are
                           always enabled — do not re-specify them here.
    --consistent-fakes     For structured-faker columns with bounded cardinality
                           (cardinality fully captured by `frequency`), build a
                           stable source-value -> fake-value mapping so the same
                           source value always produces the same fake in the
                           output. Preserves the source frequency distribution
                           and overrides the default "emit real values when
                           frequency-enumerated" behavior for structured fakers
                           (names, emails, addresses, etc.). Has no effect on
                           unstructured columns (lorem_*, free_text, unknown),
                           all-unique columns, or non-faker columns. Useful for
                           deidentified synthesis where you want stable joins
                           on the faked columns.
    --no-relationships     Disable inter-column relationship modeling. Every
                           column is generated independently even when the
                           dictionary declares a `relationships` array.
    --joint-cardinality-cap <n>  Maximum number of distinct value-tuples a
                           `joint` relationship may have. A joint group above
                           this cap falls back to independent generation (or
                           aborts under --strict-relationships). 0 means
                           unlimited. [default: 100000]
    --correlation-threshold <f>  Minimum absolute Spearman correlation for a
                           pair of columns to stay in a `correlated`
                           relationship. Weakly-correlated members are dropped.
                           [default: 0.3]
    --strict-relationships  Abort instead of warning-and-degrading when a
                           declared relationship fails validation.
    -j, --jobs <arg>       Number of jobs to use for the internal `stats` and
                           `frequency` runs.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading the input CSV.
                           Must be a single character. (default: ,)
```
## qsv table

```text
Outputs CSV data as a table with columns in alignment.

Though this command is primarily designed for DISPLAYING CSV data using
"elastic tabstops" so its more human-readable, it can also be used to convert
CSV data to other special machine-readable formats:
 -  a more human-readable TSV format with the "leftendtab" alignment option
 -  Fixed-Width format with the "leftfwf" alignment option - similar to "left",
    but with the first line being a comment (prefixed with "#") that enumerates
    the position (1-based, comma-separated) of each column (e.g. "#1,10,15").

This will not work well if the CSV data contains large fields.

Note that formatting a table requires buffering all CSV data into memory.
Therefore, you should use the 'sample' or 'slice' command to trim down large
CSV data before formatting it with this command.

See also https://github.com/dathere/qsv/wiki/Selection-and-Inspection#table

Usage:
    qsv table [options] [<input>]
    qsv table --help

table options:
    -w, --width <arg>      The minimum width of each column.
                           [default: 2]
    -p, --pad <arg>        The minimum number of spaces between each column.
                           [default: 2]
    -a, --align <arg>      How entries should be aligned in a column.
                           Options: "left", "right", "center", "leftendtab", "leftfwf".
                           "leftendtab" is a special alignment that similar to "left"
                           but with whitespace padding ending with a tab character.
                           The resulting output still validates as a valid TSV file,
                           while also being more human-readable (aka "aligned" TSV).
                           "leftfwf" is similar to "left" with Fixed Width Format alignment.
                           The first line is a comment (prefixed with "#") that enumerates
                           the position (1-based, comma-separated) of each column.
                           [default: left]
    -c, --condense <arg>   Limits the length of each field to the value
                           specified. If the field is UTF-8 encoded, then
                           <arg> refers to the number of code points.
                           Otherwise, it refers to the number of bytes.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
```
## qsv template

```text
Renders a template using CSV data with the MiniJinja template engine.
https://docs.rs/minijinja/latest/minijinja/

This command processes each row of the CSV file, making the column values available as variables.
Each row is rendered using the template. Column headers become variable names, with non-alphanumeric
characters converted to underscore (_).

Templates use Jinja2 syntax (https://jinja.palletsprojects.com/en/stable/templates/)
and can access an extensive library of built-in filters/functions, with additional ones
from minijinja_contrib https://docs.rs/minijinja-contrib/latest/minijinja_contrib/.
Additional qsv custom filters are also documented at the end of this file.

If the <outdir> argument is specified, it will create a file for each row in <outdir>, with
the filename rendered using --outfilename option.
Otherwise, ALL the rendered rows will be sent to STDOUT or the designated --output.

Example:

data.csv
```csv
"first name","last name",balance,"loyalty points",active,us_state
alice,jones,100.50,1000,true,TX
bob,smith,200.75,2000,false,CA
john,doe,10,1,true,NJ
```

template.tpl
```jinja
{% set us_state_lookup_loaded = register_lookup("us_states", "dathere://us-states-example.csv") -%}
Dear {{ first_name|title }} {{ last_name|title }}!
Your account balance is {{ balance|format_float(2) }}
    with {{ loyalty_points|human_count }} point{{ loyalty_points|int|pluralize }}!
{# This is a comment and will not be rendered. The closing minus sign in this
    block tells MiniJinja to trim whitespaces -#}
{% if us_state_lookup_loaded -%}
    {% if us_state not in ["DE", "CA"] -%}
        {% set tax_rate = us_state|lookup("us_states", "Sales Tax (2023)")|float -%}
        State: {{ us_state|lookup("us_states", "Name") }} {{us_state}} Tax Rate: {{ tax_rate }}%
        {% set loyalty_value = loyalty_points|int / 100 -%}
        {%- set tax_amount = loyalty_value * (tax_rate / 100) -%}
        {%- set loyalty_value = loyalty_value - tax_amount -%}
        Value of Points: {{ loyalty_value }}
    {% else %}
        {% set loyalty_value = 0 -%}
    {% endif %}
    Final Balance: {{ (balance|int - loyalty_value)|format_float(2) }}
{% endif %}
Status: {% if active|to_bool %}Active{% else %}Inactive{% endif %}
```

  $ qsv template --template-file template.tpl data.csv

> [!NOTE]
> All variables are of type String and will need to be cast with the `|float` or `|int`
>  filters for math operations and when a MiniJinja filter/function requires it.
> qsv's custom filters (substr, format_float, human_count, human_float_count, round_banker &
> str_to_bool) do not require casting for convenience.
> Booleans render as `True`/`False` and none (e.g. a JSON null reached via `fromjson`)
>  renders as `None`, matching Jinja2. Use `{{ v or "" }}` for an empty string instead —
>  a bare `{{ v|default("") }}` does NOT substitute for none, only for undefined.

Additional qsv-specific data-wrangling filters/functions (available in all binary variants):
```
regex_replace(pattern, replacement)  Replace ALL regex matches ($1/${name} capture refs).
regex_match(pattern)                 True if the regex matches anywhere, e.g. in {% if %}.
regex_find(pattern)                  First whole regex match, or "" if none.
floor / ceil                         Round down / up. Integer inputs stay exact; fractional
                                     inputs return a float (pipe |int, e.g. v|floor|int).
datefmt(fmt[, prefer_dmy])           Parse a messy date string (19+ formats) & reformat with
                                     a chrono format string, e.g. d|datefmt("%Y-%m-%d").
zfill(width)                         Left-pad with zeros (keeps leading sign), "42"|zfill(5)="00042".
lpad(width[, fill]) / rpad(...)      Left/right pad to width with fill char (default space).
slugify                              URL/DB/CKAN-safe slug, "NYC 311 Data!"|slugify="nyc-311-data".
blake3                               BLAKE3 hex digest of the value (stable surrogate/content keys).
fromjson / parse_json                Parse a JSON string into an indexable value, (j|fromjson).key.
coalesce(a, b, ...)                  First argument that is not undefined/none/empty string.
```

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_template.rs.
See also https://github.com/dathere/qsv/wiki/Scripting-Luau-Python#template
For a relatively complex MiniJinja template, see https://github.com/dathere/qsv/blob/master/scripts/template.tpl

Usage:
    qsv template [options] [--template <str> | --template-file <file>] [<input>] [<outdir> | --output <file>]
    qsv template --help

template arguments:
    <input>                     The CSV file to read. If not given, input is read from STDIN.
    <outdir>                    The directory where the output files will be written.
                                If it does not exist, it will be created.
                                If not set, output will be sent to stdout or the specified --output.
                                When writing to <outdir>, files are organized into subdirectories
                                of --outsubdir-size (default: 1000) files each to avoid filesystem
                                navigation & performance issues.
                                For example, with 3500 records:
                                  * <outdir>/0000/0001.txt through <outdir>/0000/1000.txt
                                  * <outdir>/0001/1001.txt through <outdir>/0001/2000.txt
                                  * <outdir>/0002/2001.txt through <outdir>/0002/3000.txt
                                  * <outdir>/0003/3001.txt through <outdir>/0003/4000.txt
template options:
    --template <str>            MiniJinja template string to use (alternative to --template-file)
    -t, --template-file <file>  MiniJinja template file to use
    -J, --globals-json <file>   A JSON file containing global variables to make available in templates.
                                The JSON properties can be accessed in templates using the "qsv_g"
                                namespace (e.g. {{qsv_g.school_name}}, {{qsv_g.year}}).
                                This allows sharing common values across all template renders.
    --outfilename <str>         MiniJinja template string to use to create the filename of the output
                                files to write to <outdir>. If set to just QSV_ROWNO, the filestem
                                is set to the current rowno of the record, padded with leading
                                zeroes, with the ".txt" extension (e.g. 001.txt, 002.txt, etc.)
                                Note that all the fields, including QSV_ROWNO, are available
                                when defining the filename template.
                                [default: QSV_ROWNO]
    --outsubdir-size <num>      The number of files per subdirectory in <outdir>.
                                [default: 1000]
    --customfilter-error <msg>  The value to return when a custom filter returns an error.
                                Use "<empty string>" to return an empty string.
                                [default: <FILTER_ERROR>]
    -j, --jobs <arg>            The number of jobs to run in parallel.
                                When not set, the number of jobs is set to the number of CPUs detected.
    -b, --batch <size>          The number of rows per batch to load into memory, before running in parallel.
                                Set to 0 to load all rows in one batch.
                                [default: 50000]
    --timeout <seconds>        Timeout for downloading lookups on URLs. [default: 30]
    --cache-dir <dir>          The directory to use for caching downloaded lookup resources.
                               If the directory does not exist, qsv will attempt to create it.
                               If the QSV_CACHE_DIR envvar is set, it will be used instead.
                               [default: ~/.qsv-cache]
    --ckan-api <url>           The URL of the CKAN API to use for downloading lookup resources
                               with the "ckan://" scheme.
                               If the QSV_CKAN_API envvar is set, it will be used instead.
                               [default: https://data.dathere.com/api/3/action]
    --ckan-token <token>       The CKAN API token to use. Only required if downloading private resources.
                               If the QSV_CKAN_TOKEN envvar is set, it will be used instead.

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout
    -n, --no-headers            When set, the first row will not be interpreted
                                as headers. Templates must use numeric 1-based indices
                                with the "_c" prefix. (e.g. col1: {{_c1}} col2: {{_c2}})
    --delimiter <sep>           Field separator for reading CSV (default: ,)
    -p, --progressbar           Show progress bars. Not valid for stdin.
```
## qsv tojsonl

```text
Smartly converts CSV to a newline-delimited JSON (JSONL/NDJSON).

By computing stats on the CSV first, it "smartly" infers the appropriate JSON data type
for each column (string, number, boolean, null).

It will infer a column as boolean if its cardinality is 2, and the first character of
the values are one of the following case-insensitive combinations:
  t/f; t/null; 1/0; 1/null; y/n & y/null are treated as true/false.

The `tojsonl` command will reuse a `stats.csv.data.jsonl` file if it exists and is
current (i.e. stats generated with --cardinality and --infer-dates options) and will
skip recomputing stats.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_tojsonl.rs.
See also https://github.com/dathere/qsv/wiki/Conversion-and-IO#tojsonl

Usage:
    qsv tojsonl [options] [<input>]
    qsv tojsonl --help

Tojsonl options:
    --trim                 Trim leading and trailing whitespace from fields
                           before converting to JSON.
    --no-boolean           Do not infer boolean fields.
    -j, --jobs <arg>       The number of jobs to run in parallel.
                           When not set, the number of jobs is set to the
                           number of CPUs detected.
    -b, --batch <size>     The number of rows per batch to load into memory,
                           before running in parallel. Automatically determined
                           for CSV files with more than 50000 rows.
                           Set to 0 to load all rows in one batch.
                           Set to 1 to force batch optimization even for files with
                           less than 50000 rows.
                           [default: 50000]

Common options:
    -h, --help             Display this message
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -o, --output <file>    Write output to <file> instead of stdout.
                           Use "-" to explicitly write to stdout.
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
    -q, --quiet            Do not display enum/const list inferencing messages.
```
## qsv to

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
See also https://github.com/dathere/qsv/wiki/Conversion-and-IO#to

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
  -A, --all-strings       Convert all fields to strings. For parquet, columns are read
                          as strings without type inference, so the inference length
                          and any pschema.json are not used.
  -j, --jobs <arg>        The number of jobs to run in parallel.
                          When not set, the number of jobs is set to the number of CPUs detected.

Common options:
    -h, --help             Display this message
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## qsv transpose

```text
Transpose the rows/columns of CSV data.

Usage:
    qsv transpose [options] [<input>]
    qsv transpose --help

Examples:
    # Transpose data in-memory.
    $ qsv transpose data.csv

    # Transpose data using multiple passes. For large datasets.
    $ qsv transpose data.csv --multipass

    # Convert CSV to "long" format using the first column as the "field" identifier
    $ qsv transpose data.csv --long 1

    # use the columns "name" & "age" as the "field" identifier
    $ qsv transpose --long "name,age" data.csv

    # use the columns 1 & 3 as the "field" identifier
    $ qsv transpose --long 1,3 data.csv

    # use the columns 1 to 3 as the "field" identifier
    $ qsv transpose --long 1-3 data.csv

    # use all columns starting with "name" as the "field" identifier
    $ qsv transpose --long /^name/ data.csv

See https://github.com/dathere/qsv/blob/master/tests/test_transpose.rs for more examples.
See also https://github.com/dathere/qsv/wiki/Transform-and-Reshape#transpose

transpose options:
    -m, --multipass        Process the transpose by making multiple passes
                           over the dataset. Consumes memory relative to
                           the number of rows.
                           Note that in general it is faster to
                           process the transpose in memory.
                           Useful for really big datasets as the default
                           is to read the entire dataset into memory.
    -s, --select <arg>     Select a subset of columns to transpose.
                           When used with --long, this filters which columns
                           become attribute rows (the field columns are unaffected).
                           See 'qsv select --help' for the full selection syntax.
    --long <selection>     Convert wide-format CSV to "long" format.
                           Output format is three columns:
                           field, attribute, value. Empty values are skipped.
                           Mutually exclusive with --multipass.

                           The <selection> argument is REQUIRED when using --long,
                           it specifies which column(s) to use as the "field" identifier.
                           It uses the same selection syntax as 'qsv select':
                           * Column names: --long varname or --long "column name"
                           * Column indices (1-based): --long 5 or --long 2,3
                           * Ranges: --long 1-4 or --long 3-
                           * Regex patterns: --long /^prefix/
                           * Comma-separated: --long var1,var2 or --long 1,3,5
                           Multiple field columns are concatenated with | separator.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
                           Ignored when --multipass or --long option is enabled.
```
## qsv validate

```text
Validates CSV data using two main modes:

JSON SCHEMA VALIDATION MODE:
===========================

This mode is invoked if a JSON Schema file (draft 2020-12) is provided.

The CSV data is validated against the JSON Schema. If the CSV data is valid, no output
files are created and the command returns an exit code of 0.

If invalid records are found, they are put into an "invalid" file, with the rest of the
records put into a "valid"" file.

A "validation-errors.tsv" report is also created with the following columns:

  * row_number: the row number of the invalid record
  * field: the field name of the invalid field
  * error: a validation error message detailing why the field is invalid

It uses the JSON Schema Validation Specification (draft 2020-12) to validate the CSV.
It validates the structure of the file, as well as the data types and domain/range of the fields.
See https://json-schema.org/draft/2020-12/json-schema-validation.html

qsv supports a custom format - `currency`. This format will only accept a valid currency, defined as:

 1. ISO Currency Symbol (optional): This is the ISO 4217 three-character code or currency symbol
    (e.g. USD, EUR, JPY, $, €, ¥, etc.)
 2. Amount: This is the numerical value of the currency. More than 2 decimal places are allowed.
 3. Formats: Valid currency formats include:
      Standard: $1,000.00 or USD1000.00
      Negative amounts: ($100.00) or -$100.00
      Different styles: 1.000,00 (used in some countries for euros)

qsv also supports two custom keywords - `dynamicEnum` and `uniqueCombinedWith`.

dynamicEnum
===========
`dynamicEnum` allows for dynamic validation against a reference CSV file.
It can be used to validate against a set of values unknown at the time of schema creation or
when the set of valid values is dynamic or too large to hardcode into the JSON Schema with `enum`.
The reference CSV file can be local or a URL (http/https, dathere & ckan schemes supported).
The "dynamicEnum" value has the form:

  // qsvlite binary variant only supports URIs which can be files on the local filesystem
  // or remote files (http and https schemes supported)
  dynamicEnum = "URI|colname" where colname is the column name or column index (0-based)

    // use data.csv from the current working directory; use the 1st column for validation
    dynamicEnum = "data.csv"

    // use data.csv in /lookup_dir directory; use the column "Agency" for validation
    dynamicEnum = "/lookupdir/data.csv|Agency"

    // get data.csv; use the 3rd column for validation (2 as the col index is 0-based)
    dynamicEnum = "https://example.com/data.csv|2"

  // on other qsv binary variants, dynamicEnum has expanded caching functionality
  dynamicEnum = "[cache_name;cache_age]|URI|colname" where cache_name and cache_age are optional

    // use data.csv from current working directory; cache it as data with a default
    // cache age of 3600 seconds i.e. the cached data.csv expires after 1 hour
    dynamicEnum = "data.csv"

    // get data.csv; cache it as custom_name, cache age 600 seconds
    dynamicEnum = "custom_name;600|https://example.com/data.csv"

    // get data.csv; cache it as data, cache age 800 seconds
    dynamicEnum = ";800|https://example.com/data.csv"

    // get the top matching result for nyc_neighborhoods (signaled by trailing ?),
    // cache it as nyc_neighborhood_data.csv (NOTE: cache name is required when using CKAN scheme)
    // with a default cache age of 3600 seconds
    // be sure to set --ckan-api, otherwise it will default to datHere's CKAN (data.dathere.com)
    dynamicEnum = "nyc_neighborhood_data|ckan:://nyc_neighborhoods?"

    // get CKAN resource with id 1234567, cache it as resname, 3600 secs cache age
    // note that if the resource is a private resource, you'll need to set --ckan-token
    dynamicEnum = "resname|ckan:://1234567"

    // same as above but with a cache age of 100 seconds; use the borough column for validation
    dynamicEnum = "resname;100|ckan:://1234567|borough

    // get us_states.csv from datHere lookup tables
    dynamicEnum = "dathere://us_states.csv"

If colname is not specified, the first column of the CSV file is read and used for validation.

Values are compared as text, so `dynamicEnum` works on integer and number columns too (`1` in
the data matches `1` in the reference file). In a boolean column, a cell matches either spelling
of its value (`true` or `1`, `false` or `0`). Empty cells are not looked up: whether they are
allowed is up to the column's `type` (e.g. ["string", "null"]).

uniqueCombinedWith
==================
`uniqueCombinedWith` allows you to validate that combinations of values across specified columns
are unique. It can be used with either column names or column indices (0-based). For example:

    // Validate that combinations of name and email are unique
    uniqueCombinedWith = ["name", "email"]

    // Validate that combinations of columns at indices 1 and 2 are unique
    uniqueCombinedWith = [1, 2]

    // Validate that the combinations of named and indexed columns are unique
    uniqueCombinedWith = ["name", 2]

Every listed column must exist: a name missing from the CSV header, or an index past its last
column, stops validation with an error. So does an index whose header name a later column
repeats, as the row then holds only the later column's value.

When a duplicate combination is found, the validation will fail and the error message will indicate
which columns had duplicate combinations (named columns first, then indexed columns). The invalid
records will be written to the .invalid file, while valid records will be written to the .valid file.
Rows are checked in file order, so the first row with a combination is valid and its later
duplicates are invalid. To keep that order, a schema using `uniqueCombinedWith` is validated
on a single thread.

`uniqueCombinedWith` complements the standard `uniqueItems` keyword, which can only validate
uniqueness across a single column.

-------------------------------------------------------

You can create a JSON Schema file from a reference CSV file using the `qsv schema` command.
Once the schema is created, you can fine-tune it to your needs and use it to validate other CSV
files that have the same structure.

Be sure to select a "training" CSV file that is representative of the data you want to validate
when creating a schema. The data types, domain/range and regular expressions inferred from the
reference CSV file should be appropriate for the data you want to validate.

Typically, after creating a schema, you should edit it to fine-tune each field's inferred
validation rules.

For example, if we created a JSON schema file called "reference.schema.json" using the `schema` command.
And want to validate "mydata.csv" which we know has validation errors, the output files from running
`qsv validate mydata.csv reference.schema.json` are:

  * mydata.csv.valid
  * mydata.csv.invalid
  * mydata.csv.validation-errors.tsv

With an exit code of 1 to indicate a validation error.

If we validate another CSV file, "mydata2.csv", which we know is valid, there are no output files,
and the exit code is 0.

If piped from stdin, the filenames will use `stdin.csv` as the base filename. For example:
  `cat mydata.csv | qsv validate reference.schema.json`

   * stdin.csv.valid
   * stdin.csv.invalid
   * stdin.csv.validation-errors.tsv


JSON SCHEMA SCHEMA VALIDATION SUBMODE:
---------------------------------------
`validate` also has a `schema` subcommand to validate JSON Schema files themselves. E.g.
     `qsv validate schema myjsonschema.json`
     // ignore format validation
     `qsv validate schema --no-format-validation myjsonschema.json`
     // check that its patterns compile with the fancy regex engine
     `qsv validate schema --fancy-regex myjsonschema.json`
The schema is compiled with the same options as JSON Schema validation mode, so qsv's custom
"currency" format is recognized and the regex options apply.

RFC 4180 VALIDATION MODE:
========================

If run without a JSON Schema file, the CSV is validated for RFC 4180 CSV standard compliance
(see https://github.com/dathere/qsv#rfc-4180-csv-standard).

It also confirms if the CSV is UTF-8 encoded.

For both modes, returns exit code 0 when the CSV file is valid, exitcode > 0 otherwise.
If all records are valid, no output files are produced.

Examples:

  # Validate a CSV file. Use this to check if a CSV file is readable by qsv.
  qsv validate data.csv

  # Quarantine rows with the wrong number of columns instead of aborting.
  # Well-formed rows go to data.csv.valid; ragged rows go to data.csv.invalid.
  qsv validate --split-ragged data.csv

  # Skip '#'-prefixed comment lines while quarantining ragged rows.
  # validate has no parser-config options of its own, but it honors the global
  # QSV_COMMENT_CHAR environment variable in BOTH validation modes. Commented lines
  # (including a commented header) are skipped - they are NOT written to the .valid file.
  QSV_COMMENT_CHAR='#' qsv validate --split-ragged data.tsv

  # For CSV dialects validate cannot express (custom quote/escape characters,
  # preamble/epilogue lines, non-UTF-8 encodings), normalize with `qsv input` FIRST,
  # then validate the normalized output. Note that `qsv input` aborts on ragged rows,
  # so this ordering only works on files that are not ragged.
  qsv input --quote "'" --escape '\' --comment '#' data.tsv -o normalized.csv
  qsv validate normalized.csv

  # Validate a TSV file against a JSON Schema
  qsv validate data.tsv schema.json

  # Validate multiple CSV files using various dialects against a JSON Schema
  qsv validate data1.csv data2.tab data3.ssv schema.json

  # Validate all CSV files in a directory against a JSON Schema
  qsv validate /path/to/csv_directory schema.json

  # Validate CSV files listed in a '.infile-list' file against a JSON Schema
  qsv validate files.infile-list schema.json

For more examples, see the tests included in this file (denoted by '#[test]') or see
https://github.com/dathere/qsv/blob/master/tests/test_validate.rs.
See also https://github.com/dathere/qsv/wiki/Validation-and-Schema#validate

Usage:
    qsv validate schema [options] [<json-schema>]
    qsv validate [options] [<input>...]
    qsv validate [options] [<input>] <json-schema>
    qsv validate --help

Validate arguments:
    <input>...                 Input CSV file(s) to validate. If not provided, will read from stdin.
                               If input is a directory, all files in the directory will be validated.
                               If the input is a file with a '.infile-list' extension, the file will
                               be read as a list of input files. If the input are snappy-compressed
                               files(s), it will be decompressed automatically.
                               Extended Input Support is only available for RFC 4180 validation mode.
    <json-schema>              JSON Schema file to validate against. If not provided, `validate`
                               will run in RFC 4180 validation mode. The file can be a local file
                               or a URL (http and https schemes supported).

Validate options:
    --trim                     Trim leading and trailing whitespace from fields before validating.
    --no-format-validation     Disable JSON Schema format validation. Ignores all JSON Schema
                               "format" keywords (e.g. date,email, uri, currency, etc.). This is
                               useful when you want to validate the structure of the CSV file
                               w/o worrying about the data types and domain/range of the fields.
                               Without this option, a "format" that qsv does not know (e.g. a
                               typo like "emial") is not checked, and a warning names it.
    --fail-fast                Stops on first error.
    --valid <suffix>           Valid record output file suffix. [default: valid]
    --invalid <suffix>         Invalid record output file suffix. [default: invalid]
    --split-ragged             Opt-in mode: instead of aborting on the first row with the wrong
                               number of columns (a "ragged" row), write well-formed rows to the
                               '<input>.<valid>' file and the ragged rows to the '<input>.<invalid>'
                               file, with a report appended to '<input>.validation-errors.tsv'.
                               Returns a non-zero exit code when any ragged row is found.
                               Only column-count mismatches are diverted; malformed quoting and
                               non-UTF-8 data still abort validation. Works in both RFC 4180 and
                               JSON Schema validation modes. The split files are written next to
                               each input file, so this is intended for on-disk file input(s).
                               A compressed input keeps its full name (data.csv.sz.valid). In RFC
                               4180 mode, which checks every entry in a zip archive, an entry is
                               named for both (data.zip.data.csv.valid; data.zip.sub/x.csv.valid
                               for an entry in a folder). Piped stdin's are 'stdin.csv.*' in the
                               current directory. If any split file would be written twice, or
                               would overwrite an input, nothing is written.
    --json                     When validating without a JSON Schema, return the RFC 4180 check
                               as a JSON file instead of a message.
    --pretty-json              Same as --json, but pretty printed.
    --valid-output <file>      Change validation mode behavior so if ALL rows are valid, to pass it to
                               output, return exit code 1, and set stderr to the number of valid rows.
                               Setting this will override the default behavior of creating
                               a valid file only when there are invalid records.
                               To send valid records to stdout, use `-` as the filename.
    -j, --jobs <arg>           The number of jobs to run in parallel.
                               When not set, the number of jobs is set to the
                               number of CPUs detected.
    -b, --batch <size>         The number of rows per batch to load into memory,
                               before running in parallel. Automatically determined
                               for CSV files with more than 50000 rows.
                               Set to 0 to load all rows in one batch.
                               Set to 1 to force batch optimization even for files with
                               less than 50000 rows. [default: 50000]

                               FANCY REGEX OPTIONS:
    --fancy-regex              Use the fancy regex engine instead of the default regex engine
                               for validation.
                               The fancy engine supports advanced regex features such as
                               lookaround and backreferences, but is not as performant as
                               the default regex engine which guarantees linear-time matching,
                               prevents DoS attacks, and is more efficient for simple patterns.
    --backtrack-limit <limit>  Set the approximate number of backtracking steps allowed.
                               This is only used when --fancy-regex is set.
                               [default: 1000000]

                               OPTIONS FOR BOTH REGEX ENGINES:
    --size-limit <mb>          Set the approximate size limit, in megabytes, of a compiled regex.
                               [default: 50]
    --dfa-size-limit <mb>      Set the approximate capacity, in megabytes, of the cache of transitions
                               used by the engine's lazy Discrete Finite Automata.
                               [default: 10]

    --offline                  Do not resolve "$ref"s to schemas outside the JSON Schema file,
                               whether they are URLs or local files; a schema that has them
                               fails to compile. Use this with JSON Schemas you do not trust.
                               The JSON Schema file itself and dynamicEnum lookups are still
                               loaded as usual.
    --timeout <seconds>        Timeout for downloading json-schemas on URLs and for
                               'dynamicEnum' lookups on URLs. If 0, no timeout is used.
                               [default: 30]
    --cache-dir <dir>          The directory to use for caching downloaded dynamicEnum resources.
                               If the directory does not exist, qsv will attempt to create it.
                               If the QSV_CACHE_DIR envvar is set, it will be used instead.
                               Not available on qsvlite.
                               [default: ~/.qsv-cache]
    --ckan-api <url>           The URL of the CKAN API to use for downloading dynamicEnum
                               resources with the "ckan://" scheme.
                               If the QSV_CKAN_API envvar is set, it will be used instead.
                               Not available on qsvlite.
                               [default: https://data.dathere.com/api/3/action]
    --ckan-token <token>       The CKAN API token to use. Only required if downloading
                               private resources.
                               If the QSV_CKAN_TOKEN envvar is set, it will be used instead.
                               Not available on qsvlite.

                                EMAIL VALIDATION OPTIONS:
    --email-required-tld        Require the email to have a valid Top-Level Domain (TLD)
                                (e.g. .com, .org, .net, etc.).
                                e.g. "john.doe@example" is VALID if this option is NOT set.
    --email-display-text        Allow display text in emails.
                                e.g. "John Doe <john.doe@example.com>" is INVALID if this option is NOT set.
    --email-min-subdomains <n>  Minimum number of subdomains required in the email.
                                e.g. "jdoe@example.com" is INVALID if this option is set to 3,
                                but "jdoe@sub.example.com" is VALID.
                                [default: 2]
    --email-domain-literal      Allow domain literals in emails.
                                e.g. "john.doe@[127.0.0.1]" is VALID if this option is set.

Common options:
    -h, --help                 Display this message
    -n, --no-headers           When set, the first row will not be interpreted
                               as headers. It will be validated with the rest
                               of the rows. Otherwise, the first row will always
                               appear as the header row in the output.
                               Note that this option is only valid when running
                               in RFC 4180 validation mode as JSON Schema validation
                               requires headers.
    -d, --delimiter <arg>      The field delimiter for reading CSV data.
                               Must be a single character.
    -p, --progressbar          Show progress bars. Not valid for stdin.
    -q, --quiet                Do not display validation summary message.
```
## qsv viz

```text
Generate charts/maps from CSV data using the plotly charting library.

Produces a self-contained, interactive HTML chart - the plotly.js runtime is embedded, so
charts work offline. Tile basemaps (`viz map`, `viz choropleth --map`) are the exception:
they fetch tiles over the network at view time. Titles and labels are plain text; LaTeX is
not typeset. With a build that includes the `viz_static` feature, charts can also be exported
as static PNG/SVG/PDF/JPEG/WebP. That needs Chrome/Chromium plus a matching chromedriver at
runtime (Firefox is NOT supported). qsv looks for chromedriver in ~/.local/bin and on your
PATH; set WEBDRIVER_PATH to the chromedriver binary to override, and BROWSER_PATH to point at
a non-default Chrome/Chromium. The chromedriver MAJOR version must match your Chrome - get a
matched pair at https://googlechromelabs.github.io/chrome-for-testing/

Set QSV_VIZ_CDN to load plotly.js from its CDN (~1.9MB smaller, but the page then needs the
network to be VIEWED). Set QSV_VIZ_NO_COMPRESS for plain-text HTML that works on pre-2023
browsers and strict-CSP embeds. Progress is shown on stderr, auto-hidden when stderr is not a
terminal, and disabled by setting QSV_PROGRESSBAR to a falsy value. For all of the above, see
https://github.com/dathere/qsv/wiki/Visualization#output-and-file-size
A `smart` HTML Data Schematic embeds a small qsv-clientd bridge (see --no-daemon-bridge):
QSV_CLIENTD_PORT sets the daemon port it probes (default 14470), and QSV_VIZ_NO_DAEMON
leaves it, and the input fingerprint, out.

The output format is inferred from the --output file extension (.html is the default).
Interactive HTML is written to stdout when --output is not given; image formats always
require --output. Use --open to view the result in your default browser/viewer.

Chart types (subcommands):
    smart       Auto-dashboard (Data Schematic) - picks a chart per column from the
                dataset's statistics & frequency distribution. No --x/--y needed.
    bar         --x = category column, --y = value column.
    line        --x = x column, --y = y column.
    scatter     --x = x column, --y = y column.
    scatter3d   --x, --y, --z = three numeric columns.
    histogram   --x = numeric column to bin.
    box         --y = value column, optional --x = group column.
    violin      Box plot plus a KDE density curve revealing the distribution's shape
                (modes, shoulders). Same inputs as box.
    pie         --x = label column, optional --y = value column.
    funnel      Stage-by-stage drop-off. --x = stage column, optional --y = value column
                (counts stage occurrences when omitted). Stages keep the order they first
                appear in the file, so the rows define the pipeline. --area draws it as a
                funnel area instead: stacked sections sized by each stage's share.
    heatmap     Correlation matrix of numeric columns (default; subset with --cols), or a
                category x category pivot with --x/--y/--z.
    contour     2D density contour of --x and --y, binned into a --bins x --bins grid.
    candlestick Financial OHLC. --x = date column, plus --ohlc-open/--high/--low/--close.
    ohlc        Financial OHLC bars (same inputs as candlestick).
    sankey      Flow diagram. --source, --target, optional --value column.
    radar       Polar/radar chart of numeric --cols, optional --series per trace.
    barpolar    Polar bar chart (a wind rose): one bar per --x category around the
                circle, clockwise from the top, as long as the --y total (rows are
                counted when --y is omitted; see --agg). Compass points (N, NE, NNE...)
                sit at their bearings on a full 8- or 16-point rose. Other categories
                get evenly spaced slots in the order they first appear in the file
                (numeric ones sort ascending); --degrees places numeric angles at their
                true bearing instead. --series stacks one colored segment per value.
    ternary     Ternary (triangle) plot of three parts of a whole: --cols names exactly
                3 numeric columns (a, b, c), and each row is drawn at its shares
                a/(a+b+c), b/(a+b+c) and c/(a+b+c). Optional --series, or --color/--size.
                Rows with a blank, non-numeric or negative part, or parts summing to 0,
                are skipped (and counted on stderr).
                The first column's corner is the top, the second's bottom-left and the
                third's bottom-right.
    treemap     Part-to-whole hierarchy as nested tiles. --cols = 2+ dimension columns
                (levels, outermost first), optional --value and --agg.
    sunburst    Same inputs as treemap, as concentric rings. Better for deep hierarchies.
    icicle      Same inputs as treemap, as level-aligned stacked bars. Good for deep,
                wide hierarchies.
    splom       Scatter-plot matrix: every pair of numeric --cols in a grid, with each
                column's distribution on the diagonal (default: all numeric).
    parcats     Parallel categories: ribbons showing how rows flow across the
                categorical --cols (best with 3-4). Complements sankey, which takes
                2 columns.
    parcoords   Parallel coordinates: one line per row across the numeric --cols
                (default: all numeric), with an optional numeric --color column.
                The numeric twin of parcats. Drag along an axis to filter rows.
    map         Point map (or --density heatmap) on MapLibre tile basemaps. Pick the
                coordinate columns with the lat/lon options below.
    geo         Point map on a projection basemap - coastlines/land/countries, no tiles
                and no token. Same lat/lon options as `map`, plus --projection.
    choropleth  Fill whole regions (countries, US states, or custom GeoJSON areas) by a
                value. --locations names the region-code column, --value/--agg the
                measure (row counts if omitted). Defaults to a token-free projection
                basemap; --map switches to MapLibre tiles.

`qsv viz smart` builds a DATA SCHEMATIC - a single, self-contained rendering of a dataset's
schema and statistics in which every claim shown is checkable against the data it describes.
The format is specified in docs/DATA_SCHEMATIC.md and is tool-neutral. A DETERMINISTIC half
(statistics and heuristics - reproducible, offline, no tokens) picks the panels and scales the
axes; a SEMANTIC half (an optional LLM-inferred Data Dictionary, see the dictionary option)
supplies what the fields MEAN. Both halves show their work, and the dictionary is a
hand-editable sidecar, so a Data Steward can correct anything the model proposed.

It reuses qsv's stats and frequency caches (the first run computes & caches stats; later runs
are fast) and auto-picks panels, so no --x/--y is needed:

  Per-column panels flow in a grid below the overview rows (see --grid-cols):
    continuous numeric -> violin or box plot; low-cardinality/boolean -> frequency bar;
    confirmed-bimodal -> histogram (needs --smarter). ID-like (near-unique) and all-empty
    columns are skipped and reported.

  Overview panels each lead the Data Schematic on their own full-width row: a KPI "big
  number" strip, a declared pipeline funnel or bridge, a correlation heatmap with a
  drill-down scatter/contour/3D triple, a time-series line, a part-to-whole hierarchy, and
  a geographic map plus region choropleth. Each is drawn only when the data supports it;
  which panel is chosen, and why, is documented at
  https://github.com/dathere/qsv/wiki/Visualization#smart-panels

Examples:
  # Data Schematic for a dataset, opened in the browser
  qsv viz smart data.csv --open

  # Data Schematic, at most 6 panels in a 3-column grid, top-5 categories per bar
  qsv viz smart data.csv --max-charts 6 --grid-cols 3 --limit 5 -o dashboard.html

  # Semantics-guided Data Schematic with a browsable Data Dictionary drawer
  qsv viz smart data.csv --dictionary infer --dict-info -o dashboard.html

  # Richer Data Schematic: extra distribution-shape stats plus pairwise associations
  qsv viz smart data.csv --smarter --bivariate -o dashboard.html

  # Aggregate (sum) sales by region into a titled bar chart, opened in the browser
  qsv viz bar sales.csv --x region --y amount --agg sum --title "Sales by region" --open

  # Scatter plot with a separate series (trace) per category
  qsv viz scatter data.csv --x age --y income --series gender -o scatter.html

  # Bubble scatter: marker size by population, marker color by a numeric score
  qsv viz scatter data.csv --x gdp --y life_exp --size population --color score -o bubble.html

  # Gapminder bubble animation: one bubble per region moving over time
  qsv viz scatter regions.csv --x gdp_index --y wellbeing_index --size population_m --series region --slider month_date -o gapminder.html

  # 3D scatter of three numeric columns, colored by a fourth
  qsv viz scatter3d data.csv --x length --y width --z height --color weight -o scatter3d.html

  # 2D density contour of two numeric columns with a 40x40 grid
  qsv viz contour data.csv --x height --y weight --bins 40 -o contour.html

  # Histogram of a numeric column with 30 bins
  qsv viz histogram data.csv --x value --bins 30 -o hist.html

  # Box plot grouped by a category, every sample point overlaid, exported to PNG
  qsv viz box data.csv --y measurement --x group --box-points all -o box.png

  # Violin plot (KDE density curve + inner box) of a value column grouped by a category
  qsv viz violin data.csv --y measurement --x group -o violin.html

  # Pie chart of category proportions (counts), as a donut
  qsv viz pie data.csv --x category --donut -o pie.html

  # Funnel of a pipeline whose stages are ROWS (stage column + amount column)
  qsv viz funnel pipeline.csv --x stage --y amount -o funnel.html

  # The same pipeline as a funnel area, each section sized by its share of the total
  qsv viz funnel pipeline.csv --x stage --y amount --area -o funnelarea.html

  # Correlation heatmap over all numeric columns
  qsv viz heatmap data.csv -o corr.html

  # Heatmap pivot: average value per (region x product)
  qsv viz heatmap sales.csv --x region --y product --z amount -o pivot.html

  # Candlestick chart from a date column and OHLC price columns
  qsv viz candlestick prices.csv --x date --ohlc-open open --high high --low low --close close -o ohlc.html

  # Sankey flow diagram of source -> target weighted by value
  qsv viz sankey flows.csv --source from --target to --value weight -o sankey.html

  # Treemap of part-to-whole sales by region then category, sized by amount
  qsv viz treemap sales.csv --cols region,category --value amount --agg sum -o treemap.html

  # Sunburst of a deep 3-level web-traffic hierarchy, sized by row count
  qsv viz sunburst web.csv --cols source,campaign,landing_page -o sunburst.html

  # Radar chart comparing numeric metrics, one trace per team
  qsv viz radar teams.csv --cols speed,power,range,accuracy --series team -o radar.html

  # Wind rose: observation counts per compass direction, stacked by speed band
  qsv viz barpolar wind.csv --x direction --series speed_band -o windrose.html

  # Wind rose from bearings in degrees, each bar at its true angle
  qsv viz barpolar wind.csv --x bearing_deg --degrees -o windrose.html

  # Ternary plot of soil texture (sand/silt/clay shares), colored by organic matter
  qsv viz ternary soils.csv --cols sand,silt,clay --color organic_pct -o ternary.html

  # Parallel coordinates across four measures, each line colored by price
  qsv viz parcoords cars.csv --cols mpg,horsepower,weight,acceleration --color price -o parcoords.html

  # Point map of earthquakes, marker color by magnitude and size by depth
  qsv viz map quakes.csv --lat lat --lon lon --color magnitude --size depth -o map.html

  # Density heatmap of the same points, on a light Carto basemap
  qsv viz map quakes.csv --lat lat --lon lon --density --style carto-positron -o heat.html

  # Projection map of earthquakes (token-free, offline), marker color by magnitude
  qsv viz geo quakes.csv --lat lat --lon lon --color magnitude --projection natural-earth -o geo.html

  # Choropleth coloring countries (ISO-3 codes) by a summed measure
  qsv viz choropleth gdp.csv --locations iso3 --value gdp --agg sum -o choropleth.html

  # US-state choropleth of row counts per state (2-letter state codes)
  qsv viz choropleth orders.csv --locations state --location-mode usa-states -o states.html

  # US counties with no GeoJSON supplied - boundaries fetched from Census TIGERweb
  qsv viz choropleth complaints.csv --locations fips --geojson auto -o counties.html

  # ...as a per-capita RATE, with the population fetched from the Census Data API
  qsv viz choropleth complaints.csv --locations fips --geojson auto --denominator census -o rate.html

  # Custom GeoJSON regions on a MapLibre tile basemap, matched by a feature id
  qsv viz choropleth counties.csv --locations fips --value pop --map --geojson counties.json --feature-id-key id -o counties.html

  # Point-in-polygon: bin lat/lon points into custom GeoJSON regions by count (no geocode)
  qsv viz choropleth quakes.csv --lat lat --lon lon --geojson prefectures.geojson --feature-id-key properties.id -o by_pref.html

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_viz.rs.
See also https://github.com/dathere/qsv/wiki/Visualization

Usage:
    qsv viz smart       [options] <input>
    qsv viz bar         [options] <input>
    qsv viz line        [options] <input>
    qsv viz scatter     [options] <input>
    qsv viz scatter3d   [options] <input>
    qsv viz histogram   [options] <input>
    qsv viz box         [options] <input>
    qsv viz violin      [options] <input>
    qsv viz pie         [options] <input>
    qsv viz funnel      [options] <input>
    qsv viz heatmap     [options] <input>
    qsv viz contour     [options] <input>
    qsv viz candlestick [options] <input>
    qsv viz ohlc        [options] <input>
    qsv viz sankey      [options] <input>
    qsv viz radar       [options] <input>
    qsv viz barpolar    [options] <input>
    qsv viz ternary     [options] <input>
    qsv viz map         [options] <input>
    qsv viz geo         [options] <input>
    qsv viz choropleth  [options] <input>
    qsv viz treemap     [options] <input>
    qsv viz sunburst    [options] <input>
    qsv viz icicle      [options] <input>
    qsv viz splom       [options] <input>
    qsv viz parcats     [options] <input>
    qsv viz parcoords   [options] <input>
    qsv viz --help


viz options:
    -x, --x <col>          Column for the x-axis / category / bin / group.
    -y, --y <col>          Column for the y-axis / value.
    -z, --z <col>          The z column: a heatmap pivot value (with --x and --y), or
                           the third numeric axis for scatter3d.
    --cols <cols>          Columns to use. For heatmap: numeric columns for the
                           correlation matrix (default: all numeric). For radar:
                           the numeric axes to plot. For treemap/sunburst/icicle: the
                           categorical dimensions that form the hierarchy levels,
                           outermost first (e.g. region,category,subcategory).
                           For splom: the numeric columns to cross-plot (default:
                           all numeric). For parcats: the categorical dimensions
                           to flow across (best with 3-4). For parcoords: the
                           numeric axes, in order (default: all numeric). For
                           ternary: exactly 3 numeric columns, the a, b and c parts.
    --series <col>         Column to split into multiple series (one trace per
                           distinct value). Applies to bar, line, scatter, scatter3d,
                           radar, barpolar (stacked), ternary, map and geo.
    --color <col>          For scatter/scatter3d/ternary/map/geo: a numeric column to encode as
                           marker color (a continuous colorscale with a colorbar). For
                           categorical coloring, use the --series option instead. Cannot
                           be combined with --series. In map density mode, this column is
                           the heatmap weight. For parcoords: the numeric column that
                           colors each line (default: the first axis).
    --size <col>           For scatter/scatter3d/ternary/map/geo: a numeric column to encode as
                           marker size, producing a bubble chart (values are rescaled to
                           a readable pixel range). Cannot be combined with --series,
                           EXCEPT on an animated scatter (see the --slider option), where
                           the --series column names the entity and this column is the
                           third data variable. In map density mode, this column is the
                           heatmap weight.
    --donut                Render a pie chart as a donut (with a center hole).
    --area                 For funnel: draw a funnel area, whose stacked sections are sized
                           by each stage's share of the total and labeled with its value
                           and percent of the total, instead of bars labeled with the
                           conversion from the previous stage. Its outline always narrows,
                           so a stage larger than the one before it can't show as growth;
                           a warning names the first such stage.
    --degrees              For barpolar: read --x as an angle in degrees (0 = north,
                           clockwise) and draw each bar at that angle, so gaps in the
                           data stay gaps. Without it, each distinct --x value gets an
                           evenly spaced slot, which suits hours, months and complete
                           degree bins (compass names are placed by bearing either way).
    --ohlc-open <col>      Open-price column for candlestick/ohlc charts.
    --high <col>           High-price column for candlestick/ohlc charts.
    --low <col>            Low-price column for candlestick/ohlc charts.
    --close <col>          Close-price column for candlestick/ohlc charts.
    --source <col>         Source node column for a sankey diagram.
    --target <col>         Target node column for a sankey diagram.
    --value <col>          Flow value column for a sankey diagram. When omitted,
                           each row counts as a flow of 1. For treemap/sunburst/icicle:
                           a numeric measure summed per sector (when omitted, each
                           row counts as 1). For smart: the numeric column its
                           region map aggregates per region (see the agg option),
                           in place of the dictionary's additive measure.
    --sankey-value-order   Order sankey nodes by total flow (largest at the top of each
                           column) instead of plotly's default crossing-minimizing "snap"
                           order. Either way the chart carries an on-screen "node order"
                           button to flip between the two layouts, and link ribbons are
                           always colored by their source node. Applies to the `sankey`
                           chart AND the `smart` Data Schematic flow panel.
    --bins <n>             Number of bins. For histogram: bins along the x-axis
                           (default: auto). For contour: the per-axis resolution of
                           the density grid (default: 20).
    --agg <fn>             How to combine values. For bar/line, aggregate the y values
                           when the x value repeats: one of sum, mean, count, min, max.
                           For barpolar, the same per category (and series): sum by
                           default, and only count when the y column is omitted.
                           For treemap/sunburst/icicle, only the additive aggregations
                           apply: count (the default) or sum (which requires --value).
                           For choropleth, how rows sharing a region are combined: sum
                           when --value is given, else count; pass mean for an intensive
                           measure (a density, rate, index or per-capita figure), since
                           summing those is meaningless and the count/sum hover's "share
                           of total" line would be too. On a bubble animation (see the
                           slider option), it collapses each entity x frame cell to a
                           single bubble and defaults to mean, the cell centroid; count is
                           rejected there, since a row count is not a position. For smart
                           (with a GeoJSON), how its region map combines the value column
                           per region: sum (the default, and the only one that also gets a
                           rate panel when a denominator is available), mean, min or max;
                           count keeps the row-count map even when every region has the
                           same number of rows, and takes no value column.
    --box-points <mode>    Which sample points to draw alongside a box or violin. Reading
                           the raw values lets plotly render true Tukey whiskers (1.5*IQR)
                           with the points beyond the fences as outliers. One of:
                           outliers (only the outliers), all (every point, jittered),
                           suspected (mark suspected outliers), none (no points, but
                           still real Tukey whiskers). Applies to `viz box`, `viz violin`
                           AND `viz smart`. For `viz box` the default is outliers; for
                           `viz smart` an explicit mode OVERRIDES a size-based heuristic
                           and is applied to every panel. `none` only hides a violin's
                           points, since its KDE needs the values anyway; the cache-only
                           escape hatch is `--violin off` with this set to none. For the
                           heuristic's thresholds, see
                           https://github.com/dathere/qsv/wiki/Visualization#distribution-panels

map options:
    --lat <col>            Latitude column for a map (decimal degrees, -90 to 90).
    --lon <col>            Longitude column for a map (decimal degrees, -180 to 180).
    --text <col>           Column whose value labels each point on hover.
    --density              Render a density heatmap (DensityMap) instead of points.
                           Weighted by the --color or --size column when given, else by
                           a uniform weight. Cannot be combined with --series.
    --style <name>         MapLibre basemap style (all render without an access token):
                           open-street-map (the default), carto-positron,
                           carto-darkmatter, carto-voyager, white-bg, basic, streets,
                           outdoors, light, dark, satellite, satellite-streets. The three
                           carto styles also have label-free "-nolabels" variants (e.g.
                           carto-positron-nolabels) that keep basemap place names from
                           competing with a dense data overlay.
                           [default: open-street-map]

geo options:
    --projection <name>    Map projection for `viz geo`. One of: natural-earth (the
                           default), mercator, orthographic, equirectangular,
                           albers-usa, robinson, winkel-tripel, mollweide, hammer,
                           azimuthal-equal-area. `viz geo` also reuses the lat, lon,
                           text, color, size and series options from `map`.
                           [default: natural-earth]

choropleth options:
    --locations <col>      Column holding the region key for each row (an ISO-3 country
                           code, a 2-letter US state code, a country name, or a GeoJSON
                           feature id, per --location-mode). With --geocode, this instead
                           names a place-name column to forward-geocode into region codes.
    --location-mode <m>    How --locations values are matched to regions. One of: iso3
                           (ISO-3166-1 alpha-3 country codes), usa-states (2-letter US
                           state codes), country-names (full country names), geojson-id
                           (match a --geojson feature id). Defaults to geojson-id when
                           a --geojson source is given (without --geocode), else iso3.
    --color-scale <name>   Colorscale for the region fill. One of: viridis (the default),
                           cividis, greys, greens, blues, reds, ylgnbu, ylorrd, bluered,
                           rdbu, portland, electric, jet, hot, blackbody, earth, picnic,
                           rainbow. [default: viridis]
    --map                  Render on a token-free MapLibre tile basemap (a ChoroplethMap)
                           instead of the default projection basemap. Requires --geojson;
                           feature-id-key defaults to id. Reuses --style for the basemap.
    --geojson <src>        Custom region polygons: a local file path, an http(s) URL to a
                           GeoJSON FeatureCollection, or a shortcut name from the
                           QSV_GEOJSON_SHORTCUTS env var (whose id sets --feature-id-key
                           when you don't pass one). Use `auto` (or `census`) to fetch US
                           boundaries from Census TIGERweb automatically; force a layer
                           with census:state, census:county, census:zcta, census:tract or
                           census:place (incorporated places AND CDPs), and pin a vintage
                           with @<year>, e.g. census:county@2021. That path sets
                           feature-id-key to properties.GEOID (properties.STUSAB for a
                           column of USPS state codes; full state names are matched to it)
                           and caches under ~/.qsv-cache for 30 days
                           (QSV_VIZ_BOUNDARY_CACHE_TTL_DAYS); it reads the codes from
                           the --locations column, so in `viz smart` it needs a --dictionary
                           naming the region column. A column of city/place NAMES also
                           needs --geocode. Required for --map and for the geojson-id
                           location mode; with --lat/--lon it instead enables
                           point-in-polygon binning. See
                           https://github.com/dathere/qsv/wiki/Visualization#census-boundaries
    --feature-id-key <k>   Property path in each GeoJSON feature whose value matches an
                           entry in the locations column, or that labels each binned
                           region (e.g. id, properties.fips). With --geojson auto the
                           key is set for you; an explicit key overrides it, except that
                           county or place names resolve to GEOIDs and refuse a key
                           that does not carry them. [default: id]
    --feature-name-key <k>  GeoJSON property path whose value is shown as the
                           human-readable region label in choropleth hover (e.g.
                           properties.name). When omitted, common name keys are
                           auto-detected; falls back to the feature id when absent.
    --check-geojson-key    Diagnostic mode. Instead of rendering, score EVERY candidate
                           feature-id path in --geojson against the distinct values of the
                           locations column and print them ranked by overlap - use it when
                           a region map shades nothing while exiting 0. Requires --geojson
                           and --locations, with a concrete source for the former (path,
                           URL or shortcut); every automatic Census spec is refused, since
                           automatic resolution picks the key itself.
    --denominator-key <k>  GeoJSON property path holding each region's DENOMINATOR (e.g.
                           properties.POP2020), addressed like --feature-id-key. Turns a
                           raw-count region map into a RATE map: in `viz choropleth` the
                           map itself becomes the rate; in `viz smart` a rate panel is
                           added BESIDE the count panel. Regions whose denominator is
                           missing or non-positive are excluded and reported; the per-region
                           scale (per 1,000 / 10,000 / 100,000 / 1,000,000 / 1,000,000,000)
                           is chosen automatically. See
                           https://github.com/dathere/qsv/wiki/Visualization#rate-maps
    --denominator-unit <u>
                           Unit the denominator values are IN, so qsv can convert and name
                           them. One of: m2, km2 (also spelled m², km², sqm, sqkm). Values
                           in m2 are converted to km², so the map reads "per km²". NEVER
                           inferred from a field name - real boundary files carry land area
                           in square METRES, which divided raw reads as "per 100,000
                           AREALAND" at approximately zero everywhere. Boundaries fetched by
                           `--geojson auto` declare their own units and need no flag.
    --denominator <col>    Column holding each region's DENOMINATOR, as an alternative to
                           reading it from the GeoJSON. Its value must be constant within a
                           region (it describes the region, not the row). `viz choropleth`
                           only, and only with a --locations region column - not with
                           the --geocode flag or lat/lon binning. Valid with the default count
                           aggregation and with --agg sum; the other aggregations are
                           already intensive, so a denominator is rejected there. In `viz
                           smart`, declare it in the data dictionary instead, via
                           x-qsv.denominator (see --dictionary).
                           The value `census` is RESERVED (a column of that name cannot be
                           used): it fetches US population from the Census Data API for a
                           per-capita rate with nothing supplied, and being a source rather
                           than a column it works on `viz smart` too. Region codes must be
                           5-digit county FIPS, 2-digit state FIPS, or 2-letter state codes.
                           The newest published ACS 5-year release is used and is always
                           stated beneath the map; pin one with @<year>, e.g. census@2019.
                           Uncovered regions are excluded and reported. Cached for 30 days
                           (QSV_VIZ_DENOMINATOR_CACHE_TTL_DAYS). REQUIRES a Census API key
                           in QSV_CENSUS_API_KEY - free at
                           https://api.census.gov/data/key_signup.html
    --geocode              Derive the region codes with qsv's geocode engine (needs a build
                           with the geocode feature): either reverse-geocode the lat/lon
                           points, or forward-geocode the locations name column. Only valid
                           with location modes iso3 or usa-states. `viz choropleth` also
                           reuses --value, --agg, --style and the lat/lon options.
                           Combined with `--geojson auto` it forward-geocodes a column of
                           city/place NAMES to their containing US county FIPS and fetches
                           those counties; lat/lon is REJECTED there, since reverse
                           geocoding finds the nearest populated place, not the containing
                           county. Each distinct name is a full engine lookup, so a column
                           with thousands of them resolves slowly; unresolvable names are
                           reported with a denser-index remedy.
    --geocode-country <col>
                           Column holding each row's expected country, as an ISO-3166-1
                           alpha-2 code (e.g. US, GB, BR). Without it a place-name search
                           spans every country, so US city names have resolved to Pakistan
                           and a point near a border takes the nearest FOREIGN place. Rows
                           whose match falls outside the hint are counted and reported,
                           never silently dropped. Country NAMES are not accepted. With
                           location-mode usa-states the country defaults to `us`. Applies to
                           both geocode sources.
    --geocode-admin1 <col>
                           Column holding each row's expected admin1 (state/province),
                           either as a qualified Geonames code (US.AL) or a bare subdivision
                           code (AL) qualified by the country. Narrows a place-name search
                           for names ambiguous on their own - there are dozens of US
                           Springfields. Spelled-out names are REJECTED: admin1 names match
                           by prefix, so `AL` would silently accept Alaska. Valid only with
                           a locations name column, not with lat/lon points.
    --region-state <col>   Column holding each row's state, for a --locations column of
                           county NAMES rather than codes. Accepts a USPS code (PA), a
                           2-digit state FIPS (42) or the full state name (Pennsylvania).
                           422 county names are carried by more than one county - Washington
                           County exists in 30 states - so without this, a column containing
                           any of them is refused rather than resolved to an arbitrary
                           state. `viz choropleth --geojson auto` only; in `viz smart` the
                           state column comes from the data dictionary. A county FIPS column
                           needs none of this.
    --no-snap              For point-in-polygon binning: do not snap at all - drop every
                           point that falls outside every region. By default an outside
                           point snaps to its nearest region when within the snap-distance
                           limit (see --snap-max-dist). Applies to both `viz choropleth` and
                           the `viz smart` GeoJSON choropleth panel; coverage is reported on
                           stderr and beneath the map either way.
    --snap-max-dist <km>   For point-in-polygon binning: the farthest (in km, an
                           equirectangular approximation) an outside point may snap to a
                           region's boundary; points with no region within it are dropped.
                           When omitted the cap is AUTO-DERIVED from the GeoJSON's median
                           region size and the lat/lon coordinate precision, clamped to
                           0.1-100 km; a fixed 10 km is used only when neither signal is
                           available. The coverage notes state the cap and how it was
                           derived. Pass a large value for effectively unbounded snapping;
                           cannot be combined with --no-snap. See
                           https://github.com/dathere/qsv/wiki/Visualization#point-in-polygon

smart options:
    --max-charts <n>       Maximum number of panels in the Data Schematic. 0 (the default)
                           means auto: draw every eligible column (up to 65), for both HTML
                           and static image export. Up to 8 cartesian panels render as one
                           typed subplot grid; beyond 8, HTML switches to an inline-div grid
                           and static export uses domain-positioned axes to fit one image.
                           Set a positive <n> to cap the panel count instead; eligible
                           columns beyond the cap are reported but not drawn. [default: 0]
    --grid-cols <n>        Number of columns in the Data Schematic grid for the per-column
                           distribution panels. Overview panels (map/geo, correlation,
                           time-series) always span the full width. [default: 2]
    --preview-threshold <n>  Row threshold for the interactive data viewer drawer of HTML
                           dashboards. Next to the row count in the metadata table, an
                           "(Explore)" link opens the underlying table in a bottom drawer
                           (with global, per-column and builder search) when the dataset has
                           at most <n> rows and ALL rows are embedded; above <n>, only the
                           first <n> rows are embedded and the link reads "(Preview)".
                           Embedded rows grow the HTML file, and browser memory, in
                           proportion to rows x columns. Set to 0 to disable the data viewer
                           entirely (no link, no embedded data). `smart` HTML only.
                           [default: 50000]
    --tour-steps <n>       How many chart panels the guided tour of a `smart` HTML dashboard
                           spotlights. This budgets the per-panel steps only - the
                           introduction, the Data Dictionary drawer chapter, the data viewer
                           chapter and the conclusion are always included. Set to 0 to
                           suppress the tour entirely - no tour, no "Tour" button, no
                           first-visit hint beacons. Left at its default (8) the budget is
                           SOFT: an all-overview dashboard gains one extra step so a
                           frequency distribution is always spotlighted. An explicit value
                           makes it a HARD cap, substituting rather than adding. A
                           dictionary's dataset-level "x-qsv" "tour" object can refine the
                           narration - see
                           https://github.com/dathere/qsv/wiki/Visualization#guided-tour
                           `smart` HTML only.
    --heatmap-density <n>  For the `viz smart` map panel: at or above <n> mappable points,
                           draw the core as a density heatmap (DensityMap) instead of
                           markers, keeping per-point hover. Defaults to 0 (disabled): dense
                           point maps instead open as individual points with an in-map
                           "Clusters/Points" toggle rather than aggregating into a static
                           heat surface. Set a positive <n> to opt back in. [default: 0]
    --cluster <mode>       For the `viz smart` map panel: whether to offer an in-map
                           "Clusters/Points" toggle that collapses dense points into native
                           MapLibre count bubbles (which expand back into individual,
                           hoverable points on zoom-in). The map always OPENS as individual
                           points. One of: auto, on, off.
                           "auto" offers the toggle for a plain-marker core (no density
                           heatmap, no bubble-size measure) once it reaches 1,000 points;
                           "on" offers it whenever the core draws as markers; "off" omits
                           it. Only affects `smart`. [default: auto]
    --photos               For the `viz smart` map panel: when a column holds image URLs
                           (detected from the stats cache), embed each point's image URL so
                           that dwelling on a map point for 2 seconds opens that row's photo
                           in a preview card beside the pointer (arrow keys page through a
                           row's photos; Escape dismisses).
                           OFF by default, and deliberately so: images load from whatever
                           third-party host the DATA names, so enabling this makes everyone
                           who opens the Data Schematic request those URLs directly,
                           revealing their IP to that host. Nothing is fetched until a viewer
                           dwells. HTML output only, tile-basemap map panel only, `smart`
                           only.
    --limit <n>            Top-N categories per frequency bar chart. [default: 10]
    --no-nulls             Omit the "(NULL)" bar (empty cells) from frequency bar charts.
                           By default `viz smart` shows a "(NULL)" bar, like `qsv frequency`.
    --no-other             Omit the "Other (N)" aggregate bar from frequency bar charts. It
                           collects the categories beyond --limit (N = how many distinct
                           categories were rolled up) and is shown by default. When just
                           ONE category is left over, it is charted under its own name
                           instead of as an opaque "Other (1)" bar.
    --smarter              Before building the Data Schematic, run `qsv moarstats --advanced`
                           to enrich the stats cache with distribution-shape statistics
                           (bimodality, entropy, skewness, outlier share, Gini, Benford MAD,
                           lag-1 autocorrelation). This unlocks histograms for bimodal
                           columns, frequency bars for concentrated high-cardinality columns,
                           skew/outlier/file-order-drift hints on box panels, Lorenz curves
                           for the most unequal additive measures, and Benford first-digit
                           panels for additive measures spanning 2+ orders of magnitude. Costs one
                           extra pass and writes <stem>.stats.csv, its sidecars and an .idx
                           index. On geocode-enabled builds it also adds the US FIPS code to
                           map hovers. Applied only with default parsing; an input using
                           the --no-headers or --delimiter flags falls back to the standard
                           Data Schematic. Only affects `smart`.
    --hierarchy-style <k>  For `smart`, the chart used for the categorical part-to-whole
                           hierarchy panel (built when 2+ low-cardinality dimensions exist).
                           One of: auto (default), treemap, sunburst, icicle. auto follows
                           best practice - a treemap for a shallow 2-level hierarchy
                           (accurate size comparison) and a sunburst for a deep 3-level one
                           (parent/child structure); icicle is an opt-in level-aligned
                           alternative. An explicit style also bypasses the association
                           screen that would otherwise skip an uninformative panel.
                           Only affects `smart`.
    --no-parcoords         Don't add the parallel-coordinates panel, which `smart` otherwise
                           draws when 3 or more numeric columns correlate (|r| >= 0.3).
                           Only affects `smart`.
    --dictionary <src>     Use a describegpt Data Dictionary to guide panel selection from
                           each field's semantic role/concept (falling back to its content
                           type) instead of relying on column statistics alone: dimensions
                           and numeric codes (ward, census_tract, zone) become bars, measures
                           get box/correlation/trend panels, date/datetime columns (or a
                           column of 4-digit years tagged as time) feed the time-series
                           panel, identifiers / PII / free-text are skipped, and lat/lon
                           feed the map. Field labels are shown as panel subtitles.
                           Columns the dictionary cannot classify still use the statistical
                           heuristic. <src> is either "infer", to run describegpt on the
                           input now (requires an LLM configured), or a path to an existing
                           describegpt dictionary file (jsonschema or json).
                           With "infer", the generated dictionary is saved beside the input
                           as <stem>.schema.json; if that file already exists it is REUSED
                           as-is, skipping the LLM. An inferred dictionary is a DRAFT, not an
                           oracle: re-inferring the same data can assign a column a different
                           role, and role drives panel selection, so a re-infer can hand you
                           a structurally different Data Schematic. The saved sidecar is
                           therefore the artifact of record - review it, correct it, and keep
                           it beside the data. Set QSV_VIZ_DICT_FRESH=1 to ignore it and
                           bypass describegpt's completion cache, forcing a fresh inference
                           that overwrites the sidecar on success. Generation/read failures
                           soft-fall back to the stats-only Data Schematic.
                           qsv re-verifies every hint below on read, so a hand-edit can
                           correct the model but cannot smuggle in a claim the data does not
                           support. Per-field hints live in a property's "x-qsv" object:
                             gauge_range [min,max] - render the KPI tile as a GAUGE on that
                               canonical scale; kept only when the observed value is inside it
                             target <goal> - add a "vs target" DELTA (value minus target).
                               A goal you supply, so "infer" never emits one
                             currency <ISO-4217> - prefix the KPI tile with that currency's
                               symbol ($192B); an unknown code renders verbatim ("XOF 1.2B")
                             unit <UCUM code> - suffix a NON-monetary measure with the unit
                               symbol ("18.4 °C"), in KPI tiles, axis titles and hovers.
                               Checked CASE-SENSITIVELY against ~44 common units (UCUM
                               distinguishes "m" from the "M" mega prefix); an off-table code
                               is dropped. Mutually exclusive with currency
                             aggregation sum|mean - declare how the measure combines across a
                               group, overriding qsv's extensive-vs-intensive guess either way
                             denominator {column, unit?, level?} - on a REGION-CODE column,
                               name the column holding each region's population to add a RATE
                               panel beside the raw-count region map. "unit" converts an area
                               given in m2 or km2; "level" names the AREAL unit those values
                               describe as a "geo." concept token, and a level naming a
                               COARSER geography than the region column is refused
                           The dictionary is also the ONLY source of the pipeline panel,
                           declared in the DATASET-level "x-qsv" object as a "relationships"
                           entry with "kind": "pipeline". Stages may be held in separate
                           columns ("members", widest/upstream first) or as values of one
                           category column ("stage_column" plus "stages", with an optional
                           "value_column"). Declared order is authoritative and is never
                           re-sorted by size: it draws as a funnel while the stage totals
                           never grow, and as a BRIDGE when one outruns its predecessor.
                           For the hint semantics, the pipeline encodings and worked JSON,
                           see https://github.com/dathere/qsv/wiki/Visualization#data-dictionary
                           Only affects `smart`.
    --dictionary-context <file>  Path to a file with extra context about the dataset (a
                           glossary, README, data dictionary, PDF, etc.) forwarded to
                           describegpt as --context-file when `--dictionary infer` generates
                           the dictionary. Better context yields better role/concept/label
                           tags, hence a better Data Schematic. Ignored unless `--dictionary
                           infer` is used. Only affects `smart`.
    --tour-audience <text>  Who the guided Tour should talk to. Forwarded to describegpt when
                           `--dictionary infer` generates the dictionary, so the inferred
                           dictionary carries an "x-qsv.tour" narration written for that
                           audience (e.g. "Explain like I'm 10" - the default - or "a board
                           of directors", "data journalists"). The audience shapes ONLY the
                           tour prose; field labels and descriptions keep their normal
                           register. Ignored unless a FRESH `--dictionary infer` actually
                           runs: when an existing <stem>.schema.json sidecar is reused, delete
                           it (or set QSV_VIZ_DICT_FRESH=1) to re-infer with a new audience.
                           Only affects `smart`.
    --dict-info            When a usable Data Dictionary is available (per --dictionary), add
                           a "Data Schematic" link beneath the page title and an info icon on
                           each panel title: hovering shows that column's description,
                           clicking opens a human-friendly rendering of the dictionary in a
                           side drawer NEXT TO the plots, scrolled to that column's entry.
                           The drawer carries a table of contents, per-column "View chart"
                           links, download buttons bundling every sidecar this run READ (each
                           under 4 MB), and a record of what the Data Schematic LEFT OUT.
                           Everything is embedded in the HTML, so no extra file is written.
                           HTML output only; ignored with a note when no dictionary is
                           available or when exporting an image. Only affects `smart`. See
                           https://github.com/dathere/qsv/wiki/Visualization#dict-info
    --dataset-pid <value>  A persistent identifier (PID) for the dataset - typically a full
                           URL such as a DOI (https://doi.org/10.1234/abc) or other citable
                           link. When set, a "PID" row is added to the metadata table at the
                           top of the Data Schematic. http(s) and mailto values become a
                           clickable link; any other scheme is shown as plain text. HTML
                           output only. Only affects `smart`.
    --no-daemon-bridge     Leave out the qsv-clientd bridge script. By default a `smart`
                           HTML Data Schematic sends one "hello" request to 127.0.0.1 when
                           opened (port 14470, or QSV_CLIENTD_PORT at render time) and,
                           only if a qsv-clientd daemon answers, offers a "Live data" chip to
                           pair with it (approved in a shell) for drill-down, refresh,
                           re-render and read-only queries. With no daemon it does nothing,
                           so the page stays self-contained. Setting QSV_VIZ_NO_DAEMON=1 has
                           the same effect. The page's qsv-schematic-source provenance JSON
                           is kept either way, but without the input fingerprint (which
                           costs an extra read of the input) and without the source URL
                           of a dc: input. HTML output only. Only affects `smart`. See
                           https://github.com/dathere/qsv/blob/master/docs/DATA_SCHEMATIC.md
    --bivariate           Add two pairwise-association overview panels driven by
                           `qsv moarstats --bivariate`: a normalized mutual information (NMI)
                           heatmap over every column pair (numeric AND categorical, unlike
                           the Pearson-only correlation heatmap), plus a ranked "top
                           relationships" bar of the strongest pairs when there are more than
                           8 chartable columns. Identifier / PII / free-text columns (per
                           the --dictionary option) and map lat/lon columns are excluded. It
                           TURNS ON --smarter, plus --dictionary infer when --dictionary
                           isn't already set. Capped at 50 columns (1,225 pairs); wider
                           datasets skip these
                           panels with a warning. Only affects `smart`. See
                           https://github.com/dathere/qsv/wiki/Visualization#bivariate
    --log-scale <mode>     Use a logarithmic y-axis for panels with a high dynamic range:
                           frequency bar panels whose tallest bar dwarfs the rest (e.g. a
                           large "(NULL)" or "Other (N)" bucket), so the small categories
                           stay visible; and box panels of an all-positive column whose
                           observed max/min ratio is huge. One of: auto, on, off. "auto"
                           switches a panel to a log y-axis only when its dynamic range is
                           high; "on" forces it on every frequency panel and every
                           all-positive box panel; "off" keeps the linear axes.
                           Only affects `smart`. [default: auto]
    --violin <mode>        Draw distribution panels as violins (a box plot wrapped in a KDE
                           density silhouette - a strict superset of a plain box) instead of
                           boxes. One of: auto, on, off. "auto" draws a violin for every
                           continuous column EXCEPT those on a log value axis (the KDE is
                           estimated in linear space, which a log axis would distort) and
                           those with too few distinct values or observations for a
                           meaningful KDE; both keep an honest box. "on" also violins those;
                           "off" never draws violins. KDEs are clamped to each column's
                           observed range, so a bounded or discrete measure can't show
                           density past a natural limit. Above a size threshold a violin is
                           drawn from a deterministic strided sample, carries no point
                           overlay and is titled "(sampled)"; that budget scales with
                           QSV_VIZ_MAX_POINTS. For the thresholds and how this interacts with
                           the box-points option, see
                           https://github.com/dathere/qsv/wiki/Visualization#distribution-panels
                           Only affects `smart`. [default: auto]

    --title <s>            Chart title.
    --x-title <s>          X-axis title. (defaults to the x column name)
    --y-title <s>          Y-axis title. (defaults to the y column name)
    --y-range <min:max>    Fix the y-axis to an explicit min:max range (two colon-
                           separated numbers, e.g. -10:55) instead of autoscaling;
                           points outside are clipped from view. Handy when one
                           extreme outlier squashes the rest. Applies to cartesian
                           charts (bar/line/scatter/histogram/box/violin/heatmap/
                           contour). Pass a negative min with `=`: --y-range=-10:55.
    --rangeslider          Add a draggable range-slider (a navigator strip) under the
                           x-axis for panning and zooming. Best for an ordered x-axis
                           (time series, line, candlestick/ohlc). Applies to cartesian
                           charts (bar/line/scatter/histogram/box/violin/candlestick/
                           ohlc); off by default.
    --slider <arg>         Animate the chart over a column: each distinct value of the
                           given column becomes an animation frame, with a Play/Pause
                           button and a slider to scrub through the frames (Gapminder-
                           style). Supported for bar/line/scatter and geo, and may be split
                           into animated traces with --series. NOT supported for `viz map`,
                           whose MapLibre basemap can't animate - use `viz geo` for an
                           animated point map. A slider column that parses as dates is
                           auto-bucketed to a readable number of frames; any other column
                           frames on its distinct values. Axis ranges are pinned across
                           frames so nothing jumps.
                           On `viz scatter`, a slider with --series AND --size builds a
                           Gapminder BUBBLE ANIMATION: --series is the entity, --x/--y the
                           measure pair and --size the third variable (bubble area). Each
                           entity x frame cell collapses to one bubble via --agg (mean by
                           default), scaled once across all frames so sizes stay comparable.
                           For `smart`, this instead takes auto, on or off, controlling
                           whether ONE animated relationship-over-time panel is added - a
                           drifting numeric pair, an animated geo map of dated points, or a
                           Gapminder entity-bubble chart (at most one; the bubble wins, then
                           the geo map, then the pair). auto requires a strong signal (a date
                           column and enough time buckets); on lowers the bar to two buckets
                           but still requires a genuinely drifting relationship; off never
                           does.
    --slider-speed <ms>    Milliseconds each animation frame is shown while playing.
                           [default: 800]
    --slider-cumulative    Accumulate rows across frames: frame N includes every row
                           whose --slider value is at or below the Nth value, so the
                           animation builds up cumulatively instead of replacing each
                           step. Applies to bar/line/scatter and geo.
                           On a bubble animation there is only ever one bubble per entity
                           per frame, so nothing piles up on screen; instead each bubble
                           shows a RUNNING aggregate over all frames up to that point, and
                           so drifts less and less as the animation plays.
    --annotation <s>       Caption note drawn at the bottom of the plot (e.g. to note
                           a clipped outlier). Cartesian charts only.
    --theme <name>         Plotly theme that drives the chart's overall look
                           (background, fonts, axis styling). One of: default,
                           plotly_white, plotly_dark, seaborn, seaborn_whitegrid,
                           seaborn_dark, matplotlib, plotnine (case-insensitive;
                           hyphens accepted). When omitted, qsv's built-in look
                           is used. Applies to all chart types, including `smart`.
    --language <lang>      Render the Data Schematic UI in this language. Accepts a
                           BCP-47/ISO 639 code (es, spa) or an English language
                           name (Spanish). Overrides the language detected in a
                           data dictionary, and is also forwarded to describegpt
                           when inferring one. Curated: en, es, fr, de, it,
                           pt-BR, ja, zh-CN. [default: auto]
    --width <n>            Image width in pixels for static export. Default 1000;
                           for `smart`, auto-scaled to the grid's column count.
    --height <n>           Image height in pixels for static export. Default 600;
                           for `smart`, auto-scaled to the number of panel rows.
    --scale <f>            Image scale factor (static export). [default: 1.0]
    --open                 Open the generated chart in the default browser/viewer.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout. The chart
                           format is inferred from the extension: .html (default),
                           .png, .svg, .pdf, .jpeg, .webp.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. Columns can then only be selected by index.
```
## qsv writestat

```text
Write a CSV as an SPSS, Stata or SAS transport file.

EXPERIMENTAL: the writers this command is built on are young. Check the files
it writes in the package that will read them before relying on them, and please
report anything that looks wrong.

Output formats, chosen by the --output file's extension or by --format:
    SPSS    .sav, .por
    Stata   .dta
    SAS     .xpt (transport version 8, or 5 with --format xpt5)
Compressed SPSS .zsav files & SAS .sas7bdat datasets can't be written. SPSS
portable .por files hold only plain printable ASCII text: a value with any
other character, such as an accented letter or a line break, is an error.

The variable metadata comes from a JSON Schema data dictionary (--dictionary).
One written by 'qsv readstat --dictionary' brings a converted file back with its
variable labels, value labels, missing values & display settings; one written
by 'qsv describegpt --dictionary' gives its labels as variable labels. Without
a dictionary, the column types are inferred from the CSV: numbers from its stats
cache (created beside it if missing, so later runs are faster), and dates, times
& true/false values as Polars recognises them. Set QSV_STATSCACHE_MODE to none
to have Polars infer every type itself instead, reading the whole file on a
single thread, which is much slower.

The dictionary also says how readstat wrote the CSV, and that is undone: the
values decoded by the option --value-labels go back to their codes, and the
SPSS sentinels of --sentinels-as become declared missing values again, whether
in <name>_null columns or embedded. A label that can't be turned back into one
code - shared by two codes, reading as a number that isn't its code, or also
an ordinary value - is an error: write the CSV again with readstat without
the label.

Metadata the output format can't hold is refused rather than dropped silently:
value labels & missing values in SAS transport & SPSS portable files, missing
values & file labels in Stata files, labels too long for SAS transport files,
column names Stata would have to change, and so on. So are data it would lose,
such as numbers beyond ±7.2e75 in a SAS transport file, which it writes as
missing. With --lossy, the file is
written anyway, and a warning names everything left out. Display settings
(measure, alignment, width & format) are written where the format has them and
left out where it doesn't.

  Convert an SPSS file to CSV & back, with its metadata:
    qsv readstat --dictionary survey.schema.json survey.sav -o survey.csv
    qsv writestat --dictionary survey.schema.json survey.csv -o survey2.sav

  Write the same data as a Stata file:
    qsv writestat --dictionary survey.schema.json survey.csv -o survey.dta

  Write a CSV as a SAS transport file, inferring the types:
    qsv writestat data.csv -o data.xpt

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_writestat.rs.

Usage:
    qsv writestat [options] [<input>]
    qsv writestat --help

writestat options:
    --dictionary <file>    The JSON Schema data dictionary giving the variable
                           metadata & types (see above).
    --format <fmt>         The format to write, if not the one the --output
                           extension names. Valid values: sav, por, dta,
                           xpt, xpt5, xpt8.
    --lossy                Write the file even if metadata the format can't
                           hold has to be left out, warning about each.
    --compress             Compress an SPSS .sav file (bytecode compression,
                           which every SPSS version reads).
    --table-name <name>    The dataset name in a SAS transport file. Defaults
                           to the dictionary's, else the --output file name.

Common options:
    -h, --help             Display this message
    -o, --output <file>    The file to write. Required.
    -d, --delimiter <arg>  The field delimiter for reading the CSV.
                           Must be a single character. (default: ,)
```
