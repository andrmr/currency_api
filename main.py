from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from models.currency import Currency, Reference
from services.crypto_rates_service import CryptoRatesRatesService
from services.currency_rates_service import ICurrencyRatesService
from services.fiat_rates_service import FiatRatesRatesService

limiter = Limiter(key_func=get_remote_address, default_limits=["3/minute"])
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

fiat_rates: ICurrencyRatesService = FiatRatesRatesService()
crypto_rates: ICurrencyRatesService = CryptoRatesRatesService()


@app.on_event('startup')
async def on_startup():
    pass


@app.get("/fiat/{reference}",
         tags=["Fiat"],
         summary="Get all rates",
         description="Returns all available rates for the specified reference.")
async def get_fiat(request: Request, reference: Reference) -> dict[str, Currency] | None:
    return await fiat_rates.get_all(reference)


@app.get("/fiat/{reference}/{symbol}",
         tags=["Fiat"],
         summary="Get single rate",
         description="Returns the rate for the specified currency/reference pair.")
async def get_fiat(request: Request, symbol: str, reference: Reference) -> Currency | None:
    return await fiat_rates.get(symbol, reference)


@app.get("/crypto/{reference}",
         tags=["Crypto"],
         summary="Get all rates",
         description="Returns all available rates for the specified reference.")
async def get_crypto(request: Request, reference: Reference) -> dict[str, Currency] | None:
    return await crypto_rates.get_all(reference)


@app.get("/crypto/{reference}/{symbol}",
         tags=["Crypto"],
         summary="Get single rate",
         description="Returns the rate for the specified currency/reference pair.")
async def get_crypto(request: Request, symbol: str, reference: Reference) -> Currency | None:
    return await crypto_rates.get(symbol, reference)
