# qsv readstat

<small>v29.0.0</small>

```text
Convert SAS, Stata & SPSS files to CSV.

EXPERIMENTAL: the readers this command is built on are young. Spot-check the
output against your source files before relying on a conversion, and please
report anything that looks wrong.

Supported input formats:
    SAS     .sas7bdat, .xpt, .xpt5, .xpt8
    Stata   .dta
    SPSS    .sav, .zsav, .por

Coded values are written as their underlying codes, not their labels, so the
conversion is lossless. SPSS durations (DTIME) are written as their number of
seconds, as SPSS stores them. Use --value-labels to decode them instead. SAS keeps
its value labels in a separate .sas7bcat format catalog, which --value-labels
finds next to the data file, or --sas7bcat names.

User-defined missing values ("sentinels") - SAS's .A to .Z & ._, Stata's .a
to .z, SPSS's declared missing codes - become empty cells by default, like any
other missing value. Use --sentinels-as to keep them. Without it, a warning
says how many sentinels were dropped & where. Counting them reads files on a
single thread, and SPSS files whole (see --batch), so it is skipped when the
option --jobs is above 1, and for SPSS files holding over about 128 MB of
data. As SPSS files declare their missing values, the warning then names the
variables that do instead. SAS & Stata files don't, so they get no warning.

The variable metadata these formats carry - variable labels, value labels,
missing-value codes, measure & display settings - can be dumped instead of the
data with --metadata. Or --dictionary writes it alongside the data, as a JSON
Schema data dictionary of the CSV written: variable labels become titles,
value labels an enum (when they cover every value written), and the rest is
kept under "x-qsv". It has the shape 'qsv describegpt --dictionary' writes, so
'qsv validate' & 'qsv viz smart --dictionary' read it - without an LLM.

Only part of a file can be read: --select picks variables, which the readers
skip over without decoding, and --offset, --limit & --sample pick rows. Stata,
uncompressed SPSS & SAS transport files jump straight to the --offset. SAS
datasets & compressed SPSS files still pass over the rows before it (decoding
them, for a SAS dataset at --jobs > 1), and .por files are read whole. Reading
stops once --limit is reached.

  Convert a SAS dataset to CSV:
    qsv readstat data.sas7bdat > data.csv

  Convert an SPSS file, decoding coded values to their labels:
    qsv readstat --value-labels survey.sav -o survey.csv

  Keep the sentinel codes of a SAS dataset, in a <name>_null column after each
  numeric variable:
    qsv readstat --sentinels-as value data.sas7bdat

  Keep them in the variables' own columns instead:
    qsv readstat --sentinels-as value --sentinels-embedded data.sas7bdat

  Keep the sentinels of two SPSS variables as their labels, leaving the other
  values as codes:
    qsv readstat --sentinels-as label --sentinels-columns q1,q2 survey.sav

  Read three variables & the first 1000 rows of a wide SPSS file:
    qsv readstat --select id,age,income --limit 1000 survey.sav

  Read every variable from "q1" to "q20", in file order:
    qsv readstat --select q1-q20 survey.sav

  Read every variable except two (a leading ! excludes those listed):
    qsv readstat --select '!notes,comments' survey.sav

  Take a reproducible random sample of 500 rows, in file order:
    qsv readstat --sample 500 --seed 42 data.sas7bdat

  Convert an SPSS file & write its data dictionary, then chart it with the
  variable labels as titles:
    qsv readstat --dictionary survey.schema.json survey.sav -o survey.csv
    qsv viz smart --dictionary survey.schema.json survey.csv

  Dump the variable dictionary of a Stata file:
    qsv readstat --metadata pretty-json panel.dta

  Dump the metadata of just two variables:
    qsv readstat --metadata json --select age,income panel.dta

  Pipe straight into another qsv command:
    qsv readstat data.sas7bdat | qsv stats

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_readstat.rs.

Usage:
    qsv readstat [options] [<input>]
    qsv readstat --help

readstat options:
    --metadata <fmt>       Dump variable metadata instead of the data.
                           Valid values: none, csv, json, pretty-json.
                           For SAS, the value labels are included when a
                           format catalog is used (see --value-labels).
                           [default: none]
    --value-labels         Decode coded values to their label strings
                           (e.g. 1 becomes "Male") instead of writing the
                           underlying codes. For SAS .sas7bdat files, the
                           labels come from the format catalog: the file
                           named by --sas7bcat, else <name>.sas7bcat or
                           formats.sas7bcat next to the data file. Not
                           supported for .xpt files.
    --sas7bcat <file>      The SAS format catalog (.sas7bcat) holding the
                           value labels of a .sas7bdat file, for use by
                           the options --value-labels, --sentinels-as label
                           & --metadata. It only names the catalog, so the
                           data needs one of the first two.
    --dictionary <file>    Also write a JSON Schema data dictionary of the
                           CSV written to <file>. Name it <stem>.schema.json
                           after the CSV & 'qsv viz smart' finds it on its
                           own. It describes the data as written, so the
                           other options shape it too: the types follow
                           the option --compress-numeric, the enums
                           follow --value-labels, & so on.
    --compress-numeric     Write float variables that only ever hold whole
                           numbers as integers, without the ".0" (e.g. 3.0
                           becomes 3). SPSS stores every number as a float, so
                           this matters most for SPSS files. It is decided per
                           variable, over the rows written: one value like 2.5
                           keeps the ".0" on every row of that variable. The
                           file is read twice - once to check the values.
                           With sentinel labels embedded, a variable with a
                           label that reads as a number (e.g. "1.0") keeps its
                           ".0", so the label is not rewritten.
    --sentinels-as <what>  Keep sentinels instead of writing them as empty
                           cells. Each eligible variable gets a <name>_null
                           column right after it, holding the sentinel of each
                           row that has one & empty otherwise.
                           Valid values: none, value, label.
                             none  - write them as empty cells, without the
                                     check & its warning.
                             value - the sentinel's code (e.g. .A or 99).
                             label - the sentinel's value label if it has one,
                                     else its code.
                           label labels only the sentinels: other values stay
                           codes unless --value-labels is also given.
                           SAS takes its sentinel labels from the format
                           catalog, found as for --value-labels. For SPSS,
                           value cannot be combined with --value-labels.
                           Not supported for .xpt & .por files. Tracking
                           sentinels reads files on a single thread, so the
                           option --jobs has no effect, and reads SPSS .sav
                           & .zsav files whole (see --batch).
    --sentinels-embedded   Write each sentinel into its variable's own column
                           instead of a <name>_null column. Those columns then
                           mix numbers & sentinels. Requires --sentinels-as.
    --sentinels-columns <list>  Comma-separated variables to keep sentinels
                           for. Requires --sentinels-as. By default, every
                           eligible variable: the numeric ones for SAS &
                           Stata, those with declared missing values for SPSS.
    --select <cols>        The variables to read, in the order given, using
                           qsv's select syntax: names, 1-based indices,
                           ranges (q1-q20) & /regex/, or a leading ! to
                           read every variable except those listed. See
                           'qsv select --help' for the full syntax. Variables
                           left out are skipped by the reader. Also applies
                           to the option --metadata, which then lists only
                           these variables.
    --offset <n>           Skip the first <n> rows. [default: 0]
    --limit <n>            Write at most <n> rows, counted after the
                           rows skipped by --offset.
    --sample <n>           Write a random sample of <n> rows, in file order,
                           drawn from the rows --offset & --limit select.
                           If there are no more than <n> such rows, all of
                           them are written.
    --seed <number>        Seed the random number generator of --sample,
                           so the same sample is drawn every time.
    -j, --jobs <arg>       Number of reader threads. [default: 1]
                           Raising it speeds up large uncompressed files at the
                           cost of memory, as out-of-order chunks have to be
                           buffered to keep the rows in source order. Row order
                           is preserved either way.
    -b, --batch <size>     Number of rows to read into memory at a time.
                           Does not apply to SPSS portable (.por) files - they
                           have no chunked reader upstream, so they are read
                           whole & memory scales with the file. Nor does it
                           apply to .sav & .zsav files while their sentinels
                           are tracked, which also reads them whole: with
                           the option --sentinels-as value or label, or by
                           the sentinel check when a variable declares
                           missing values & the file holds at most about
                           128 MB of data (see --sentinels-as none).
                           [default: 50000]

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The delimiter to use when writing CSV data.
                           Must be a single character. (default: ,)
```
