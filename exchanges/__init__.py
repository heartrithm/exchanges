from .apis.bitfinex import BitfinexApi
from .apis.binance import BinanceApi, BinanceMarginApi


def exchange_factory(exchange):
    if exchange == "bitfinex":
        return BitfinexApi
    if exchange == "binance":
        return BinanceApi
    if exchange == "binance_margin":
        return BinanceMarginApi
