from ..base import ExchangeApiException
from ..binance import BinanceApi, BinanceMarginApi
from exchanges import exchange_factory

import requests_mock
import unittest


class BinanceTest(unittest.TestCase):
    def test_symbols(self):
        c = exchange_factory("binance")()
        self.assertEqual("ETHUSDT", c.get_symbol("USDT", "ETH"))
        self.assertEqual("ETH/USDT", c.get_pair("ETHUSDT"))
        self.assertEqual("ETH/USDT", c.unmake_symbol("ETHUSDT"))
        self.assertEqual("ETHUSDT", c.make_symbol("ETH/USDT"))

    def test_public_candles_v3(self):
        c = exchange_factory("binance")()
        with requests_mock.mock() as m:
            m.get("https://api.binance.com/api/v3/klines?symbol=ETHUSDT", text='{"open":"543.0"}')
            self.assertEqual(c.brequest(3, "klines", params={"symbol": "ETHUSDT"}), {"open": "543.0"})

    def test_public_v3(self):
        c = BinanceApi()
        # One real call without a mock
        try:
            self.assertEqual(c.brequest(2, "ping"), [1])
        except ExchangeApiException:  # pragma: no cover
            print("Error fetching binance platform status. Network down?")

    def test_auth_v3(self):
        c = BinanceApi("my key", "my secret")
        with requests_mock.mock() as m:
            m.post(
                requests_mock.ANY,
                text='{"balances": [{"asset": "BTC", "free": "0.10730199", "locked": "0.00000000"}]}',
            )
            result = c.brequest(3, endpoint="balances", authenticate=True, method="POST")
            self.assertEqual(result, {"balances": [{"asset": "BTC", "free": "0.10730199", "locked": "0.00000000"}]})

    def test_auth_margin_api(self):
        c = BinanceMarginApi("my key", "my secret")
        with requests_mock.mock() as m:
            m.post(
                requests_mock.ANY, text='{"amount": "26505.468", "borrowLimit": "200000"}',
            )
            result = c.brequest(1, endpoint="margin/maxBorrowable", authenticate=True, method="POST")
            self.assertEqual(result, {"amount": "26505.468", "borrowLimit": "200000"})
