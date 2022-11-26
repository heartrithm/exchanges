import hashlib
import hmac
import urllib

from cachetools import TTLCache, cached
from loguru import logger
import arrow
import requests

from .base import BaseExchangeApi, ExchangeApiException


class BinanceApi(BaseExchangeApi):
    api_prefix = "api"

    @cached(cache=TTLCache(maxsize=32, ttl=300))
    def pull_symbols(self):
        logger.info("Calling live binance API for symbols list")
        return requests.get("https://api.binance.com/api/v3/exchangeInfo").json().get("symbols")

    def get_symbol(self, stake_currency, trade_currency):
        return self.make_symbol(trade_currency + "/" + stake_currency)

    def get_pair(self, symbol):
        return self.unmake_symbol(symbol)

    @cached(cache={})
    def unmake_symbol(self, symbol):
        self.symbols = self.pull_symbols()

        our_symbol = [x for x in self.symbols if x["symbol"] == symbol]
        assert our_symbol, f"Trading pair {symbol} not found on Binance."

        return f'{our_symbol[0]["baseAsset"]}/{our_symbol[0]["quoteAsset"]}'

    def make_symbol(self, symbol):
        pieces = symbol.split("/")
        return "{}{}".format(pieces[0], pieces[1])

    def prepare_signed_request(self, headers, params):
        if not params:
            params = {}
        params.update({"timestamp": round(arrow.utcnow().float_timestamp * 1000)})
        params = urllib.parse.urlencode(params)
        signature = (
            hmac.new(bytes(self.secret, "latin-1"), msg=bytes(params, "latin-1"), digestmod=hashlib.sha256)
            .hexdigest()
            .upper()
        )
        params += "&signature=" + signature
        headers.update({"X-MBX-APIKEY": self.key, "signature": signature})
        return headers, params

    def brequest(
        self,
        api_version,
        endpoint=None,
        authenticate=False,
        method="GET",
        params=None,
        data=None,
    ):
        # different from bitfinex support, we support specifying any api version, because binance always
        # seems to have some lengthy transitions.
        assert not endpoint.startswith(
            (f"/{self.api_prefix}", f"{self.api_prefix}")
        ), "endpoint should not be a full path, but the url after sapi/v1/"

        base_url = "https://api.binance.com"
        api_path = f"/{self.api_prefix}/v{api_version}/{endpoint}"

        headers = self.DEFAULT_HEADERS.copy()

        # Required because data for the signature must match the data that is passed in the body as json, even if empty
        data = data or {}

        if authenticate:
            # NOTE cannot change headers or params after this
            headers, params = self.prepare_signed_request(headers, params)

        url = base_url + api_path
        return self.request(url, method, params, data, headers)


class BinanceMarginApi(BinanceApi):
    def __init__(self, *args, **kwargs):
        self.api_prefix = "sapi"
        super().__init__(*args, **kwargs)


class BinanceFuturesApi(BinanceApi):
    def __init__(self, *args, **kwargs):
        self.api_prefix = "fapi"
        super().__init__(*args, **kwargs)


class BinanceException(ExchangeApiException):
    pass
