# qsv log

<small>v19.1.0</small>

```text
Logs an MCP tool invocation entry to qsvmcp.log. Only intended for internal use by the
qsv MCP server, not for general CLI use and only available from the qsvmcp binary variant.

This command is used internally by the MCP server to create an audit trail of
tool invocations. Each entry includes the tool name, a prefixed invocation UUID
(with a "s-" prefix for start, "e-" for end), and context (agent's reason or result).

The log file (qsvmcp.log) is written in the current working directory of the
process. When invoked by the MCP server, this is the server's configured working
directory (set via qsv_set_working_dir). Ensure the CWD is consistent to avoid
logs being scattered across directories.

Usage:
    qsv log <tool-name> <invocation-id> [<message>...]
    qsv log --help

Common options:
    -h, --help     Display this message
```
