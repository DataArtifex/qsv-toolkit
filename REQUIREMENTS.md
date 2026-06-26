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
- Make sure a 'help' method is available for each command.
- Do include a class for the `qsv` command itself, which is the entry point for the QSV command line tool.

## QSV commands documentation
- Maintain a `references/cmd/README.md` file that lists all the QSV documented commands and their documentation files.
  - The list should be sorted alphabetically.
  - The list should include the name of the command and a short description.

## Sphinx project documentation
- Generate or update the project documentation using Sphinx.
- The documentation should be stored in the `docs/source` directory.
- The documentation should be structured in a way that is easy to read and maintain.
- The documentation should be generated using the `make html` command.

## File Conversion and Metadata Extraction (SAS, Stata, SPSS)
- Support reading statistical data formats including SAS (`.sas7bdat`, `.sas7bcat`, `.xport`), Stata (`.dta`), and SPSS (`.sav`, `.zsav`, `.por`) using `pyreadstat`.
- Support converting these formats to and from CSV to allow processing with QSV.
- Extract file-level and variable-level metadata (such as variable labels, value labels, and formats) from these formats to generate metadata schemas or DDI-Codebook XML.
