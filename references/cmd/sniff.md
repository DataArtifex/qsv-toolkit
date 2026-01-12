# qsv sniff

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
