from .apis.bitfinex import BitfinexApi
from .apis.binance import BinanceApi, BinanceMarginApi, BinanceFuturesApi
from .apis.sfox import SFOXApi


def exchange_factory(exchange):
    if exchange == "bitfinex":
        return BitfinexApi
    if exchange == "binance":
        return BinanceApi
    if exchange == "binance_margin":
        return BinanceMarginApi
    if exchange == "binance_futures":
        return BinanceFuturesApi
    if exchange == "sfox":
        return SFOXApi
