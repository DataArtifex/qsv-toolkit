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
