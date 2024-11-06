from dataclasses import dataclass

from entities.google_maps_url_generator import GoogleMapsURLGenerator
from entities.qlik_url_generator import QlikSenseURLGenerator


@dataclass
class Account:
    id: int
    name: str
    category: str
    street: str
    city: str
    zip: str
    uuid: str

    @property
    def map_url(self) -> str:
        return GoogleMapsURLGenerator.generate_url(
            account_name=str(self.name),
            street=str(self.street),
            city=str(self.city),
            zip_code=str(self.zip)
        )

    @property
    def qlik_url(self):
        return QlikSenseURLGenerator.generate_account_page_url(str(self.id))

    @property
    def formatted_address(self):
        return f"{self.street} · {self.zip} {self.city}"
