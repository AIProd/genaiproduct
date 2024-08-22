from abc import abstractmethod, ABC
from typing import Optional, List

import pandas as pd

from modules.sales.utils import FindingResult


class Finding(ABC):
    @abstractmethod
    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:
        pass