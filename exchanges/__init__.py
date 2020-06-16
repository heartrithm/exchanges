from .apis.bitfinex import BitfinexApi


def exchange_factory(exchange):
    if exchange == "bitfinex":
        return BitfinexApi
