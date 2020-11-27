from .apis.bitfinex import BitfinexApi
from .apis.binance import BinanceApi


def exchange_factory(exchange):
    if exchange == "bitfinex":
        return BitfinexApi
    if exchange == "binance":
        return BinanceApi
