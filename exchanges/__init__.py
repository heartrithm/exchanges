from .apis.binance import BinanceApi, BinanceFuturesApi, BinanceMarginApi
from .apis.bitfinex import BitfinexApi
from .apis.ftx import FTXApi
from .apis.kucoin import KuCoinApi
from .apis.sfox import SFOXApi
from .apis.shrimpy import ShrimpyApi
from .apis.tardis import TardisApi


def exchange_factory(exchange):
    if exchange == "bitfinex":
        return BitfinexApi
    elif exchange == "binance":
        return BinanceApi
    elif exchange == "binance_margin":
        return BinanceMarginApi
    elif exchange == "binance_futures":
        return BinanceFuturesApi
    elif exchange == "ftx":
        return FTXApi
    elif exchange == "kucoin":
        return KuCoinApi
    elif exchange == "sfox":
        return SFOXApi
    elif exchange == "shrimpy":
        return ShrimpyApi
    elif exchange == "tardis":
        return TardisApi
    else:  # pragma: no cover
        raise NotImplementedError(f"Exchange '{exchange}' not supported")
