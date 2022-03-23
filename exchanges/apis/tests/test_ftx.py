import json
import unittest

import requests_mock

from exchanges import exchange_factory


class FTXTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.client = exchange_factory("ftx")(key="key", secret="secret")
        super(FTXTest, self).__init__(*args, **kwargs)

    def test_get_funding_data(self):
        with requests_mock.mock() as m:
            m.get(
                "https://ftx.com/api/funding_rates",
                text='{"success": true,"result": '
                '[{"future":"BTC-PERP","rate":-0.000013,"time":"2022-01-27T11:00:00+00:00"}]}',
            )
            result = self.client.brequest(1, "funding_rates", params={"future": "BTC-PERP"})
            self.assertEqual(
                result,
                {
                    "success": True,
                    "result": [{"future": "BTC-PERP", "rate": -0.000013, "time": "2022-01-27T11:00:00+00:00"}],
                },
            )

    def test_auth(self):
        with requests_mock.mock() as m:
            m.post(
                "https://ftx.com/api/orders",
                headers={"FTX-KEY": "secret"},
                text=json.dumps(
                    {
                        "success": True,
                        "result": {
                            "createdAt": "2019-03-05T09:56:55.728933+00:00",
                            "filledSize": 0,
                            "future": "XRP-PERP",
                            "id": 9596912,
                            "market": "XRP-PERP",
                            "price": 0.306525,
                            "remainingSize": 31431,
                            "side": "sell",
                            "size": 31431,
                            "status": "open",
                            "type": "limit",
                            "reduceOnly": False,
                            "ioc": False,
                            "postOnly": False,
                            "clientId": None,
                        },
                    }
                ),
            )
            result = self.client.brequest(1, "orders", True, "POST")
            self.assertTrue(result["success"])
