from typing import List, Optional

import pandas as pd
from uuid import uuid4
from dataclasses import dataclass, field, asdict


@dataclass
class HCP:
    id: str
    name: str
    email: str
    specialty: str
    franchise: str

    account_uuid: Optional[str] = None
    uuid: str = field(default_factory=lambda: str(uuid4()))

    @classmethod
    def from_dict(cls, data: dict) -> 'HCP':
        hcp = cls(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            specialty=data['specialty'],
            franchise=data['franchise']
        )
        if 'uuid' in data:
            hcp.uuid = data['uuid']
        return hcp

    @classmethod
    def create_dataframe(cls, hcps: List['HCP']) -> pd.DataFrame:
        return pd.DataFrame([asdict(hcp) for hcp in hcps])

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> List['HCP']:
        return [cls.from_dict(row.to_dict()) for _, row in df.iterrows()]
