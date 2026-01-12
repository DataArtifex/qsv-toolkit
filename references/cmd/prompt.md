# qsv prompt

```text
Open a file dialog to pick a file as input or save to an output file.

Examples:
Pick a single file as input to qsv stats using an INPUT file dialog,
pipe into qsv stats using qsv prompt, and browse the stats using qsv lens:

  $ qsv prompt | qsv stats | qsv lens

If you want to save the output of a command to a file using a save file OUTPUT dialog,
pipe into qsv prompt using the --fd-output flag:

  $ qsv prompt -m 'Pick a CSV file to summarize' | qsv stats -E | qsv prompt --fd-output

Prompt for a spreadsheet, and export to CSV using a save file dialog:

  $ qsv prompt -m 'Select a spreadsheet to export to CSV' -F xlsx,xls,ods | \
      qsv excel - | qsv prompt -m 'Save exported CSV to...' --fd-output

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
