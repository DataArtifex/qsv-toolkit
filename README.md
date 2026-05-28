# QSV Toolkit (`dartfx-qsv`)

[![PyPI - Version](https://img.shields.io/pypi/v/dartfx-qsv.svg)](https://pypi.org/project/dartfx-qsv)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dartfx-qsv.svg)](https://pypi.org/project/dartfx-qsv)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

**QSV Toolkit** is a Python package designed to facilitate integration and interaction with the [QSV](https://github.com/dathere/qsv) open-source data wrangling toolkit from [datHere](https://www.dathere.com).

> [!WARNING]
> This project is in its early development stages. Stability is not guaranteed, and API changes may occur.

## 🚀 Overview

The toolkit provides high-level Python wrappers and Pydantic models for QSV commands, allowing you to orchestrate complex data pipelines directly from Python or Jupyter notebooks while leveraging the performance of the QSV CLI.

## 📋 Requirements

- **Python 3.12+**
- **[QSV CLI](https://github.com/dathere/qsv)**: The `qsv` executable must be installed and available in your `PATH`.

## ⚙️ Installation

### Using `uv` (Recommended)

```bash
uv add dartfx-qsv
```

### Using `pip`

```bash
pip install dartfx-qsv
```

### Local Development

If you are contributing to the toolkit, clone the repository and install it in editable mode:

```bash
git clone https://github.com/DataArtifex/qsv-toolkit.git
cd qsv-toolkit
uv sync
```

## 📖 Usage

The toolkit offers two ways to interact with QSV: a class-based API (preferred) and simplified function wrappers.

### Class-based API

The new class-based API provides better organization and discoverability of command parameters.

```python
from dartfx.qsv import cmd

# Initialize a command
stats_cmd = cmd.Stats(everything=True, infer_dates=True)

# Run the command on a file
output = stats_cmd.run("data.csv")
print(output)

# Select specific columns
select_cmd = cmd.Select(selection="name,age,city")
filtered_csv = select_cmd.run("data.csv")
```

### Function Wrappers (Backward Compatible)

Legacy function wrappers are available for common operations.

```python
from dartfx.qsv import cmd

# Quick index
cmd.index("data.csv")

# Quick stats
json_output = cmd.stats("data.csv", everything=True)
```

### 📊 DDI-Codebook Generation (CLI & API)

The toolkit features a DDI-Codebook XML generation utility that transforms a CSV file and its associated QSV statistics/frequency data into a valid DDI-Codebook (version 2.5 or 2.6) XML document.

#### CLI Usage

After installing the package, the `dartfx-qsv` executable is registered. You can use the `toddic` command to generate DDI XML:

```bash
# Generate DDI 2.6 Codebook to stdout
dartfx-qsv toddic path/to/data.csv

# Save DDI 2.6 Codebook to an XML file
dartfx-qsv toddic path/to/data.csv -o metadata.xml

# Generate DDI 2.5 Codebook with custom categorical columns
dartfx-qsv toddic path/to/data.csv -v 2.5 -c status,gender,country

# Speed up generation by providing pre-computed stats/schema files from QSV
dartfx-qsv toddic path/to/data.csv --stats-data stats.json --schema-data schema.json
```

**Available Options for `toddic`:**

* `CSV_PATH` (Required argument): Path to the source CSV file.
* `-o, --output PATH`: Path to write the generated DDI XML. Defaults to stdout.
* `-v, --ddi-version TEXT`: DDI-Codebook version (`2.5` or `2.6`). Defaults to `2.6`.
* `-t, --categorical-threshold INTEGER`: Threshold for auto-detecting categorical variables. Defaults to `20`.
* `-c, --categorical-column TEXT`: Explicit categorical column name(s). Can be specified multiple times, or comma-separated.
* `--stats-data PATH`: Path to pre-computed stats data file (JSON, JSONL, or CSV).
* `--schema-data PATH`: Path to pre-computed schema data file (JSON).
* `--frequency-data PATH`: Path to pre-computed frequency data file (JSON).

#### Python API Usage

You can also use this feature programmatically in Python code:

```python
from dartfx.qsv.utils import generate_ddi_codebook

# Generate a DDI 2.6 Codebook XML string
xml_string = generate_ddi_codebook(
    csv_path="data.csv",
    version="2.6",
    categorical_threshold=20
)
```

### 🗄️ SQL Script Generation (CLI & API)

The toolkit features a SQL script generation utility that translates a CSV file's inferred schema (using `qsv schema` and optional stats/frequency data) into a DDL script to create and load a database table.

#### CLI Usage

Use the `tosql` command to generate the SQL script:

```bash
# Generate Postgres SQL script to stdout
dartfx-qsv tosql path/to/data.csv

# Save SQLite SQL script to a file
dartfx-qsv tosql path/to/data.csv -f sqlite -o schema.sql

# Generate MySQL SQL script for a custom table name and database schema
dartfx-qsv tosql path/to/data.csv -f mysql -t my_custom_table -s my_db_schema

# Generate script with single or composite primary keys (case-insensitive)
dartfx-qsv tosql path/to/data.csv -pk id,name
```

**Available Options for `tosql`:**

* `CSV_PATH` (Required argument): Path to the source CSV file.
* `-o, --output PATH`: Path to write the generated SQL script. Defaults to stdout.
* `-f, --flavor TEXT`: Target database flavor (`postgres`, `sqlite`, `mysql`, `mssql`, `oracle`, `clickhouse`, `duckdb`, `snowflake`, `bigquery`, `redshift`, `mariadb`). Defaults to `postgres`.
* `-t, --table TEXT`: Custom table name. Defaults to `tbl_<csv-filename>`.
* `-s, --schema TEXT`: Optional database schema name (postgres/mysql only).
* `-pk, --primary-key TEXT`: Primary key column name(s). For composite keys, use comma-separated names.
* `--stats-data PATH`: Path to pre-computed stats data file (JSON, JSONL, or CSV).
* `--schema-data PATH`: Path to pre-computed schema data file (JSON).
* `--frequency-data PATH`: Path to pre-computed frequency data file (JSON).

#### Python API Usage

You can also generate the SQL script programmatically in Python:

```python
from dartfx.qsv import generate_sql

# Generate Postgres DDL and copy commands as a string with a primary key
sql_script = generate_sql(
    csv_path="data.csv",
    flavor="postgres",
    table_name="my_table",
    primary_key=["id", "name"]
)
```

## 🛠 Supported Commands

The toolkit currently wraps over 30 QSV commands, providing access to a wide range of data wrangling operations:

| Command | Description |
|:---|:---|
| **Apply** | Apply series of transformations to a column. |
| **Behead** | Drop a CSV file's header. |
| **Cat** | Concatenate CSV files by row or by column. |
| **Count** | Returns a count of the number of records in the CSV data. |
| **Dedup** | Remove redundant rows. |
| **DescribeGPT** | Inference metadata and provide a summary of the given CSV data using an LLM. |
| **Enum** | Add a new column enumerating CSV lines. |
| **Explode** | Explode rows based on some column separator. |
| **Fill** | Fill empty values. |
| **FixLengths** | Makes all records have same length. |
| **Flatten** | Prints flattened records such that fields are labeled separated by a new line. |
| **Fmt** | Formats CSV data with a custom delimiter or CRLF line endings. |
| **Frequency** | Compute a frequency table of the given CSV data. |
| **Headers** | Show header names. |
| **Index** | Creates an index of the given CSV data. |
| **Join** | Joins two sets of CSV data on the specified columns. |
| **MoarStats** | Computes additional statistics and outlier metadata for CSV data. |
| **Py** | Evaluate a Python expression on CSV data. |
| **Rename** | Rename the columns of CSV data efficiently. |
| **Replace** | Replace patterns in CSV data. |
| **Reverse** | Reverse rows of CSV data. |
| **Sample** | Randomly sample CSV data. |
| **Schema** | Generate JSON Schema or Polars Schema from CSV data. |
| **Search** | Search CSV data with a regex. |
| **SearchSet** | Search CSV data with a regex set. |
| **Select** | Select, re-order, duplicate or drop columns. |
| **Slice** | Slice records from CSV. |
| **Sniff** | Quickly sniff CSV metadata. |
| **Sort** | Sort CSV data in alphabetical, numerical, reverse or random order. |
| **Sqlp** | Run a SQL query against several CSVs using the Pola.rs engine. |
| **Stats** | Computes summary statistics for CSV data. |
| **Validate** | Validate CSV data for RFC4180-compliance or with JSON Schema. |

## 📚 Documentation

Detailed documentation is available in the `docs/` directory.

### Building HTML Documentation

```bash
cd docs
make html
```

The generated documentation will be available at `docs/build/html/index.html`.

## 🤝 Contributing

We welcome contributions! Please see our [AGENTS.md](AGENTS.md) for technical guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the `LICENSE.txt` file for details.
