import json
import os
from pydantic import BaseModel, computed_field, Field 
from typing import Optional

class DataProduct(BaseModel):
    root: str

class DataFile(BaseModel):
    product: DataProduct
    name: str
    subpath: str = "" # path to file under data product root

    @computed_field
    @property
    def stem(self) -> str:
        return os.path.splitext(self.filename)[0]

    @computed_field
    @property
    def dirpath(self) -> str:
        return os.path.join(self.product.root, self.subpath)

    @computed_field
    @property
    def extension(self) -> str:
        return os.path.splitext(self.name)[1].lower()[1:]

    @computed_field
    @property
    def filename(self) -> str:
        return self.name
    
    @computed_field
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
    is_ascii: bool = False
    sum: Optional[float] = None
    min: Optional[str] = None
    max: Optional[str] = None
    range: Optional[float] = None
    sort_order: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    sum_length: Optional[int] = None
    avg_length: Optional[float] = None
    stddev_length: Optional[float] = None
    variance_length: Optional[float] = None
    cv_length: Optional[float] = None
    mean: Optional[float] = None
    sem: Optional[float] = None
    stddev: Optional[float] = None
    variance: Optional[float] = None
    cv: Optional[float] = None
    nullcount: int
    max_precision: Optional[int] = None
    sparsity: Optional[float] = None
    mad: Optional[float] = None
    lower_outer_fence: Optional[float] = None
    lower_inner_fence: Optional[float] = None
    q1: Optional[float] = None
    q2_median: Optional[float] = None
    q3: Optional[float] = None
    iqr: Optional[float] = None
    upper_inner_fence: Optional[float] = None
    upper_outer_fence: Optional[float] = None
    skewness: Optional[float] = None
    cardinality: int
    uniqueness_ratio: Optional[float] = None
    mode: Optional[str] = None
    mode_count: Optional[int] = None
    mode_occurrences: Optional[int] = None
    antimode: Optional[str] = None
    antimode_count: Optional[int] = None
    antimode_occurrences: Optional[int] = None
    
    model_config = {
        "populate_by_name": True,  # Allow using both field name and alias
    }

class QsvStatsFile(BaseModel):
    """QSV statistics file associated with a data file."""
    datafile: DataFile # The associated data file
    _data: list[QsvStatsDataModel]

    @computed_field
    @property
    def jsonl_filename(self) -> str:
        return f"{self.datafile.stem}.stats.{self.datafile.extension}.data.jsonl"
    
    @computed_field
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
        with open(self.jsonl_filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        json_data = json.loads(line)
                        self._data.append(QsvStatsDataModel(**json_data))
                    except json.JSONDecodeError as e:
                        raise json.JSONDecodeError(
                            f"Invalid JSON on line {line_num}: {e.msg}",
                            e.doc,
                            e.pos
                        )
        return self._data

class QsvFrequencyFile(BaseModel):
    pass

class QsvSchemaFile(BaseModel):
    pass

class QsvPolarsSchemaFile(BaseModel):
    pass



