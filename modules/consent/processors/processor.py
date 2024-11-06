from typing import Optional

import polars as pl
from abc import ABC, abstractmethod
from modules.consent import constants


class Processor(ABC):
    def __init__(self, input_lazy_frame: pl.LazyFrame):
        self.column_mapping = constants.COLUMN_MAPPING
        self.processing_lazy_frame = self._prepare_data_frame(input_lazy_frame)

    @abstractmethod
    def process(self) -> Optional[pl.LazyFrame]:
        pass

    @abstractmethod
    def _prepare_data_frame(self, data: pl.LazyFrame) -> pl.LazyFrame:
        pass
