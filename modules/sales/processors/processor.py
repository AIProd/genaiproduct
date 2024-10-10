from abc import abstractmethod, ABC
from typing import Optional

import polars as pl


class Processor(ABC):

    def __init__(self, input_lazy_frame: pl.LazyFrame):
        self.processing_lazy_frame = self._prepare_data_frame(input_lazy_frame)
        self.output_df = pl.LazyFrame()

    @abstractmethod
    def process(self) -> Optional[pl.LazyFrame]:
        pass

    @abstractmethod
    def _prepare_data_frame(self, data: pl.LazyFrame) -> pl.LazyFrame:
        pass
