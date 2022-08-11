import json
import os

import httpx
from asyncache import cached
from cachetools import TTLCache

from models.currency import Currency, Reference
from services.currency_rates_service import ICurrencyRatesService


class CryptoRatesRatesService(ICurrencyRatesService):
    async def get(self, symbol: str, reference: Reference) -> Currency | None:
        rates = await _get_rates(reference)
        return rates.get(symbol.upper(), None)

    async def get_all(self, reference: Reference) -> dict[str, Currency] | None:
        return await _get_rates(reference)


@cached(TTLCache(float('inf'), 21600))
async def _get_rates(reference: Reference) -> dict[str, Currency]:
    async with httpx.AsyncClient() as client:
        apikey_nomics = os.getenv('APIKEY_NOMICS')
        request = client.get(
            f'https://api.nomics.com/v1/currencies/ticker?key={apikey_nomics}&interval=1d,7d,30d&convert={reference.value.upper()}&per-page=100&page=1')
        response = await request

        if response.status_code != httpx.codes.OK:
            return {}

    currencies = {}
    for obj in json.loads(response.text):
        c = Currency()
        c.symbol = obj['symbol'].upper()
        c.name = obj['name']
        c.value = float(obj['price'])
        c.value_1d = round(c.value - float(obj['1d']['price_change']), 4)
        c.value_7d = round(c.value - float(obj['7d']['price_change']), 4)
        c.value_30d = round(c.value - float(obj['30d']['price_change']), 4)
        c.value = round(c.value, 4)

        currencies[c.symbol] = c

    currencies = {k: v for k, v in sorted(currencies.items())}
    return currencies
