from .apis.bitfinex import BitfinexApi
from .apis.binance import BinanceApi, BinanceMarginApi, BinanceFuturesApi
from .apis.sfox import SFOXApi


def exchange_factory(exchange):
    if exchange == "bitfinex":
        return BitfinexApi
    elif exchange == "binance":
        return BinanceApi
    elif exchange == "binance_margin":
        return BinanceMarginApi
    elif exchange == "binance_futures":
        return BinanceFuturesApi
    elif exchange == "sfox":
        return SFOXApi
    else:  # pragma: no cover
        raise NotImplementedError(f"Exchange '{exchange}' not supported")
