import json
import os
from typing import Any

from pydantic import BaseModel, Field, computed_field


class Repository(BaseModel):
    root: str


class DataFile(BaseModel):
    repository: Repository
    name: str
    subpath: str = ""  # path to file under data product root

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stem(self) -> str:
        return os.path.splitext(self.filename)[0]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dirpath(self) -> str:
        return os.path.join(self.repository.root, self.subpath)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def extension(self) -> str:
        return os.path.splitext(self.name)[1].lower()[1:]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def filename(self) -> str:
        return self.name

    @computed_field  # type: ignore[prop-decorator]
    @property
    def filepath(self) -> str:
        return os.path.join(self.repository.root, self.subpath, self.name)


class CsvDataFile(DataFile):
    pass


class ParquetDataFile(DataFile):
    pass


class SpssDataFile(DataFile):
    pass


class StataDataFile(DataFile):
    pass


class SasDataFile(DataFile):
    pass


class QsvStatsDataModel(BaseModel):
    """Statistics data for a field/column."""

    field: str
    type: str = Field(alias="type")
    is_ascii: bool | None = None
    sum: float | None = None
    min: str | None = None
    max: str | None = None
    range: float | None = None
    sort_order: str | None = None
    sortiness: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    sum_length: int | None = None
    avg_length: float | None = None
    stddev_length: float | None = None
    variance_length: float | None = None
    cv_length: float | None = None
    mean: float | None = None
    sem: float | None = None
    geometric_mean: float | None = None
    harmonic_mean: float | None = None
    stddev: float | None = None
    variance: float | None = None
    cv: float | None = None
    nullcount: int
    n_negative: int | None = None
    n_zero: int | None = None
    n_positive: int | None = None
    max_precision: int | None = None
    sparsity: float | None = None
    mad: float | None = None
    lower_outer_fence: float | None = None
    lower_inner_fence: float | None = None
    q1: float | None = None
    q2_median: float | None = None
    q3: float | None = None
    iqr: float | None = None
    upper_inner_fence: float | None = None
    upper_outer_fence: float | None = None
    skewness: float | None = None
    cardinality: int
    uniqueness_ratio: float | None = None
    mode: str | None = None
    mode_count: int | None = None
    mode_occurrences: int | None = None
    antimode: str | None = None
    antimode_count: int | None = None
    antimode_occurrences: int | None = None
    percentiles: str | None = None
    zero_padded_numeric: bool | None = None

    # moarstats fields
    kurtosis: float | None = None
    bimodality_coefficient: float | None = None
    pearson_skewness: float | None = None
    gini_coefficient: float | None = None
    quartile_coefficient_dispersion: float | None = None
    outliers_percentage: float | None = None
    outlier_impact_ratio: float | None = None
    mad_stddev_ratio: float | None = None
    median_mean_ratio: float | None = None
    normalized_entropy: float | None = None

    model_config = {
        "populate_by_name": True,  # Allow using both field name and alias
    }


class QsvStatsFile(BaseModel):
    """QSV statistics file associated with a data file."""

    datafile: DataFile  # The associated data file
    _data: list[QsvStatsDataModel]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def jsonl_filename(self) -> str:
        return f"{self.datafile.stem}.stats.{self.datafile.extension}.data.jsonl"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def jsonl_filepath(self) -> str:
        return os.path.join(self.datafile.dirpath, self.jsonl_filename)

    def load(self) -> list[QsvStatsDataModel]:
        """
        Load statistics data from the JSONL file.

        Returns:
            list[QsvStatsDataModel]: List of statistics data models, one per line in the JSONL file.

        Raises:
            FileNotFoundError: If the stats file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        self._data = []
        with open(self.jsonl_filepath, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        json_data = json.loads(line)
                        self._data.append(QsvStatsDataModel(**json_data))
                    except json.JSONDecodeError as e:
                        raise json.JSONDecodeError(f"Invalid JSON on line {line_num}: {e.msg}", e.doc, e.pos) from e
        return self._data


class QsvFrequencyItem(BaseModel):
    """A single frequency distribution item."""

    value: str
    count: int
    percentage: float


class QsvFrequencyField(BaseModel):
    """Frequency distribution data for a field/column."""

    field: str
    cardinality: int
    frequencies: list[QsvFrequencyItem]


class QsvFrequencyMetadata(BaseModel):
    """Metadata for the frequency cache file."""

    arg_input: str | None = None
    flag_high_card_threshold: int | None = None
    flag_high_card_pct: int | None = None
    flag_no_nulls: bool | None = None
    flag_no_headers: bool | None = None
    flag_delimiter: str | None = None
    record_count: int | None = None
    column_count: int | None = None
    date_generated: str | None = None
    qsv_version: str | None = None
    selection_signature: str | None = None
    canonical_input_path: str | None = None


class QsvFrequencyFile(BaseModel):
    """QSV frequency file associated with a data file."""

    datafile: DataFile  # The associated data file
    _metadata: QsvFrequencyMetadata | None = None
    _data: list[QsvFrequencyField] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def jsonl_filename(self) -> str:
        return f"{self.datafile.stem}.freq.{self.datafile.extension}.data.jsonl"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def jsonl_filepath(self) -> str:
        return os.path.join(self.datafile.dirpath, self.jsonl_filename)

    @property
    def metadata(self) -> QsvFrequencyMetadata | None:
        """Get the parsed frequency metadata."""
        return self._metadata

    def load(self) -> list[QsvFrequencyField]:
        """
        Load frequency data from the JSONL file.

        Returns:
            list[QsvFrequencyField]: List of frequency field data models.

        Raises:
            FileNotFoundError: If the frequency file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        self._data = []
        self._metadata = None

        with open(self.jsonl_filepath, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return self._data

        # Parse first line as metadata
        try:
            meta_data = json.loads(lines[0])
            self._metadata = QsvFrequencyMetadata(**meta_data)
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback if first line is not metadata but a field record
            try:
                field_data = json.loads(lines[0])
                if "field" in field_data:
                    self._data.append(QsvFrequencyField(**field_data))
            except Exception:
                raise e from None

        # Parse subsequent lines as fields
        for line_num, line in enumerate(lines[1:], 2):
            try:
                field_data = json.loads(line)
                self._data.append(QsvFrequencyField(**field_data))
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"Invalid JSON on line {line_num}: {e.msg}", e.doc, e.pos) from e

        return self._data


class QsvSchemaProperty(BaseModel):
    """JSON Schema property definition for a CSV column."""

    description: str | None = None
    type: list[str] | str
    minimum: float | None = None
    maximum: float | None = None
    min_length: int | None = Field(default=None, alias="minLength")
    max_length: int | None = Field(default=None, alias="maxLength")
    enum: list[Any] | None = None
    pattern: str | None = None
    format: str | None = None

    model_config = {
        "populate_by_name": True,
    }


class QsvSchemaFile(BaseModel):
    """QSV JSON Schema file associated with a data file."""

    datafile: DataFile  # The associated data file

    schema_version: str = Field(default="https://json-schema.org/draft/2020-12/schema", alias="$schema")
    title: str | None = None
    description: str | None = None
    type: str = "object"
    properties: dict[str, QsvSchemaProperty] = {}
    required: list[str] = []

    model_config = {
        "populate_by_name": True,
    }

    @computed_field  # type: ignore[prop-decorator]
    @property
    def schema_filename(self) -> str:
        return f"{self.datafile.name}.schema.json"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def schema_filepath(self) -> str:
        return os.path.join(self.datafile.dirpath, self.schema_filename)

    def load(self) -> "QsvSchemaFile":
        """
        Load the JSON Schema data from the file.

        Returns:
            QsvSchemaFile: Self with loaded properties.

        Raises:
            FileNotFoundError: If the schema file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        with open(self.schema_filepath, encoding="utf-8") as f:
            data = json.load(f)

        # Update self fields with loaded data
        self.schema_version = data.get("$schema", self.schema_version)
        self.title = data.get("title", self.title)
        self.description = data.get("description", self.description)
        self.type = data.get("type", self.type)

        self.properties = {k: QsvSchemaProperty(**v) for k, v in data.get("properties", {}).items()}
        self.required = data.get("required", [])

        return self


class QsvPolarsSchemaFile(BaseModel):
    """QSV Polars Schema file associated with a data file."""

    datafile: DataFile  # The associated data file
    fields: dict[str, str] = {}
    metadata: dict[str, Any] | None = None

    model_config = {
        "populate_by_name": True,
    }

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pschema_filename(self) -> str:
        return f"{self.datafile.name}.pschema.json"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pschema_filepath(self) -> str:
        return os.path.join(self.datafile.dirpath, self.pschema_filename)

    def load(self) -> "QsvPolarsSchemaFile":
        """
        Load the Polars Schema data from the file.

        Returns:
            QsvPolarsSchemaFile: Self with loaded properties.

        Raises:
            FileNotFoundError: If the pschema file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        with open(self.pschema_filepath, encoding="utf-8") as f:
            data = json.load(f)

        self.fields = data.get("fields", {})
        self.metadata = data.get("metadata", None)

        return self
