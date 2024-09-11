from typing import List, Optional

import pandas as pd
from uuid import uuid4
from dataclasses import dataclass, field, asdict


@dataclass
class Employee:
    name: str
    email: str
    uuid: str = field(default_factory=lambda: str(uuid4()))

    @classmethod
    def from_dict(cls, data: dict) -> 'Employee':
        hcp = cls(
            name=data['name'],
            email=data['email']
        )
        if 'uuid' in data:
            hcp.uuid = data['uuid']
        return hcp

    @classmethod
    def create_dataframe(cls, employees: List['Employee']) -> pd.DataFrame:
        return pd.DataFrame([asdict(employee) for employee in employees])

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> List['Employee']:
        return [cls.from_dict(row.to_dict()) for _, row in df.iterrows()]
