import asyncio
import json
import os
from datetime import datetime, timedelta
from enum import Enum

from asyncache import cached
from cachetools import TTLCache
from httpx import AsyncClient, Response, codes

from models.currency import Currency, Reference
from services.currency_rates_service import ICurrencyRatesService


class FiatRatesRatesService(ICurrencyRatesService):
    async def get(self, symbol: str, reference: Reference) -> Currency | None:
        rates = await _get_rates(reference)
        return rates.get(symbol.upper(), None)

    async def get_all(self, reference: Reference) -> dict[str, Currency] | None:
        return await _get_rates(reference)


@cached(TTLCache(float('inf'), 3600))
async def _get_rates(reference: Reference) -> dict[str, Currency]:
    async with AsyncClient() as client:
        requests = [client.get(_path_for_timepoint(reference, t)) for t in _TimePoint]
        responses = await asyncio.gather(*requests)

    def parse_response(r: Response) -> dict[str, float]:
        if r.status_code != codes.OK:
            return {}
        return json.loads(r.text)[reference.value]

    rates: dict[_TimePoint, dict[str, float]] = {t: parse_response(r) for t, r in zip(_TimePoint, responses)}
    available_currencies = await _get_currency_list()

    currencies = {}
    for symbol, name in available_currencies.items():
        symbol = symbol.lower()

        if symbol not in rates[_TimePoint.Latest]:
            continue

        c = Currency()
        c.symbol = symbol.upper()
        c.name = name
        c.value = rates[_TimePoint.Latest][symbol]
        c.value_1d = rates[_TimePoint.OneDay].get(symbol, -1)
        c.value_7d = rates[_TimePoint.SevenDay].get(symbol, -1)
        c.value_30d = rates[_TimePoint.ThirtyDay].get(symbol, -1)

        currencies[c.symbol] = c

    currencies = {k: v for k, v in sorted(currencies.items())}
    return currencies


@cached(TTLCache(float('inf'), 3600))
async def _get_currency_list() -> dict[str, str]:
    async with AsyncClient() as client:
        apikey_getgeoapi = os.getenv('APIKEY_GETGEOAPI')
        response = await client.get(
            f'https://api.getgeoapi.com/v2/currency/list?api_key={apikey_getgeoapi}&format=json')

    if response.status_code != codes.OK:
        return {}

    currencies: dict[str, str] = {s: n for s, n in json.loads(response.text)['currencies'].items()}
    return currencies


class _TimePoint(Enum):
    Latest = 0
    OneDay = 1
    SevenDay = 7
    ThirtyDay = 30


def _path_for_timepoint(reference: Reference, timepoint: _TimePoint) -> str:
    if timepoint == _TimePoint.Latest:
        time_param = 'latest'
    else:
        time_param = (datetime.today() - timedelta(days=timepoint.value)).strftime("%Y-%m-%d")

    return f'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/{time_param}/currencies/{reference.value}.json'
