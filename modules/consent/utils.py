from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class FindingResult:
    account_name: str
    hcp: str
    employee_name: str
    type: str
    details: str
    timestamp: datetime = field(default_factory=lambda: datetime.now())

