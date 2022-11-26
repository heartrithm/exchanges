import unittest

import requests_mock

from exchanges import exchange_factory


class SFOXTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.client = exchange_factory("sfox")("key", "secret")
        super(SFOXTest, self).__init__(*args, **kwargs)

    def test_symbols(self):
        self.assertEqual("ethusd", self.client.get_symbol("USD", "ETH"))
        self.assertEqual("ETH/USD", self.client.get_pair("ethusd"))
        self.assertEqual("ETH/USD", self.client.unmake_symbol("ethusd"))
        self.assertEqual("ethusd", self.client.make_symbol("ETH/USD"))

    def test_auth_v3(self):
        with requests_mock.mock() as m:
            m.post(
                requests_mock.ANY,
                text='{"balances": [{"asset": "BTC", "free": "0.10730199", "locked": "0.00000000"}]}',
            )
            result = self.client.brequest(endpoint="balances", authenticate=True, method="POST")
            self.assertEqual(result, {"balances": [{"asset": "BTC", "free": "0.10730199", "locked": "0.00000000"}]})

    def test__urls(self):
        """Ensure candles vs. real API calls hit the right URLs"""
        with requests_mock.mock() as m:
            m.get("https://chartdata.sfox.com/candlesticks", text='{"noop": true}')
            self.client.brequest(endpoint="candlesticks", method="GET")
        with requests_mock.mock() as m:
            m.get("https://api.sfox.com/v1/everything_else", text='{"noop": true}')
            self.client.brequest(1, endpoint="everything_else", method="GET")
