# qsv pro

```text
Interact with qsv pro API. Learn more about qsv pro at: https://qsvpro.dathere.com.

- qsv pro must be running for this command to work as described.
- Some features of this command require a paid plan of qsv pro and may require an Internet connection.

The qsv pro command has subcommands:
    lens:     Run csvlens on a local file in a new Alacritty terminal emulator window (Windows only).
    workflow: Import a local file into the qsv pro Workflow (Workflow must be open).

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
