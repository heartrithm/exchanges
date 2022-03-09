import unittest

import requests_mock

from exchanges import exchange_factory


class TardisTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.client = exchange_factory("tardis")("key", "secret")
        super(TardisTest, self).__init__(*args, **kwargs)

    def test_get_ftx_futures_data_from_tardis(self):
        with requests_mock.mock() as m:
            m.get(
                "https://api.tardis.dev/v1/data-feeds/ftx",
                text='''2020-06-01T00:00:05.1876755Z {"channel":"instrument","generated":true,"market":"BTC-PERP","type":"update","data":{"stats":{"nextFundingRate":1e-06,"nextFundingTime":"2020-06-01T00:00:00+00:00","openInterest":11206.9761,"volume":24277.5613},"info":{"ask":9442.5,"bid":9439.5,"change1h":-0.0013225413955456806,"change24h":-0.02705767149409885,"changeBod":-0.024644794626711444,"description":"Bitcoin Perpetual Futures","enabled":true,"expired":false,"expiryDescription":"Perpetual","group":"perpetual","imfFactor":0.002,"index":9450.74824289,"last":9442.5,"lowerBound":8978.0,"marginPrice":9439.0,"mark":9439.0,"name":"BTC-PERP","perpetual":true,"positionLimitWeight":1.0,"postOnly":false,"priceIncrement":0.5,"sizeIncrement":0.0001,"type":"perpetual","underlying":"BTC","underlyingDescription":"Bitcoin","upperBound":9923.0,"volume":24277.5613,"volumeUsd24h":231369008.9906}}}'''
            )
            result = self.client.brequest(1, "data-feeds/ftx", params={"symbols": ["BTC-PERP"], "filters": '[%7B"channel":"instrument"%7D]'})
            self.assertEqual(result["data"]["stats"]["openInterest"], 11206.9761)
            self.assertEqual(result["data"]["info"]["underlying"], "BTC")
