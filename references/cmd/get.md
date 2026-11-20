# qsv get

<small>v29.0.0</small>

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
