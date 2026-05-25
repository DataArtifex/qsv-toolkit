from __future__ import annotations

from pathlib import Path

import typer

from dartfx.qsv.utils import generate_ddi_codebook

app = typer.Typer(help="Dartfx CLI for QSV tools.")


@app.callback()
def main() -> None:
    """
    Dartfx CLI for QSV tools.
    """
    pass


@app.command()
def toddic(
    csv_path: Path = typer.Argument(
        ...,
        help="Path to the source CSV file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to write the generated DDI XML. If not specified, outputs to stdout.",
        writable=True,
    ),
    ddi_version: str = typer.Option(
        "2.6",
        "--ddi-version",
        "-v",
        help="DDI-Codebook version ('2.5' or '2.6').",
    ),
    categorical_threshold: int = typer.Option(
        20,
        "--categorical-threshold",
        "-t",
        help="Cardinality threshold for auto-detecting categorical variables.",
    ),
    categorical_column: list[str] | None = typer.Option(
        None,
        "--categorical-column",
        "-c",
        help="Explicit list of categorical column names. Can be specified multiple times, or comma-separated.",
    ),
    stats_data: Path | None = typer.Option(
        None,
        "--stats-data",
        help="Path to pre-computed stats data file (JSON, JSONL, or CSV).",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    schema_data: Path | None = typer.Option(
        None,
        "--schema-data",
        help="Path to pre-computed schema data file (JSON).",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    frequency_data: Path | None = typer.Option(
        None,
        "--frequency-data",
        help="Path to pre-computed frequency data file (JSON).",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
) -> None:
    """
    Generate a DDI-Codebook XML document from a CSV file using QSV outputs.
    """
    # Parse categorical columns, allowing comma-separated values in addition to multiple flags
    flat_categorical_columns: list[str] | None = None
    if categorical_column:
        flat_categorical_columns = []
        for col in categorical_column:
            if "," in col:
                flat_categorical_columns.extend(c.strip() for c in col.split(",") if c.strip())
            else:
                if col.strip():
                    flat_categorical_columns.append(col.strip())

    try:
        xml_content = generate_ddi_codebook(
            csv_path=csv_path,
            stats_data=stats_data,
            schema_data=schema_data,
            frequency_data=frequency_data,
            version=ddi_version,
            output_xml_path=output,
            categorical_threshold=categorical_threshold,
            categorical_columns=flat_categorical_columns,
        )
        if not output:
            typer.echo(xml_content)
    except Exception as e:
        typer.echo(f"Error generating DDI codebook: {e}", err=True)
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
