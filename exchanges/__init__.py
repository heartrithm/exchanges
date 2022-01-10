from .apis.binance import BinanceApi, BinanceFuturesApi, BinanceMarginApi
from .apis.bitfinex import BitfinexApi
from .apis.kucoin import KucoinApi
from .apis.sfox import SFOXApi
from .apis.shrimpy import ShrimpyApi


def exchange_factory(exchange):
    if exchange == "bitfinex":
        return BitfinexApi
    elif exchange == "binance":
        return BinanceApi
    elif exchange == "binance_margin":
        return BinanceMarginApi
    elif exchange == "binance_futures":
        return BinanceFuturesApi
    elif exchange == "kucoin":
        return KucoinApi
    elif exchange == "sfox":
        return SFOXApi
    elif exchange == "shrimpy":
        return ShrimpyApi
    else:  # pragma: no cover
        raise NotImplementedError(f"Exchange '{exchange}' not supported")
