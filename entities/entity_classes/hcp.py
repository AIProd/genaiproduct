from dataclasses import dataclass
from typing import Optional


@dataclass
class HCP:
    id: str
    name: str
    email: str
    specialty: str
    franchise: str
    ter_target: str
    uuid: str
    account_uuid: Optional[str] = None
