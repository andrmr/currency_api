from dataclasses import dataclass
from enum import Enum


class Reference(Enum):
    EUR = 'eur'
    USD = 'usd'


@dataclass
class Currency:
    def __init__(self):
        pass

    symbol: str
    name: str
    value: float
    value_1d: float
    value_7d: float
    value_30d: float
