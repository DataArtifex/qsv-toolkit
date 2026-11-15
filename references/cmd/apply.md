# qsv apply

<small>v28.0.0</small>

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
