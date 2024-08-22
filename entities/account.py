from typing import List

import pandas as pd
from uuid import uuid4
from dataclasses import dataclass, field, asdict


@dataclass
class Account:
    id: int
    name: str
    category: str
    uuid: str = field(default_factory=lambda: str(uuid4()))

    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        account = cls(
            id=data['id'],
            name=data['name'],
            category=data['category'],

        )
        if 'uuid' in data:
            account.uuid = data['uuid']
        return account

    @classmethod
    def create_dataframe(cls, accounts: List['Account']) -> pd.DataFrame:
        return pd.DataFrame([asdict(account) for account in accounts])

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> List['Account']:
        return [cls.from_dict(row.to_dict()) for _, row in df.iterrows()]
