import unittest

import requests_mock

from exchanges import exchange_factory

from ..base import ExchangeApiException


class KuCoinTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.client = exchange_factory("kucoin")("passphrase", "key", "secret")
        super(KuCoinTest, self).__init__(*args, **kwargs)

    def test_kucoin_status(self):
        # One real call without a mock
        try:
            self.assertEqual(
                self.client.brequest(1, "status"), {"code": "200000", "data": {"msg": "", "status": "open"}}
            )
        except ExchangeApiException:
            print("Error fetching KuCoin platform status. Network down?")

    def test_retrieve_lending_data(self):
        with requests_mock.mock() as m:
            m.get(
                "https://api.kucoin.com/api/v1/margin/trade/last",
                text='{"code": "200000", "data": [{"tradeId": "123", "currency": "USDT", "size": 100}]}',
            )
            result = self.client.brequest(1, "margin/trade/last", params={"currency": "USDT"})
            self.assertEqual(result, {"code": "200000", "data": [{"tradeId": "123", "currency": "USDT", "size": 100}]})

    def test_auth(self):
        with requests_mock.mock() as m:
            m.delete("https://api.kucoin.com/api/v1/orders", json={"code": "200000", "data": {"cancelledOrderIds": []}})
            result = self.client.brequest(1, "orders", True, "DELETE")
            self.assertEqual(result, {"code": "200000", "data": {"cancelledOrderIds": []}})
            self.assertEqual(self.client.passphrase, "passphrase")
