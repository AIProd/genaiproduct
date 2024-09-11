from abc import abstractmethod, ABC
from typing import Optional

import pandas as pd

from modules.consent.utils import FindingResult


class Finding(ABC):
    @abstractmethod
    def generate(self, data: pd.DataFrame) -> Optional[FindingResult]:
        pass