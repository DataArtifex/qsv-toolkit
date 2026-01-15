# QSV Commands

# QSV Commands

## apply

```text
Apply a series of transformation functions to given CSV column/s. This can be used to
perform typical data-wrangling tasks and/or to harmonize some values, etc.

It has four subcommands:
 1. operations*   - 40 string, format, currency, regex & NLP operators.
 2. emptyreplace* - replace empty cells with <--replacement> string.
 3. dynfmt        - Dynamically constructs a new column from other columns using
                    the <--formatstr> template.
 4. calcconv      - parse and evaluate math expressions, with support for units
                    and conversions.
    * subcommand is multi-column capable.

OPERATIONS (multi-column capable)
Multiple operations can be applied, with the comma-delimited operation series
applied in order:

  trim => Trim the cell
  trim,upper => Trim the cell, then transform to uppercase
  lower,simdln => Lowercase the cell, then compute the normalized
      Damerau-Levenshtein similarity to --comparand

Operations support multi-column transformations. Just make sure the
number of transformed columns with the --rename option is the same. e.g.:

# trim and fold to uppercase the col1,col2 and col3 columns and rename them
# to newcol1,newcol2 and newcol3

  $ qsv apply operations trim,upper col1,col2,col3 -r newcol1,newcol2,newcol3 file.csv

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

Examples:
Trim, then transform to uppercase the surname field.

  $ qsv apply operations trim,upper surname file.csv

Trim, then transform to uppercase the surname field and rename the column uppercase_clean_surname.

  $ qsv apply operations trim,upper surname -r uppercase_clean_surname file.csv

Trim, then transform to uppercase the surname field and
save it to a new column named uppercase_clean_surname.

  $ qsv apply operations trim,upper surname -c uppercase_clean_surname file.csv

Trim, then transform to uppercase the firstname and surname fields and
rename the columns ufirstname and usurname.

  $ qsv apply operations trim,upper firstname,surname -r ufirstname,usurname file.csv

Trim parentheses & brackets from the description field.

  $ qsv apply operations mtrim description --comparand '()<>' file.csv

Replace ' and ' with ' & ' in the description field.

  $ qsv apply operations replace description --comparand ' and ' --replacement ' & ' file.csv

Extract the numeric value of the Salary column in a new column named Salary_num.

  $ qsv apply operations currencytonum Salary -c Salary_num file.csv

Convert the USD_Price to PHP_Price using the currency symbol "PHP" with a conversion rate of 60.

  $ qsv apply operations numtocurrency USD_Price -C PHP -R 60 -c PHP_Price file.csv

Base64 encode the text_col column & save the encoded value into new column named encoded & decode it.

  $ qsv apply operations encode64 text_col -c encoded file.csv | qsv apply operations decode64 encoded

Compute the Normalized Damerau-Levenshtein similarity of the neighborhood column to the string 'Roxbury'
and save it to a new column named dln_roxbury_score.

  $ qsv apply operations lower,simdln neighborhood --comparand roxbury -c dln_roxbury_score boston311.csv

You can also use this subcommand command to make a copy of a column:

  $ qsv apply operations copy col_to_copy -c col_copy file.csv

EMPTYREPLACE (multi-column capable)
Replace empty cells with <--replacement> string.
Non-empty cells are not modified. See the `fill` command for more complex empty field operations.

Examples:
Replace empty cells in file.csv Measurement column with 'None'.

  $ qsv apply emptyreplace Measurement --replacement None file.csv

Replace empty cells in file.csv Measurement column with 'Unknown Measurement'.

  $ qsv apply emptyreplace Measurement --replacement 'Unknown Measurement' file.csv

Replace empty cells in file.csv M1,M2 and M3 columns with 'None'.

  $ qsv apply emptyreplace M1,M2,M3 --replacement None file.csv

Replace all empty cells in file.csv for columns that start with 'Measurement' with 'None'.

  $ qsv apply emptyreplace '/^Measurement/' --replacement None file.csv

Replace all empty cells in file.csv for columns that start with 'observation'
case insensitive with 'None'.

  $ qsv apply emptyreplace --replacement None '/(?i)^observation/' file.csv

DYNFMT
Dynamically constructs a new column from other columns using the <--formatstr> template.
The template can contain arbitrary characters. To insert a column value, enclose the
column name in curly braces, replacing all non-alphanumeric characters with underscores.

If you need to dynamically construct a column with more complex formatting requirements and
computed values, check out the py command to take advantage of Python's f-string formatting.

Examples:
Create a new column 'mailing address' from 'house number', 'street', 'city' and 'zip-code' columns:

  $ qsv apply dynfmt --formatstr '{house_number} {street}, {city} {zip_code} USA' -c 'mailing address' file.csv

Create a new column 'FullName' from 'FirstName', 'MI', and 'LastName' columns:

  $ qsv apply dynfmt --formatstr 'Sir/Madam {FirstName} {MI}. {LastName}' -c FullName file.csv

CALCCONV
Parse and evaluate math expressions into a new column, with support for units and conversions.
The math expression is built dynamically using the <--formatstr> template, similar to the DYNFMT
subcommand, with the addition that if the literal '<UNIT>' is found at the end of the template, the
inferred unit will be appended to the result.

For a complete list of supported units, constants, operators and functions, see https://docs.rs/cpc

Examples:
Do simple arithmetic:
  $ qsv apply calcconv --formatstr '{col1} + {col2} * {col3}' --new-column result file.csv

With support for operators like % and ^:
  $ qsv apply calcconv --formatstr '{col1} % 3' --new-column remainder file.csv

Convert from one unit to another:
  $ qsv apply calcconv --formatstr '{col1}mb in gigabytes' -c gb file.csv
  $ qsv apply calcconv --formatstr '{col1} Fahrenheit in Celsius" -c metric_temperature file.csv

Mix units and conversions are automatically done for you:
  $ qsv apply calcconv --formatstr '{col1}km + {col2}mi in meters' -c meters file.csv

You can append the inferred unit at the end of the result by ending the expression with '<UNIT>':
  $ qsv apply calcconv --formatstr '({col1} + {col2})km to light years <UNIT>' -c light_years file.csv

You can even do complex temporal unit conversions:
  $ qsv apply calcconv --formatstr '{col1}m/s + {col2}mi/h in kilometers per h' -c kms_per_h file.csv

Use math functions - see https://docs.rs/cpc/latest/cpc/enum.FunctionIdentifier.html for list of functions:
  $ qsv apply calcconv --formatstr 'round(sqrt{col1}^4)! liters' -c liters file.csv

Use percentages:
  $ qsv apply calcconv --formatstr '10% of abs(sin(pi)) horsepower to watts' -c watts file.csv

And use very large numbers:
  $ qsv apply calcconv --formatstr '{col1} Billion Trillion * {col2} quadrillion vigintillion' -c num_atoms file.csv

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_apply.rs.

Usage:
qsv apply operations <operations> [options] <column> [<input>]
qsv apply emptyreplace --replacement=<string> [options] <column> [<input>]
qsv apply dynfmt --formatstr=<string> [options] --new-column=<name> [<input>]
qsv apply calcconv --formatstr=<string> [options] --new-column=<name> [<input>]
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

    CALCONV subcommand:
        --formatstr=<string>        The calculation/conversion expression to use.
        --new-column=<name>         Put the calculated/converted values in a new column.

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

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout.
    -n, --no-headers            When set, the first row will not be interpreted
                                as headers.
    -d, --delimiter <arg>       The field delimiter for reading CSV data.
                                Must be a single character. (default: ,)
    -p, --progressbar           Show progress bars. Not valid for stdin.
```
## behead

```text
Drop a CSV file's header.

Usage:
    qsv behead [options] [<input>]
    qsv behead --help

Common options:
    -h, --help             Display this message
    -f, --flexible         Do not validate if the CSV has different number of
                           fields per record, increasing performance.
    -o, --output <file>    Write output to <file> instead of stdout.
```
## cat

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

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_cat.rs.

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
## count

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

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_count.rs.

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
    --low-memory           Use the Polars CSV Reader's low-memory mode. This mode
                           is slower but uses less memory. If counting still fails,
                           use --no-polars instead to use the streaming CSV reader.


Common options:
    -h, --help             Display this message
    -f, --flexible         Do not validate if the CSV has different number of
                           fields per record, increasing performance when counting
                           without an index.
    -n, --no-headers       When set, the first row will be included in
                           the count.
    -d, --delimiter <arg>  The delimiter to use when reading CSV data.
                           Must be a single character. [default: ,]
```
## dedup

```text
Deduplicates CSV rows. 

This requires reading all of the CSV data into memory because because the rows need
to be sorted first.

That is, unless the --sorted option is used to indicate the CSV is already sorted -
typically, with the sort cmd for more sorting options or the extsort cmd for larger
than memory CSV files. This will make dedup run in streaming mode with constant memory.

Either way, the output will not only be deduplicated, it will also be sorted.

A duplicate count will also be sent to <stderr>.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_dedup.rs.

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
```
## describegpt

```text
Create a "neuro-procedural" Data Dictionary and/or infer Description & Tags about a Dataset
using an OpenAI API-compatible Large Language Model (LLM).

It does this by compiling Summary Statistics & a Frequency Distribution of the Dataset,
and then prompting the LLM with detailed, configurable, Mini Jinja-templated prompts with
these extended statistical context.

The Data Dictionary is "neuro-procedural" as it uses a hybrid approach. It's primarily populated
deterministically using Summary Statistics & Frequency Distribution data, and only the human-friendly
Label & Description are populated by the "neural network" LLM using the same statistical context.

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
QSV_DESCRIBEGPT_DB_ENGINE environment variable is set to the absolute path of the DuckDB binary,
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
Local LLMs tested include Ollama, Jan and LM Studio.

NOTE: LLMs are prone to inaccurate information being produced. Verify output results before using them.

CACHING:
As LLM inferencing takes time and can be expensive, describegpt caches the LLM inferencing results
in a either a disk cache (default) or a Redis cache. It does so by calculating the BLAKE3 hash of the
input file and using it as the primary cache key along with the prompt type, model and other parameters
as required.

The default disk cache is stored in the ~/.qsv/cache/describegpt directory with a default TTL of 28 days
and cache hits NOT refreshing an existing cached value's TTL.
Adjust the QSV_DISKCACHE_TTL_SECS & QSV_DISKCACHE_TTL_REFRESH env vars to change disk cache settings.

Alternatively a Redis cache can be used instead of the disk cache. This is especially useful if you want
to share the cache across the network with other users or computers.
The Redis cache is stored in database 3 by default with a TTL of 28 days and cache hits NOT refreshing
an existing cached value's TTL. Adjust the QSV_DG_REDIS_CONNSTR, QSV_REDIS_MAX_POOL_SIZE,
QSV_REDIS_TTL_SECONDS & QSV_REDIS_TTL_REFRESH env vars to change Redis cache settings.

Examples:

  # Generate a Data Dictionary, Description & Tags of data.csv using default OpenAI gpt-oss-20b model
  # (replace <API_KEY> with your OpenAI API key)
  $ qsv describegpt data.csv --api-key <API_KEY> --all

  # Generate a Data Dictionary of data.csv using the DeepSeek R1:14b model on a local Ollama instance
  $ qsv describegpt data.csv -u http://localhost:11434/v1 --model deepseek-r1:14b --dictionary

  # Ask questions about the sample NYC 311 dataset using LM Studio with the default gpt-oss-20b model.
  # Questions that can be answered using the Summary Statistics & Frequency Distribution of the dataset.
  $ export QSV_LLM_BASE_URL=http://localhost:1234/v1
  $ qsv describegpt NYC_311.csv --prompt "What is the most common complaint?"
  $ qsv describegpt NYC_311.csv --prompt "List the top 10 complaints."
  $ qsv describegpt NYC_311.csv -p "Can you tell me how many complaints were resolved?"

  # Ask detailed questions that require SQL queries and auto-invoke SQL RAG mode
  # Generate a DuckDB SQL query to answer the question
  $ export QSV_DESCRIBEGPT_DB_ENGINE=/path/to/duckdb
  $ qsv describegpt NYC_311.csv -p "What's the breakdown of complaint types by borough descending order?"
  # Prompt requires a SQL query. Execute query and save results to a file with the --sql-results option.
  # If generated SQL query runs successfully, the file is "results.csv". Otherwise, it is "results.sql".
  $ qsv describegpt NYC_311.csv -p "Aggregate complaint types by community board" --sql-results results

  # Cache Dictionary, Description & Tags inference results using the Redis cache instead of the disk cache
  $ qsv describegpt data.csv --all --redis-cache
  # Get fresh Description & Tags inference results from the LLM and refresh disk cache entries for both
  $ qsv describegpt data.csv --description --tags --fresh
  # Get fresh inference results from the LLM and refresh the Redis cache entries for all three
  $ qsv describegpt data.csv --all --redis-cache --fresh

  # Forget a cached response for data.csv's data dictionary if it exists and then exit
  $ qsv describegpt data.csv --dictionary --forget
  # Flush/Remove ALL cached entries in the disk cache
  $ qsv describegpt --flush-cache
  # Flush/Remove ALL cached entries in the Redis cache
  $ qsv describegpt --redis-cache --flush-cache

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_describegpt.rs.

For more detailed info on how describegpt works and how to prepare a prompt file,
see https://github.com/dathere/qsv/blob/master/docs/Describegpt.md

Usage:
    qsv describegpt [options] [<input>]
    qsv describegpt (--redis-cache) (--flush-cache)
    qsv describegpt --help

describegpt options:
                           DATA ANALYSIS/INFERENCING OPTIONS:
    --dictionary           Create a Data Dictionary using a hybrid "neuro-procedural" pipeline - i.e.
                           the Dictionary is populated deterministically using Summary Statistics and
                           Frequency Distribution data, and only the human-friendly Label and Description
                           are populated by the LLM using the same statistical context.
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
                           [default: 25]
    --addl-cols            Add additional columns to the dictionary from the Summary Statistics.
  --addl-cols-list <list>  A comma-separated list of additional stats columns to add to the dictionary.
                           The columns must be present in the Summary Statistics.
                           If the columns are not present in the Summary Statistics or already in the
                           dictionary, they will be ignored.
                           CONVENIENCE VALUES:
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
                           [default: --infer-dates --infer-boolean --mad --quartiles --percentiles --force --stats-jsonl]
    --enum-threshold <n>   The threshold for compiling Enumerations with the frequency command
                           before bucketing other unique values into the "Other" category.
                           [default: 10]

                           CUSTOM PROMPT OPTIONS:
    -p, --prompt <prompt>  Custom prompt to answer questions about the dataset.
                           The prompt will be answered based on the dataset's Summary Statistics,
                           Frequency data & Data Dictionary. If the prompt CANNOT be answered by looking
                           at these metadata, a SQL query will be generated to answer the question.
                           If the "polars" or the "QSV_DESCRIBEGPT_DB_ENGINE" environment variable is set
                           & the `--sql-results` option is used, the SQL query will be automatically
                           executed and its results returned.
                           Otherwise, the SQL query will be returned along with the reasoning behind it.
                           If it starts with "file:" prefix, the prompt is read from the file specified.
                           e.g. "file:my_long_prompt.txt"
    --sql-results <file>   The file to save the SQL query results to.
                           Only valid if the --prompt option is used & the "polars" or the
                           "QSV_DESCRIBEGPT_DB_ENGINE" environment variable is set.
                           If the SQL query executes successfully, the results will be saved with a
                           ".csv" extension. Otherwise, it will be saved with a ".sql" extension so
                           the user can inspect why it failed and modify it.
    --prompt-file <file>   The configurable TOML file containing prompts to use for inferencing.
                           If no file is provided, default prompts will be used.
                           The prompt file uses the Mini Jinja template engine (https://docs.rs/minijinja)
                           See https://github.com/dathere/qsv/blob/master/resources/describegpt_defaults.toml
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

                           LLM API OPTIONS:
    -u, --base-url <url>   The LLM API URL. Supports APIs & local LLMs compatible with
                           the OpenAI API specification (Ollama, Jan, LM Studio, TogetherAI, etc.).
                           The default base URL for Ollama is http://localhost:11434/v1.
                           The default for Jan is https://localhost:1337/v1.
                           The default for LM Studio is http://localhost:1234/v1.
                           The base URL will be the base URL of the prompt file.
                           If the QSV_LLM_BASE_URL environment variable is set, it'll be used instead.
                           [default: https://api.openai.com/v1]
    -m, --model <model>    The model to use for inferencing.
                           If the QSV_LLM_MODEL environment variable is set, it'll be used instead.
                           [default: openai/gpt-oss-20b]
    --language <lang>      The output language/dialect to use for the response. (e.g., "Spanish", "French",
                           "Hindi", "Mandarin", "Italian", "Castilian", "Franglais", "Taglish", "Pig Latin",
                           "Valley Girl", "Pirate", "Shakespearean English", "Chavacano", "Gen Z", "Yoda", etc.)
    
                             CHAT MODE (--prompt) LANGUAGE DETECTION BEHAVIOR:
                             When --prompt is used and --language is not set, automatically detects
                             the language of the prompt with an 80% confidence threshold.
                             If the threshold is met, it will specify the detected language in its response.
                             If set to a float (0.0 to 1.0), specifies the detection confidence threshold.
                             If set to a string, specifies the language/dialect to use for the response.
                             Note that LLMs often detect the language independently, but will often respond
                             in the model's default language. This option is here to ensure responses are
                             in the detected language of the prompt.
    --addl-props <json>    Additional model properties to pass to the LLM chat/completion API.
                           Various models support different properties beyond the standard ones.
                           For instance, gpt-oss-20b supports the "reasoning_effort" property.
                           e.g. to set the "reasoning_effort" property to "high" & "temperature"
                           to 0.5, use '{"reasoning_effort": "high", "temperature": 0.5}'
    -k, --api-key <key>    The API key to use. If the QSV_LLM_APIKEY envvar is set,
                           it will be used instead. Required when the base URL is not localhost.
                           Set to NONE to suppress sending the API key.
    -t, --max-tokens <n>   Limits the number of generated tokens in the output.
                           Set to 0 to disable token limits.
                           If the --base-url is localhost, indicating a local LLM,
                           the default is automatically set to 0.
                           [default: 10000]
    --timeout <secs>       Timeout for completions in seconds. If 0, no timeout is used.
                           [default: 300]
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
  --disk-cache-dir <dir>   The directory <dir> to store the disk cache. Note that if the directory
                           does not exist, it will be created. If the directory exists, it will be used as is,
                           and will not be flushed. This option allows you to maintain several disk caches
                           for different describegpt jobs (e.g. one for a data portal, another for internal
                           data exchange, etc.)
                           [default: ~/.qsv/cache/describegpt]
    --redis-cache          Use Redis instead of the default disk cache to cache LLM completions.
                           It connects to "redis://127.0.0.1:6379/3" by default, with a connection pool
                           size of 20, with a TTL of 28 days, and cache hits NOT refreshing an existing
                           cached value's TTL.
                           This option automatically disables the disk cache.
    --fresh                Send a fresh request to the LLM API, refreshing a cached response if it exists.
                           When a --prompt SQL query fails, you can also use this option to request the
                           LLM to generate a new SQL query.
    --forget               Remove a cached response if it exists and then exit.
    --flush-cache          Flush the current cache entries on startup.
                           WARNING: This operation is irreversible.

Common options:
    -h, --help             Display this message
    --format <format>      Output format: Markdown, TSV, JSON, or TOON.
                           TOON is a compact, human-readable encoding of the JSON data model for LLM prompts.
                           See https://toonformat.dev/ for more info.
                           [default: Markdown]
    -o, --output <file>    Write output to <file> instead of stdout. If --format is set to TSV,
                           separate files will be created for each prompt type with the pattern
                           {filestem}.{kind}.tsv (e.g., output.dictionary.tsv, output.tags.tsv).
    -q, --quiet            Do not print status messages to stderr.
```
## enum

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
## explode

```text
Explodes a row into multiple ones by splitting a column value based on the
given separator.

For instance the following CSV:

name,colors
John,blue|yellow
Mary,red

Can be exploded on the "colors" <column> based on the "|" <separator> to:

name,colors
John,blue
John,yellow
Mary,red

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
## fill

```text
Fill empty fields in selected columns of a CSV.

This command fills empty fields in the selected column
using the last seen non-empty field in the CSV. This is
useful to forward-fill values which may only be included
the first time they are encountered.

The option `--default <value>` fills all empty values
in the selected columns with the provided default value.

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

Usage:
    qsv fill [options] [--] <selection> [<input>]
    qsv fill --help

fill options:
    -g --groupby <keys>    Group by specified columns.
    -f --first             Fill using the first valid value of a column, instead of the latest.
    -b --backfill          Fill initial empty values with the first valid value.
    -v --default <value>   Fill using this default value.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. (i.e., They are not searched, analyzed,
                           sliced, etc.)
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## fixlengths

```text
Transforms CSV data so that all records have the same length. The length is
the length of the longest record in the data (not counting trailing empty fields,
but at least 1). Records with smaller lengths are padded with empty fields.

This requires two complete scans of the CSV data: one for determining the
record size and one for the actual transform. Because of this, the input
given must be a file and not stdin.

Alternatively, if --length is set, then all records are forced to that length.
This requires a single pass and can be done with stdin.

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
## flatten

```text
Prints flattened records such that fields are labeled separated by a new line.
This mode is particularly useful for viewing one record at a time. Each
record is separated by a special '#' character (on a line by itself), which
can be changed with the --separator flag.

There is also a condensed view (-c or --condense) that will shorten the
contents of each field to provide a summary view.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_flatten.rs.

Usage:
    qsv flatten [options] [<input>]
    qsv flatten --help

flatten options:
    -c, --condense <arg>          Limits the length of each field to the value
                                  specified. If the field is UTF-8 encoded, then
                                  <arg> refers to the number of code points.
                                  Otherwise, it refers to the number of bytes.
    -f, --field-separator <arg>   A string of character to write between a column name
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
## fmt

```text
Formats CSV data with a custom delimiter or CRLF line endings.

Generally, all commands in qsv output CSV data in a default format, which is
the same as the default format for reading CSV data. This makes it easy to
pipe multiple qsv commands together. However, you may want the final result to
have a specific delimiter or record separator, and this is where 'qsv fmt' is
useful.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_fmt.rs.

Usage:
    qsv fmt [options] [<input>]
    qsv fmt --help

fmt options:
    -t, --out-delimiter <arg>  The field delimiter for writing CSV data.
                               Must be a single character.
                               If set to "T", uses tab as the delimiter.
                               [default: ,]
    --crlf                     Use '\r\n' line endings in the output.
    --ascii                    Use ASCII field and record separators.
                               Use Substitute (U+00A1) as the quote character.
    --quote <arg>              The quote character to use. [default: "]
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
## frequency

```text
Compute a frequency distribution table on input data. It has CSV and JSON output modes.
https://en.wikipedia.org/wiki/Frequency_(statistics)#Frequency_distribution_table

In CSV output mode (default), the table is formatted as CSV data with the following
columns - field,value,count,percentage,rank.

The rank column is 1-based and is calculated based on the count of the values,
with the most frequent having a rank of 1. In case of ties, the rank is calculated
based on the rank-strategy option - "min" (default), "max", "dense", "ordinal", or "average".

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
or -1 for CPU-based chunking (1 chunk = num records/number of CPUs)), or by setting the --jobs option.

NOTE: "Complete" Frequency Tables:

    By default, ID columns will have an "<ALL UNIQUE>" value with count equal to
    rowcount and percentage set to 100 with a rank of 0. This is done by using the
    stats cache to fetch each column's cardinality - allowing qsv to short-circuit
    frequency compilation and eliminate the need to maintain a hashmap for ID columns.

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
    -u, --unq-limit <arg>   If a column has all unique values, limit the
                            frequency table to a sample of N unique items.
                            Set to '0' to disable a unique_limit.
                            [default: 10]
    --lmt-threshold <arg>   The threshold for which --limit and --unq-limit
                            will be applied. If the number of unique items
                            in a column >= threshold, the limits will be applied.
                            Set to '0' to disable the threshold and always apply limits.
                            [default: 0]
-r, --rank-strategy <arg>   The strategy to use when there are count-tied values in the frequency table.
                            See https://en.wikipedia.org/wiki/Ranking for more info.
                            Valid values are:
                              - dense: Assigns consecutive integers regardless of ties,
                                incrementing by 1 for each new count value (AKA "1223" ranking).
                              - min: Tied items receive the minimum rank position (AKA "1224" ranking).
                              - max: Tied items receive the maximum rank position (AKA "1334" ranking).
                              - ordinal: The next rank is the current rank plus 1 (AKA "1234" ranking).
                              - average: Tied items receive the average of their ordinal positions
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
    --other-text <arg>      The text to use for the "Other" category. If set to "<NONE>",
                            the "Other" category will not be included in the frequency table.
                            [default: Other]
    -a, --asc               Sort the frequency tables in ascending order by count.
                            The default is descending order. Note that this option will
                            also reverse ranking - i.e. the LEAST frequent values will
                            have a rank of 1.
    --no-trim               Don't trim whitespace from values when computing frequencies.
                            The default is to trim leading and trailing whitespaces.
    --null-text <arg>       The text to use for NULL values.
                            [default: (NULL)]
    --no-nulls              Don't include NULLs in the frequency table.
    -i, --ignore-case       Ignore case when computing frequencies.
   --all-unique-text <arg>  The text to use for the "<ALL_UNIQUE>" category.
                            [default: <ALL_UNIQUE>]
    --vis-whitespace        Visualize whitespace characters in the output. See
                            https://github.com/dathere/qsv/wiki/Supplemental#whitespace-markers
                            for the list of whitespace markers.
    -j, --jobs <arg>        The number of jobs to run in parallel when the given CSV data has
                            an index. Note that a file handle is opened for each job.
                            When not set, defaults to the number of CPUs detected.

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
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
```
## headers

```text
Prints the fields of the first row in the CSV data.

These names can be used in commands like 'select' to refer to columns in the
CSV data.

Note that multiple CSV files may be given to this command. This is useful with
the --intersect flag.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_headers.rs.

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
    --intersect            Shows the intersection of all headers in all of
                           the inputs given.
    --trim                 Trim space & quote characters from header name.

Common options:
    -h, --help             Display this message
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## index

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
## join

```text
Joins two sets of CSV data on the specified columns.

The default join operation is an 'inner' join. This corresponds to the
intersection of rows on the keys specified.

Joins are always done by ignoring leading and trailing whitespace. By default,
joins are done case sensitively, but this can be disabled with the --ignore-case
flag.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_join.rs.

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
## moarstats

```text
Add dozens of additional statistics, including extended outlier & robust statistics
to an existing stats CSV file. It also maps the field type to the most specific
W3C XML Schema Definition (XSD) datatype (https://www.w3.org/TR/xmlschema-2/).

The `moarstats` command extends an existing stats CSV file (created by the `stats` command)
by computing "moar" (https://www.dictionary.com/culture/slang/moar) statistics that can be
derived from existing stats columns and by scanning the original CSV file.

It looks for the `<FILESTEM>.stats.csv` file for a given CSV input. If the stats CSV file
does not exist, it will first run the `stats` command with configurable options to establish
the baseline stats, to which it will add more stats columns.

If the `.stats.csv` file is found, it will skip running stats and just append the additional
stats columns.

Currently computes the following 18 additional univariate statistics:
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
11. Kurtosis: Measures the "tailedness" of the distribution (excess kurtosis).
    Positive values indicate heavy tails, negative values indicate light tails.
    Values near 0 indicate a normal distribution.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Kurtosis
12. Bimodality Coefficient: Measures whether a distribution has two modes (peaks) or is unimodal.
    BC < 0.555 indicates unimodal, BC >= 0.555 indicates bimodal/multimodal.
    Computed as (skewness² + 1) / (kurtosis + 3).
    Requires --advanced flag (needs skewness from base stats and kurtosis from --advanced flag).
    https://en.wikipedia.org/wiki/Bimodality
13. Gini Coefficient: Measures inequality/dispersion in the distribution.
    Values range from 0 (perfect equality) to 1 (maximum inequality).
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Gini_coefficient
14. Atkinson Index: Measures inequality in the distribution with a sensitivity parameter.
    Values range from 0 (perfect equality) to 1 (maximum inequality).
    The Atkinson Index is a more general form of the Gini coefficient that allows for
    different sensitivity to inequality. Sensitivity is configurable via --epsilon.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Atkinson_index
15. Shannon Entropy: Measures the information content/uncertainty in the distribution.
    Higher values indicate more diversity, lower values indicate more concentration.
    Values range from 0 (all values identical) to log2(n) where n is the number of unique values.
    Requires --advanced flag.
    https://en.wikipedia.org/wiki/Entropy_(information_theory)
16. Normalized Entropy: Normalized version of Shannon Entropy scaled to [0, 1].
    Values range from 0 (all values identical) to 1 (all values equally distributed).
    Computed as shannon_entropy / log2(cardinality).
    Requires shannon_entropy (from --advanced flag) and cardinality (from base stats).
17. Winsorized Mean: Replaces values below/above thresholds with threshold values, then computes mean.
    All values are included in the calculation, but extreme values are capped at thresholds.
    https://en.wikipedia.org/wiki/Winsorized_mean
    Also computes: winsorized_stddev, winsorized_variance, winsorized_cv, winsorized_range,
    and winsorized_stddev_ratio (winsorized_stddev / overall_stddev).
18. Trimmed Mean: Excludes values outside thresholds, then computes mean.
    Only values within thresholds are included in the calculation.
    https://en.wikipedia.org/wiki/Truncated_mean
    Also computes: trimmed_stddev, trimmed_variance, trimmed_cv, trimmed_range,
    and trimmed_stddev_ratio (trimmed_stddev / overall_stddev).
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
Kurtosis, Gini & Atkinson Index require reading the original CSV file to collect
all values for computation.

BIVARIATE STATISTICS:

The `moarstats` command also computes the following 6 bivariate statistics:
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

These bivariate statistics are computed when the `--bivariate` flag is used
and require an indexed CSV file (index will be auto-created if missing).
Bivariate statistics are output to a separate file: `<FILESTEM>.stats.bivariate.csv`.

Bivariate statistics require reading the entire CSV file and are computationally VERY expensive.
For large files (>= 10k records), parallel chunked processing is used when an index is available.
For smaller files or when no index exists, sequential processing is used.

MULTI-DATASET BIVARIATE STATISTICS:

When using the `--join-inputs` flag, multiple datasets can be joined internally before
computing bivariate statistics. This allows analyzing bivariate statistics across datasets
that share common join keys. The joined dataset is saved as a temporary file that is
automatically deleted after computing the bivariate statistics.
The bivariate statistics are saved to `<FILESTEM>.stats.bivariate.joined.csv`.

Examples:

  # Add moar stats to existing stats file
  $ qsv moarstats data.csv

  # Generate baseline stats first with custom options, then add moar stats
  $ qsv moarstats data.csv --stats-options "--everything --infer-dates"

  # Output to different file
  $ qsv moarstats data.csv --output enhanced_stats.csv

  # Compute bivariate statistics between fields
  $ qsv moarstats data.csv --bivariate

  # Join multiple datasets and compute bivariate statistics
  $ qsv moarstats data.csv -B --join-inputs customers.csv,products.csv --join-keys cust_id,prod_id

  # Join multiple datasets and compute bivariate statistics with different join type
  $ qsv moarstats data.csv -B -J customers.csv,products.csv -K cust_id,prod_id -T left

Usage:
    qsv moarstats [options] [<input>]
    qsv moarstats --help

moarstats options:
    --advanced             Compute Kurtosis, ShannonEntropy, Bimodality Coefficient,
                           Gini Coefficient and Atkinson Index.
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
                           [default: --infer-dates --infer-boolean --mad --quartiles --percentiles --force --stats-jsonl]
    --round <n>            Round statistics to <n> decimal places. Rounding follows
                           Midpoint Nearest Even (Bankers Rounding) rule.
                           [default: 4]
    --use-percentiles      Use percentiles instead of Q1/Q3 for winsorization/trimming.
                           Requires percentiles to be computed in the stats CSV.
   --pct-thresholds <arg>  Comma-separated percentile pair (e.g., "10,90") to use
                           for winsorization/trimming when --use-percentiles is set.
                           Both values must be between 0 and 100, and lower < upper.
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
                           Computes pairwise correlations, covariances, mutual information, and
                           normalized mutual information between columns. Outputs to
                           <FILESTEM>.stats.bivariate.csv.
    -S, --bivariate-stats <stats>
                           Comma-separated list of bivariate statistics to compute.
                           Options: pearson, spearman, kendall, covariance, mi (mutual information),
                           nmi (normalized mutual information)
                           Use "all" to compute all statistics or "fast" to compute only
                           pearson & covariance, which is much faster as it doesn't require storing
                           all values and uses streaming algorithms.
                           [default: fast]
    -C, --cardinality-threshold <n>
                           Skip mutual information computation for field pairs where either
                           field has cardinality exceeding this threshold. Helps avoid
                           expensive computations for high-cardinality fields.
                           [default: 1000000]
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
## py

```text
Create a new computed column or filter rows by evaluating a Python expression on 
every row of a CSV file.

The executed Python has 4 ways to reference cell values (as strings):
  1. Directly by using column name (e.g. amount) as a local variable. If a column
     name has spaces and other special characters, they are replaced with underscores
     (e.g. "unit cost" -> unit_cost, "test-units/sec" -> test_units_sec)
  2. Indexing cell value by column name as an attribute: col.amount
  3. Indexing cell value by column name as a key: col["amount"]
  4. Indexing cell value by column position: col[0]

Of course, if your input has no headers, then 4. will be the only available
option.

Some usage examples:

  Sum numeric columns 'a' and 'b' and call new column 'c'
  $ qsv py map c "int(a) + int(b)"
  $ qsv py map c "int(col.a) + int(col['b'])"
  $ qsv py map c "int(col[0]) + int(col[1])"

  Use Python f-strings to calculate using multiple columns (qty, fruit & "unit cost") 
    and format into a new column 'formatted'
  $ qsv py map formatted 'f"{qty} {fruit} cost ${(float(unit_cost) * float(qty)):.2f}"'

  You can even have conditionals in your f-string:
  $ qsv py map formatted \
   'f"""{qty} {fruit} cost ${(float(unit_cost) * float(qty)):.2f}. Its quite {"cheap" if ((float(unit_cost) * float(qty)) < 20.0) else "expensive"}!"""'

  Note how we needed to use triple double quotes for the f-string, so we can use the literals
  "cheap" and "expensive" in the f-string expression.

  Strip and prefix cell values
  $ qsv py map prefixed "'clean_' + a.strip()"

  Filter some lines based on numerical filtering
  $ qsv py filter "int(a) > 45"

  Load helper file with function to compute Fibonacci sequence of the column "num_col"
  $ qsv py map --helper fibonacci.py fib qsv_uh.fibonacci(num_col) data.csv

  Below is a detailed example of the --helper option:

  Use case:
  Need to calculate checksum/md5sum of some columns. First column (c1) is "id", and do md5sum of
  the rest of the columns (c2, c3 and c4).

  Given test.csv:
    c1,c2,c3,c4
    1,a2,a3,a4
    2,b2,b3,b4
    3,c2,c3,c4

  and hashhelper.py:
    import hashlib
    def md5hash (*args):
        s = ",".join(args)
        return(hashlib.md5(s.encode('utf-8')).hexdigest())

  with the following command:
  $ qsv py map --helper hashhelper.py hashcol 'qsv_uh.md5hash(c2,c3,c4)' test.csv

  we get:
  c1,c2,c3,c4,hashcol
  1,a2,a3,a4,cb675342ed940908eef0844d17c35fab
  2,b2,b3,b4,7d594b33f82bdcbc1cfa6f924a84c4cd
  3,c2,c3,c4,6eabbfdbfd9ab6ae7737fb2b82f6a1af
  
  Note that qsv with the `python` feature enabled will panic on startup even if you're not
  using the `py` command if Python's shared libraries are not found.
  
  Also, the following Python modules are automatically loaded and available to the user -
  builtins, math, random & datetime. The user can import additional modules with the --helper option,
  with the ability to use any Python module that's installed in the current Python virtualenv. 

  The Python expression is evaluated on a per record basis.
  With "py map", if the expression is invalid for a record, "<ERROR>" is returned for that record.
  With "py filter", if the expression is invalid for a record, that record is not filtered.

  If any record has an invalid result, an exitcode of 1 is returned and an error count is logged.

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_py.rs.

Usage:
    qsv py map [options] -n <expression> [<input>]
    qsv py map [options] <new-column> <expression> [<input>]
    qsv py map --helper <file> [options] <new-column> <expression> [<input>]
    qsv py filter [options] <expression> [<input>]
    qsv py map --help
    qsv py filter --help
    qsv py --help

py argument:
    <expression>           Can either be a Python expression, or if it starts with
                           "file:" or ends with ".py" - the filepath from which to
                           load the Python expression.
                           Note that argument expects a SINGLE expression, and not
                           a full-blown Python script. Use the --helper option
                           to load helper code that you can call from the expression.

py options:
    -f, --helper <file>    File containing Python code that's loaded into the 
                           qsv_uh Python module. Functions with a return statement
                           in the file can be called with the prefix "qsv_uh".
                           The returned value is used in the map or filter operation.

    -b, --batch <size>     The number of rows per batch to process before
                           releasing memory and acquiring a new GILpool.
                           Set to 0 to process the entire file in one batch.
                           [default: 50000]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. Namely, it will be sorted with the rest
                           of the rows. Otherwise, the first row will always
                           appear as the header row in the output.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -p, --progressbar      Show progress bars. Not valid for stdin.
```
## rename

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
## replace

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

  $ qsv replace '([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})' /
   '<EMAIL>' file.csv


For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_replace.rs.

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
## reverse

```text
Reverses rows of CSV data.

Useful for cases when there is no column that can be used for sorting in reverse order,
or when keys are not unique and order of rows with the same key needs to be preserved.

Note that if the CSV is not indexed, this operation will require reading all of the
CSV data into memory

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
## sample

```text
Randomly samples CSV data.

It supports eight sampling methods:
- RESERVOIR: the default sampling method when NO INDEX is present and no sampling method
  is specified. Visits every CSV record exactly once, using MEMORY PROPORTIONAL to the
  sample size (k) - O(k).
  https://en.wikipedia.org/wiki/Reservoir_sampling

- INDEXED: the default sampling method when an INDEX is present and no sampling method
  is specified. Uses random I/O to sample efficiently, as it only visits records selected
  by random indexing, using MEMORY PROPORTIONAL to the sample size (k) - O(k).
  https://en.wikipedia.org/wiki/Random_access

- BERNOULLI: the sampling method when the --bernoulli option is specified.
  Each record has an independent probability p of being selected, where p is
  specified by the <sample-size> argument. For example, if p=0.1, then each record
  has a 10% chance of being selected, regardless of the other records. The final
  sample size is random and follows a binomial distribution. Uses CONSTANT MEMORY - O(1).
  When sampling from a remote URL, processes the file in chunks without downloading it
  entirely, making it especially efficient for sampling large remote files.
  https://en.wikipedia.org/wiki/Bernoulli_sampling

- SYSTEMATIC: the sampling method when the --systematic option is specified.
  Selects every nth record from the input, where n is the integer part of <sample-size>
  and the fraction part is the percentage of the population to sample.
  For example, if <sample-size> is 10.5, it will select every 10th record and 50% of the
  population. If <sample-size> is a whole number (no fractional part), it will select
  every nth record for the whole population. Uses CONSTANT memory - O(1). The starting
  point can be specified as "random" or "first". Useful for time series data or when you
  want evenly spaced samples.
  https://en.wikipedia.org/wiki/Systematic_sampling

- STRATIFIED: the sampling method when the --stratified option is specified.
  Stratifies the population by the specified column and then samples from each stratum.
  Particularly useful when a population has distinct subgroups (strata) that are
  heterogeneous within but homogeneous between in terms of the variable of interest. 
  For example, if you want to sample 1,000 records from a population of 100,000 across the US,
  you can stratify the population by US state and then sample 20 records from each stratum.
  This will ensure that you have a representative sample from each of the 50 states.
  The sample size must be a whole number. Uses MEMORY PROPORTIONAL to the
  number of strata (s) and samples per stratum (k) as specified by <sample-size> - O(s*k).
  https://en.wikipedia.org/wiki/Stratified_sampling

- WEIGHTED: the sampling method when the --weighted option is specified.
  Samples records with probabilities proportional to values in a specified weight column.
  Records with higher weights are more likely to be selected. For example, if you have
  sales data and want to sample transactions weighted by revenue, high-value transactions
  will have a higher chance of being included. Non-numeric weights are treated as zero.
  The weights are automatically normalized using the maximum weight in the dataset.
  Specify the desired sample size with <sample-size>. Uses MEMORY PROPORTIONAL to the
  sample size (k) - O(k).
  "Weighted random sampling with a reservoir" https://doi.org/10.1016/j.ipl.2005.11.003

- CLUSTER: the sampling method when the --cluster option is specified.
  Samples entire groups of records together based on a cluster identifier column.
  The number of clusters is specified by the <sample-size> argument.
  Useful when records are naturally grouped (e.g., by household, neighborhood, etc.).
  For example, if you have records grouped by neighborhood and specify a sample size of 10,
  it will randomly select 10 neighborhoods and include ALL records from those neighborhoods
  in the output. This ensures that natural groupings in the data are preserved.
  Uses MEMORY PROPORTIONAL to the number of clusters (c) - O(c).
  https://en.wikipedia.org/wiki/Cluster_sampling

- TIMESERIES: the sampling method when the --timeseries option is specified.
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

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_sample.rs.

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
                            - standard: Use the standard RNG.
                              1.5 GB/s throughput.
                            - faster: Use faster RNG using the Xoshiro256Plus algorithm.
                              8 GB/s throughput.
                            - cryptosecure: Use cryptographically secure HC128 algorithm.
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

                           REMOTE FILE OPTIONS:
    --user-agent <agent>   Specify custom user agent to use when the input is a URL.
                           It supports the following variables -
                           $QSV_VERSION, $QSV_TARGET, $QSV_BIN_NAME, $QSV_KIND and $QSV_COMMAND.
                           Try to follow the syntax here -
                           https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
    --timeout <secs>       Timeout for downloading URLs in seconds. If 0, no timeout is used.
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
## schema

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

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_schema.rs.

Usage:
    qsv schema [options] [<input>]
    qsv schema --help

Schema options:
    --enum-threshold <num>     Cardinality threshold for adding enum constraints.
                               Enum constraints are compiled for String & Integer types.
                               [default: 50]
    -i, --ignore-case          Ignore case when compiling unique values for enum constraints.
                               Do note however that the `validate` command is case-sensitive
                               when validating against enum constraints.
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
                               in the field match the detected format.
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
## search

```text
Filters CSV data by whether the given regex matches a row.

The regex is applied to selected field in each row, and if any field matches,
then the row is written to the output, and the number of matches to stderr.

The columns to search can be limited with the '--select' flag (but the full row
is still written to the output if there is a match).

Returns exitcode 0 when matches are found, returning number of matches to stderr.
Returns exitcode 1 when no match is found, unless the '--not-one' flag is used.

When --quick is enabled, no output is produced and exitcode 0 is returned on 
the first match.

When the CSV is indexed, a faster parallel search is used.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_search.rs.

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
                           but will instead flag the found rows in a new
                           column named <column>, with the row numbers
                           of the matched rows and 0 for the non-matched rows.
                           If column is named M, only the M column will be written
                           to the output, and only matched rows are returned.
    -Q, --quick            Return on first match with an exitcode of 0, returning
                           the row number of the first match to stderr.
                           Return exit code 1 if no match is found.
                           No output is produced.
    --preview-match <arg>  Preview the first N matches or all the matches found in
                           N milliseconds, whichever occurs first. Returns the preview to
                           stderr. Output is still written to stdout or --output as usual.
                           Only applicable when CSV is NOT indexed, as it's read sequentially.
                           Forces a sequential search, even if the CSV is indexed.
    -c, --count            Return number of matches to stderr.
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
                           Automatically sets --quiet.
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
                           Only applicable when CSV is NOT indexed.
    -q, --quiet            Do not return number of matches to stderr.
```
## searchset

```text
Filters CSV data by whether the given regex set matches a row.

Unlike the search operation, this allows regex matching of multiple regexes 
in a single pass.

The regexset-file is a plain text file with multiple regexes, with a regex on 
each line.

The regex set is applied to each field in each row, and if any field matches,
then the row is written to the output, and the number of matches to stderr.

The columns to search can be limited with the '--select' flag (but the full row
is still written to the output if there is a match).

Returns exitcode 0 when matches are found, returning number of matches to stderr.
Returns exitcode 1 when no match is found, unless the '--not-one' flag is used.

When --quick is enabled, no output is produced and exitcode 0 is returned on 
the first match.

When the CSV is indexed, a faster parallel search is used.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_searchset.rs.

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
    -c, --count                Return number of matches to stderr.
                               Ignored if --json is enabled.
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
    -q, --quiet                Do not return number of matches to stderr.
```
## select

```text
Select columns from CSV data efficiently.

This command lets you manipulate the columns in CSV data. You can re-order,
duplicate, reverse or drop them. Columns can be referenced by index or by
name if there is a header row (duplicate column names can be disambiguated with
more indexing). Column ranges can also be specified. Finally, columns can be
selected using regular expressions.

  Select the first and fourth columns:
  $ qsv select 1,4

  Select the first 4 columns (by index and by name):
  $ qsv select 1-4
  $ qsv select Header1-Header4

  Ignore the first 2 columns (by range and by omission):
  $ qsv select 3-
  $ qsv select '!1-2'

  Select the third column named 'Foo':
  $ qsv select 'Foo[2]'

  Select the first and last columns, _ is a special character for the last column:
  $ qsv select 1,_

  Reverse the order of columns:
  $ qsv select _-1

  Sort the columns lexicographically (i.e. by their byte values)
  $ qsv select 1- --sort

  Select some columns and then sort them:
  $ qsv select 1,4,5-7 --sort

  Randomly shuffle the columns:
  $ qsv select 1- --random
  # with a seed
  $ qsv select 1- --random --seed 42

  Select some columns and then shuffle them with a seed:
  $ qsv select 1,4,5-7 --random --seed 42

  Select columns using a regex using '/<regex>/':
  # select columns starting with 'a'
  $ qsv select /^a/
  # select columns with a digit
  $ qsv select '/^.*\d.*$/'
  # remove SSN, account_no and password columns
  $ qsv select '!/SSN|account_no|password/'

  Re-order and duplicate columns arbitrarily using different types of selectors:
  $ qsv select 3-1,Header3-Header1,Header1,Foo[2],Header1

  Quote column names that conflict with selector syntax:
  $ qsv select '\"Date - Opening\",\"Date - Actual Closing\"'

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_select.rs.

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
## slice

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

Examples:
  # Slice from the 3rd record to the end
  $ qsv slice --start 2 data.csv

  # Slice the first three records
  $ qsv slice --start 0 --end 2 data.csv
  $ qsv slice --len 3 data.csv
  $ qsv slice -l 3 data.csv

  # Slice the last record
  $ qsv slice -s -1 data.csv

  # Slice the last 10 records
  $ qsv slice -s -10 data.csv

  # Get everything except the last 10 records
  $ qsv slice -s -10 --invert data.csv

  # Slice the first three records of the last 10 records
  $ qsv slice -s -10 -l 3 data.csv

  # Slice the second record
  $ qsv slice --index 1 data.csv
  $ qsv slice -i 1 data.csv

  # Slice from the second record, two records
  $ qsv slice -s 1 --len 2 data.csv

  # Slice records 10 to 20 as JSON
  $ qsv slice -s 9 -e 19 --json data.csv
  $ qsv slice -s 9 -l 10 --json data.csv

  # Slice records 1 to 9 and 21 to the end as JSON
  $ qsv slice -s 9 -l 10 --invert --json data.csv

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will not be interpreted
                           as headers. Otherwise, the first row will always
                           appear in the output as the header row.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
```
## sniff

```text
Quickly sniff the first n rows and infer CSV metadata (delimiter, header row, number of
preamble rows, quote character, flexible, is_utf8, average record length, number of records,
content length and estimated number of records if sniffing a URL, file size, number of fields,
field names & data types) using a Viterbi algorithm. (https://en.wikipedia.org/wiki/Viterbi_algorithm)

`sniff` is also a mime type detector, returning the detected mime type, file size and
last modified date. If --no-infer is enabled, it doesn't even bother to infer the CSV's schema.
This makes it useful for accelerated CKAN harvesting and for checking stale/broken resource URLs.

It detects more than 120 mime types, including CSV, MS Office/Open Document files, JSON, XML, 
PDF, PNG, JPEG and specialized geospatial formats like GPX, GML, KML, TML, TMX, TSX, TTML.
see https://docs.rs/file-format/latest/file_format/#reader-features

NOTE: This command "sniffs" a CSV's schema by sampling the first n rows (default: 1000)
of a file. Its inferences are sometimes wrong if the the file is too small to infer a pattern
or if the CSV has unusual formatting - with atypical delimiters, quotes, etc.

In such cases, selectively use the --sample, --delimiter and --quote options to improve
the accuracy of the sniffed schema.

If you want more robust, guaranteed schemata, use the "schema" or "stats" commands
instead as they scan the entire file. However, they only work on local files and well-formed
CSVs, unlike `sniff` which can work with remote files, various CSV dialects and is very fast
regardless of file size.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_sniff.rs.

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
                             [default: 1000]
    --prefer-dmy             Prefer to parse dates in dmy format. Otherwise, use mdy format.
                             Ignored when --no-infer is enabled.
    -d, --delimiter <arg>    The delimiter for reading CSV data.
                             Specify this when the delimiter is known beforehand,
                             as the delimiter inferencing algorithm can sometimes fail.
                             Must be a single ascii character.
    --quote <arg>        The quote character for reading CSV data.
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
## sort

```text
Sorts CSV data in lexicographical, natural, numerical, reverse, unique or random order.

Note that this requires reading all of the CSV data into memory. If
you need to sort a large file that may not fit into memory, use the
extsort command instead.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_sort.rs.

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
    -R, --reverse           Reverse order
    -i, --ignore-case       Compare strings disregarding case
    -u, --unique            When set, identical consecutive lines will be dropped
                            to keep only one line per sorted value.

                            RANDOM SORTING OPTIONS:
    --random                Randomize (scramble) the data by row
    --seed <number>         Random Number Generator (RNG) seed to use if --random is set
    --rng <kind>            The RNG algorithm to use if --random is set.
                            Three RNGs are supported:
                            - standard: Use the standard RNG.
                              1.5 GB/s throughput.
                            - faster: Use faster RNG using the Xoshiro256Plus algorithm.
                              8 GB/s throughput.
                            - cryptosecure: Use cryptographically secure HC128 algorithm.
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
## sqlp

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
## stats

```text
Compute summary statistics & infers data types for each column in a CSV.

> IMPORTANT: `stats` is heavily optimized for speed. It ASSUMES the CSV is well-formed & UTF-8 encoded.
> This allows it to employ numerous performance optimizations (skip repetitive UTF-8 validation, skip
> bounds checks, cache results, etc.) that may result in undefined behavior if the CSV is not well-formed.
> All these optimizations are GUARANTEED to work with well-formed CSVs.
> If you encounter problems generating stats, use `qsv validate` FIRST to confirm the CSV is valid.

> For MAXIMUM PERFORMANCE, create an index for the CSV first with 'qsv index' to enable multithreading,
> or set --cache-threshold option or set the QSV_AUTOINDEX_SIZE environment variable to automatically
> create an index when the file size is greater than the specified size (in bytes).

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
It returns "*ALL" if all the values are unique, and only returns a preview of the first
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
in <FILESTEM>.stats.csv & if the --stats-json option is used, <FILESTEM>.stats.csv.data.jsonl
(e.g., qsv stats nyc311.csv will create nyc311.stats.csv & nyc311.stats.csv.data.jsonl).
The arguments used to generate the cached stats are saved in <FILESTEM>.stats.csv.jsonl.

If stats have already been computed for the input file with similar arguments and the file
hasn't changed, the stats will be loaded from the cache instead of recomputing it.

These cached stats are also used by other qsv commands (currently `describegpt`, `frequency`,
`joinp`, `pivotp`, `schema`, `sqlp` & `tojsonl`) to work smarter & faster.
If the cached stats are not current (i.e., the input file is newer than the cached stats),
the cached stats will be ignored and recomputed. For example, see the "boston311" test files in
https://github.com/dathere/qsv/blob/4529d51273218347fef6aca15ac24e22b85b2ec4/tests/test_stats.rs#L608.

Examples:

Compute "streaming" statistics for the "nyc311.csv" file:
  $ qsv stats nyc311.csv

Compute all statistics for the "nyc311.csv" file:
  $ qsv stats --everything nyc311.csv
  $ qsv stats -E nyc311.csv
  $ qsv stats -E nyc311.tsv // Tab-separated
  $ qsv stats -E nyc311.tab // Tab-separated
  $ qsv stats -E nyc311.ssv // Semicolon-separated
  $ qsv stats -E nyc311.csv.sz // Snappy-compressed CSV
  $ qsv stats -E nyc311.tsv.sz // Snappy-compressed Tab-separated
  $ qsv stats -E nyc311.ssv.sz // Snappy-compressed Semicolon-separated

Compute all statistics for "nyc311.tsv", inferring dates using default date column name patterns:
  $ qsv stats -E --infer-dates nyc311.tsv

Compute all statistics for "nyc311.tab", inferring dates only for columns with "_date" & "_dte"
in the column names:
  $ qsv stats -E --infer-dates --dates-whitelist _date,_dte nyc311.tab

In addition, also infer boolean data types for "nyc311.ssv" file:
  $ qsv stats -E --infer-dates --dates-whitelist _date --infer-boolean nyc311.ssv

In addition to basic "streaming" stats, also compute cardinality for the "nyc311.csv" file:
  $ qsv stats --cardinality nyc311.csv

Prefer DMY format when inferring dates for the "nyc311.csv" file:
  $ qsv stats -E --infer-dates --prefer-dmy nyc311.csv

Infer data types only for the "nyc311.csv" file:
  $ qsv stats --typesonly nyc311.csv

Infer data types only, including boolean and date types for the "nyc311.csv" file:
  $ qsv stats --typesonly --infer-boolean --infer-dates nyc311.csv

If the polars feature is enabled, support additional tabular file formats and
compression formats:
  $ qsv stats data.parquet // Parquet
  $ qsv stats data.avro // Avro
  $ qsv stats data.jsonl // JSON Lines
  $ qsv stats data.json (will only work with a JSON Array)
  $ qsv stats data.csv.gz // Gzipped CSV
  $ qsv stats data.tab.zlib // Zlib-compressed Tab-separated
  $ qsv stats data.ssv.zst // Zstd-compressed Semicolon-separated

Automatically create an index for the "nyc311.csv" file to enable multithreading
if it's larger than 5MB and there is no existing index file:
  $ qsv stats -E --cache-threshold -5000000 nyc311.csv

Auto-create a TEMPORARY index for the "nyc311.csv" file to enable multithreading
if it's larger than 5MB and delete the index and the stats cache file after the stats run:
  $ qsv stats -E --cache-threshold -5000005 nyc311.csv

Prompt for CSV/TSV/TAB file to compute stats for:
  $ qsv prompt -F tsv,csv,tab | qsv stats -E | qsv table

Prompt for a file to save the stats to in the ~/Documents directory:
  $ qsv stats -E nyc311.csv | qsv prompt -d ~/Documents --fd-output

Prompt for both INPUT and OUTPUT files in the ~/Documents dir with custom prompts:
  $ qsv prompt -m 'Select a CSV file to summarize' -d ~/Documents -F csv | \
      qsv stats -E --infer-dates | \
      qsv prompt -m 'Save summary to...' -d ~/Documents --fd-output --save-fname summarystats.csv

For more examples, see https://github.com/dathere/qsv/tree/master/resources/test
For more info, see https://github.com/dathere/qsv/wiki/Supplemental#stats-command-output-explanation

Usage:
    qsv stats [options] [<input>]
    qsv stats --help

stats options:
    -s, --select <arg>        Select a subset of columns to compute stats for.
                              See 'qsv select --help' for the format details.
                              This is provided here because piping 'qsv select'
                              into 'qsv stats' will prevent the use of indexing.
    -E, --everything          Compute all statistics available EXCEPT --dataset-stats.
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

    --round <decimal_places>  Round statistics to <decimal_places>. Rounding is done following
                              Midpoint Nearest Even (aka "Bankers Rounding") rule.
                              https://docs.rs/rust_decimal/latest/rust_decimal/enum.RoundingStrategy.html
                              If set to the sentinel value 9999, no rounding is done.
                              For dates - range, stddev & IQR are always at least 5 decimal places as
                              they are reported in days, and 5 places gives us millisecond precision.
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
                              Set to "all" to inspect ALL fields for
                              date/datetime types. Ignored if --infer-dates is false.

                              Note that false positive date matches WILL most likely occur
                              when using "all" as unix epoch timestamps are just numbers.
                              Be sure to only use "all" if you know ALL the columns you're
                              inspecting are dates, boolean or string fields.

                              To avoid false positives, preprocess the file first
                              with the `datefmt` command to convert unix epoch timestamp
                              columns to RFC3339 format.
                              [default: date,time,due,open,close,created]
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
 -c, --cache-threshold <arg>  Controls the creation of stats cache files.
                                - when greater than 1, the threshold in milliseconds before caching
                                  stats results. If a stats run takes longer than this threshold,
                                  the stats results will be cached.
                                - 0 to suppress caching.
                                - 1 to force caching.
                                - a negative number to automatically create an index when
                                  the input file size is greater than abs(arg) in bytes.
                                  If the negative number ends with 5, it will delete the index
                                  file and the stats cache file after the stats run. Otherwise,
                                  the index file and the cache files are kept.
                              [default: 5000]
    --vis-whitespace          Visualize whitespace characters in the output.
                              See https://github.com/dathere/qsv/wiki/Supplemental#whitespace-markers
                              for the list of whitespace markers.
    --dataset-stats           Compute dataset statistics (e.g. row count, column count, file size and
                              fingerprint hash) and add them as additional rows to the output, with
                              the qsv__ prefix and an additional qsv__value column.
                              The --everything option DOES NOT enable this option.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -n, --no-headers       When set, the first row will NOT be interpreted
                           as column names. i.e., They will be included
                           in statistics.
    -d, --delimiter <arg>  The field delimiter for READING CSV data.
                           Must be a single character. (default: ,)
    --memcheck             Check if there is enough memory to load the entire
                           CSV into memory using CONSERVATIVE heuristics.
                           This option is ignored when computing default, streaming
                           statistics, as it is not needed.
```
## validate

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

When a duplicate combination is found, the validation will fail and the error message will indicate
which columns had duplicate combinations (named columns first, then indexed columns). The invalid
records will be written to the .invalid file, while valid records will be written to the .valid file.

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

RFC 4180 VALIDATION MODE:
========================

If run without a JSON Schema file, the CSV is validated for RFC 4180 CSV standard compliance
(see https://github.com/dathere/qsv#rfc-4180-csv-standard).

It also confirms if the CSV is UTF-8 encoded.

For both modes, returns exit code 0 when the CSV file is valid, exitcode > 0 otherwise.
If all records are valid, no output files are produced.

For examples, see the tests included in this file (denoted by '#[test]') or see
https://github.com/dathere/qsv/blob/master/tests/test_validate.rs.

Usage:
    qsv validate schema [--no-format-validation] [<json-schema>]
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
    --fail-fast                Stops on first error.
    --valid <suffix>           Valid record output file suffix. [default: valid]
    --invalid <suffix>         Invalid record output file suffix. [default: invalid]
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
