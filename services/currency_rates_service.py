from abc import ABC, abstractmethod

from models.currency import Currency, Reference


class ICurrencyRatesService(ABC):
    @abstractmethod
    async def get(self, symbol: str, reference: Reference) -> Currency | None:
        raise 'Not implemented'

    @abstractmethod
    async def get_all(self, reference: Reference) -> dict[str, Currency] | None:
        raise 'Not implemented'
