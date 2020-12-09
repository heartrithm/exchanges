from ..base import ExchangeApiException
from exchanges import exchange_factory

import requests_mock
import unittest


class BinanceTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.client = exchange_factory("binance")("key", "secret")
        self.margin_client = exchange_factory("binance_margin")("key", "secret")
        super(BinanceTest, self).__init__(*args, **kwargs)

    def test_symbols(self):
        self.assertEqual("ETHUSDT", self.client.get_symbol("USDT", "ETH"))
        self.assertEqual("ETH/USDT", self.client.get_pair("ETHUSDT"))
        self.assertEqual("ETH/USDT", self.client.unmake_symbol("ETHUSDT"))
        self.assertEqual("ETHUSDT", self.client.make_symbol("ETH/USDT"))

    def test_public_candles_v3(self):
        with requests_mock.mock() as m:
            m.get("https://api.binance.com/api/v3/klines?symbol=ETHUSDT", text='{"open":"543.0"}')
            self.assertEqual(self.client.brequest(3, "klines", params={"symbol": "ETHUSDT"}), {"open": "543.0"})

    def test_public_v3(self):
        # One real call without a mock
        try:
            self.assertEqual(self.client.brequest(2, "ping"), [1])
        except ExchangeApiException:  # pragma: no cover
            print("Error fetching binance platform status. Network down?")

    def test_auth_v3(self):
        with requests_mock.mock() as m:
            m.post(
                requests_mock.ANY,
                text='{"balances": [{"asset": "BTC", "free": "0.10730199", "locked": "0.00000000"}]}',
            )
            result = self.client.brequest(3, endpoint="balances", authenticate=True, method="POST")
            self.assertEqual(result, {"balances": [{"asset": "BTC", "free": "0.10730199", "locked": "0.00000000"}]})

    def test_auth_margin_api(self):
        with requests_mock.mock() as m:
            m.post(
                requests_mock.ANY, text='{"amount": "26505.468", "borrowLimit": "200000"}',
            )
            result = self.margin_client.brequest(1, endpoint="margin/maxBorrowable", authenticate=True, method="POST")
            self.assertEqual(result, {"amount": "26505.468", "borrowLimit": "200000"})
