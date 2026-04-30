# qsv blake3

<small>19.1.0</small>
```text
Compute cryptographic hashes of files using blake3.

This command is functionally similar to b3sum, providing fast, parallel blake3 hashing
of one or more files. It supports keyed hashing, key derivation, variable-length output,
and checksum verification. When no file is given, or when "-" is given, reads stdin.

For examples, see https://github.com/dathere/qsv/blob/master/tests/test_blake3.rs.

Usage:
    qsv blake3 [options] [<input>...]
    qsv blake3 --help

blake3 options:
    --keyed              Use the keyed mode, reading the 32-byte key from stdin.
                         When using --keyed, file arguments are required (cannot
                         also read data from stdin).
    --derive-key <CTX>   Use the key derivation mode, with the given context string.
                         Cannot be used with --keyed.
    -l, --length <LEN>   The number of output bytes, before hex encoding.
                         [default: 32]
    --no-mmap            Disable memory mapping. Also disables multithreading.
    --no-names           Omit filenames in the output.
    --raw                Write raw output bytes to stdout, rather than hex.
                         Only a single input is allowed. --no-names is implied.
    --tag                Output checksums in tagged format.
    -c, --check          Read blake3 sums from the input files and check them.
    -j, --jobs <arg>     The number of jobs to run in parallel for hashing.
                         When not set, uses the number of CPUs detected.
                         Set to 1 to disable multithreading.

Common options:
    -h, --help           Display this message
    -o, --output <file>  Write output to <file> instead of stdout.
    -q, --quiet          Skip printing OK for each checked file.
                         Must be used with --check.
```
