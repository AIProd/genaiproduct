from dataclasses import dataclass


@dataclass
class Account:
    id: int
    name: str
    category: str
    street: str
    city: str
    zip: str
    uuid: str
