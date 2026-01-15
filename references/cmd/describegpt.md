# describegpt

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
