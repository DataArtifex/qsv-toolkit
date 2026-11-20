# qsv describegpt

<small>v29.0.0</small>

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
