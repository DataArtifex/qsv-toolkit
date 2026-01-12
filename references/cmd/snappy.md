# qsv snappy

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
