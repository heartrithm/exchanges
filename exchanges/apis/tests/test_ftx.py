import unittest

import requests_mock

from exchanges import exchange_factory


class FTXTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.client = exchange_factory("ftx")("key", "secret")
        super(FTXTest, self).__init__(*args, **kwargs)

    def test_get_funding_data(self):
        with requests_mock.mock() as m:
            m.get(
                "https://ftx.com/api/funding_rates",
                text='{"success": true,"result": '
                '[{"future":"BTC-PERP","rate":-0.000013,"time":"2022-01-27T11:00:00+00:00"}]}',
            )
            result = self.client.brequest(1, "funding_rates", params={"future": "BTC-PERP"})
            self.assertEqual(result, {"success": True, "result": [{"future": "BTC-PERP", "rate": -0.000013,
                "time": "2022-01-27T11:00:00+00:00"}]})
