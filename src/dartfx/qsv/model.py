import json
import os

from pydantic import BaseModel, Field, computed_field


class DataProduct(BaseModel):
    root: str


class DataFile(BaseModel):
    product: DataProduct
    name: str
    subpath: str = ""  # path to file under data product root

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stem(self) -> str:
        return os.path.splitext(self.filename)[0]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dirpath(self) -> str:
        return os.path.join(self.product.root, self.subpath)

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
        return os.path.join(self.product.root, self.subpath, self.name)


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


class QsvFrequencyFile(BaseModel):
    pass


class QsvSchemaFile(BaseModel):
    pass


class QsvPolarsSchemaFile(BaseModel):
    pass
