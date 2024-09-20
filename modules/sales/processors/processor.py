from abc import abstractmethod, ABC
from typing import Optional

import pandas as pd


class Processor(ABC):

    def __init__(self, input_data_frame):
        self.processing_data_frame = self._prepare_data_frame(input_data_frame)

    @abstractmethod
    def process(self) -> Optional[pd.DataFrame]:
        pass

    @abstractmethod
    def _prepare_data_frame(self, data: pd.DataFrame) -> pd.DataFrame:
        pass
