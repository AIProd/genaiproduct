from dataclasses import dataclass
from typing import Optional

from entities.qlik_url_generator import QlikSenseURLGenerator


@dataclass
class HCP:
    id: str
    name: str
    email: str
    specialty: str
    franchise: str
    ter_target: str
    uuid: str
    product_priorities: str
    lat: float
    lon: float
    account_uuid: Optional[str] = None

    @property
    def qlik_url(self):
        return QlikSenseURLGenerator.generate_account_page_url(str(self.id))
