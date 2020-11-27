# from ..base import ExchangeApiException
# from ..binance import BinanceApi, binanceNonceException
from exchanges import exchange_factory

# import requests_mock
import unittest


class BinanceTest(unittest.TestCase):
    # def test_auth_v1(self):
    #    c = BinanceApi("my key", "my secret")
    #    with requests_mock.mock() as m:
    #        m.post("https://api.binance.com/v1/offer/cancel", text='{"id": 124124}')
    #        result = c.brequest(1, "offer/cancel", authenticate=True, method="POST", data={"offer_id": 124124},)
    #        self.assertEqual(result["id"], 124124)

    def test_symbols(self):
        c = exchange_factory("binance")()
        self.assertEqual("ETHUSDT", c.get_symbol("USDT", "ETH"))
        self.assertEqual("ETH/USDT", c.get_pair("ETHUSDT"))
        self.assertEqual("ETH/USDT", c.unmake_symbol("ETHUSDT"))
        self.assertEqual("ETHUSDT", c.make_symbol("ETH/USDT"))

    # def test_public_v1(self):
    #    c = exchange_factory("binance")()
    #    with requests_mock.mock() as m:
    #        m.get("https://api.binance.com/v1/pubticker/btcusd", text='{"mid":"244.755"}')
    #        self.assertEqual(c.brequest(1, "pubticker/btcusd"), {"mid": "244.755"})

    # def test_auth_v2(self):
    #    c = BinanceApi("my key", "my secret")
    #    with requests_mock.mock() as m:
    #        m.post(
    #            "https://api.binance.com/v2/auth/r/wallets", text='[["funding", "USD", 24570.03334688, 0, 500.143]]',
    #        )
    #        result = c.brequest(2, endpoint="auth/r/wallets", authenticate=True, method="POST")
    #        self.assertEqual(result, [["funding", "USD", 24570.03334688, 0, 500.143]])

    # def test_errors(self):

    #    c = BinanceApi()

    #    # Error conditions
    #    with requests_mock.mock() as m:
    #        with self.assertRaises(ExchangeApiException):
    #            m.get(
    #                "https://api.binance.com/v1/error", text='{"message": "Invalid Request"}', status_code=400,
    #            )
    #            c.brequest(1, "error")

    #        with self.assertRaises(ExchangeApiException):
    #            m.get(
    #                "https://api-pub.binance.com/v2/error", text='["error", 2141, "Invalid Request"]', status_code=400,
    #            )
    #            c.brequest(2, "error")

    #        with self.assertRaises(ExchangeApiException):
    #            m.get(
    #                "https://api.binance.com/v1/badjson", text="{badjson", status_code=400,
    #            )
    #            c.brequest(1, "badjson")

    #        with self.assertRaises(ExchangeApiException):
    #            # Simulate cloudflare failure
    #            m.get(
    #                "https://api.binance.com/v1/html",
    #                text="blah blah <title>Invalid Request</title>blah",
    #                status_code=502,
    #            )
    #            c.brequest(1, "html")

    #        with self.assertRaises(binanceNonceException):
    #            m.get(
    #                "https://api.binance.com/v1/nonce", text='{"message":"Nonce is too small."}', status_code=400,
    #            )
    #            c.brequest(1, "nonce")

    #        with self.assertRaises(binanceNonceException):
    #            m.get(
    #                "https://api-pub.binance.com/v2/nonce", text='["error",10114,"nonce: small"]', status_code=500,
    #            )
    #            c.brequest(2, "nonce")

    #        with self.assertRaises(ExchangeApiException):
    #            m.get(
    #                "https://api-pub.binance.com/v2/newformat", text='{"newformat": true}', status_code=500,
    #            )
    #            c.brequest(2, "newformat")

    # def test_public_v2(self):
    #    c = BinanceApi()
    #    # One real call without a mock
    #    try:
    #        self.assertEqual(c.brequest(2, "platform/status"), [1])
    #    except ExchangeApiException:  # pragma: no cover
    #        print("Error fetching binance platform status. Network down?")
