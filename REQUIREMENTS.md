This toolkit focuses on wrapping the datHere QSV Data Wrangling command line utility
It is assume that you have QSV is installed and available in your PATH.

## Python QSV commands wrappers
- For each of the QSV commands, generate a Python class that can be used to execute the command.
- The classes and underlying methods are stored in the  `src/dartfx/qsv/cmd.py` file.
- The classes should be structured in a way that is easy to read and maintain.
- The list of commands can be found by running `qsv --list`.
- Run the shell command with the `--help` parameter to get its description and the list of arguments and options.
  e.g. `qsv stats --help`
- If a command already exists, verify that its description and input parameters are up to date with the latest version of QSV
- The commands should be sorted alphabetically, except for generic/inherited classes, which may appear at the top. 

## QSV commands documentation
- For each of the QSV commands, generate a markdown documentation file in the `references/cmd` directory.
- Each documentation file:
  - should be named and titled after the command it documents.
  - should only include the output of the command line options in a code block.
- Maintain a `references/cmd/README.md` file that lists all the commands and their documentation files.
  - The list should be sorted alphabetically.
  - The list should include the name of the command and a short description.

## Sphinx project documentation
- Generate or update the project documentation using Sphinx.
- The documentation should be stored in the `docs/source` directory.
- The documentation should be structured in a way that is easy to read and maintain.
- The documentation should be generated using the `make html` command.
