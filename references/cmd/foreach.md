# qsv foreach

```text
Execute a shell command once per record in a given CSV file.

NOTE: Windows users are recommended to use Git Bash as their terminal when
running this command. Download it from https://git-scm.com/downloads. When installing,
be sure to select "Use Git from the Windows Command Prompt" to ensure that the
necessary Unix tools are available in the terminal.

WARNING: This command can be dangerous. Be careful when using it with
untrusted input.

Or per @thadguidry: 😉
Please ensure when using foreach to use trusted arguments, variables, scripts, etc.
If you don't do due diligence and blindly use untrusted parts... foreach can indeed
become a footgun and possibly fry your computer, eat your lunch, and expose an entire
datacenter to a cancerous virus in your unvetted batch file you grabbed from some
stranger on the internet that runs...FOR EACH LINE in your CSV file. GASP!"

Examples:

Delete all files whose filenames are listed in the filename column:

  $ qsv foreach filename 'rm {}' assets.csv

Execute a command that outputs CSV once per record without repeating headers:

  $ qsv foreach query --unify 'search --year 2020 {}' queries.csv > results.csv

Same as above but with an additional column containing the current value:

  $ qsv foreach query -u -c from_query 'search {}' queries.csv > results.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_foreach.rs.

Usage:
    qsv foreach [options] <column> <command> [<input>]
    qsv foreach --help

foreach arguments:
    column      The column to use as input for the command.
    command     The command to execute. Use "{}" to substitute the value
                of the current input file line.
                If you need to execute multiple commands, use a shell
                script. See foreach_multiple_commands_with_shell_script()
                in tests/test_foreach.rs for an example.
    input       The CSV file to read. If not provided, will read from stdin.

foreach options:
    -u, --unify                If the output of the executed command is a CSV,
                               unify the result by skipping headers on each
                               subsequent command. Does not work when --dry-run is true.
    -c, --new-column <name>    If unifying, add a new column with given name
                               and copying the value of the current input file line.
    --dry-run <file|boolean>   If set to true (the default for safety reasons), the commands are
                               sent to stdout instead of executing them.
                               If set to a file, the commands will be written to the specified
                               text file instead of executing them. 
                               Only if set to false will the commands be actually executed.
                               [default: true]

Common options:
    -h, --help             Display this message
    -n, --no-headers       When set, the file will be considered to have no
                           headers.
    -d, --delimiter <arg>  The field delimiter for reading CSV data.
                           Must be a single character. (default: ,)
    -p, --progressbar      Show progress bars. Not valid for stdin.
```
