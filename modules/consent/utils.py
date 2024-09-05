from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class FindingResult:
    account_uuid: str
    hcp_uuid: str
    employee_uuid: str
    type: str
    details: str
    timestamp: datetime = field(default_factory=lambda: datetime.now())

