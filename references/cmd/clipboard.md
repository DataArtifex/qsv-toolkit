# qsv clipboard

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

Usage:
    qsv clipboard [options]
    qsv clipboard --help

clip options:
    -s, --save             Save output to clipboard.
Common options:
    -h, --help             Display this message
```
