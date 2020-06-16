from ..base import ExchangeApiException
from ..bitfinex import BitfinexApi, BitfinexNonceException
from exchanges import exchange_factory
import requests_mock
import unittest


class BitfinexTest(unittest.TestCase):
    def test_auth_v1(self):
        c = BitfinexApi("my key", "my secret")
        with requests_mock.mock() as m:
            m.post("https://api.bitfinex.com/v1/offer/cancel", text='{"id": 124124}')
            result = c.brequest(
                1,
                "offer/cancel",
                authenticate=True,
                method="POST",
                data={"offer_id": 124124},
            )
            self.assertEqual(result["id"], 124124)

    def test_symbols(self):
        c = exchange_factory("bitfinex")()
        self.assertEqual("tETHUSD", c.get_symbol("USD", "ETH"))

    def test_public_v1(self):
        c = exchange_factory("bitfinex")()
        with requests_mock.mock() as m:
            m.get(
                "https://api.bitfinex.com/v1/pubticker/btcusd", text='{"mid":"244.755"}'
            )
            self.assertEqual(c.brequest(1, "pubticker/btcusd"), {"mid": "244.755"})

    def test_auth_v2(self):
        c = BitfinexApi("my key", "my secret")
        with requests_mock.mock() as m:
            m.post(
                "https://api.bitfinex.com/v2/auth/r/wallets",
                text='[["funding", "USD", 24570.03334688, 0, 500.143]]',
            )
            result = c.brequest(
                2, endpoint="auth/r/wallets", authenticate=True, method="POST"
            )
            self.assertEqual(result, [["funding", "USD", 24570.03334688, 0, 500.143]])

    def test_errors(self):

        c = BitfinexApi()

        # Error conditions
        with requests_mock.mock() as m:
            with self.assertRaises(ExchangeApiException):
                m.get(
                    "https://api.bitfinex.com/v1/error",
                    text='{"message": "Invalid Request"}',
                    status_code=400,
                )
                c.brequest(1, "error")

            with self.assertRaises(ExchangeApiException):
                m.get(
                    "https://api-pub.bitfinex.com/v2/error",
                    text='["error", 2141, "Invalid Request"]',
                    status_code=400,
                )
                c.brequest(2, "error")

            with self.assertRaises(ExchangeApiException):
                m.get(
                    "https://api.bitfinex.com/v1/badjson",
                    text="{badjson",
                    status_code=400,
                )
                c.brequest(1, "badjson")

            with self.assertRaises(ExchangeApiException):
                # Simulate cloudflare failure
                m.get(
                    "https://api.bitfinex.com/v1/html",
                    text="blah blah <title>Invalid Request</title>blah",
                    status_code=502,
                )
                c.brequest(1, "html")

            with self.assertRaises(BitfinexNonceException):
                m.get(
                    "https://api.bitfinex.com/v1/nonce",
                    text='{"message":"Nonce is too small."}',
                    status_code=400,
                )
                c.brequest(1, "nonce")

            with self.assertRaises(BitfinexNonceException):
                m.get(
                    "https://api-pub.bitfinex.com/v2/nonce",
                    text='["error",10114,"nonce: small"]',
                    status_code=500,
                )
                c.brequest(2, "nonce")

            with self.assertRaises(ExchangeApiException):
                m.get(
                    "https://api-pub.bitfinex.com/v2/allelse",
                    text='allelse',
                    status_code=500,
                )
                c.brequest(2, "allelse")

    def test_public_v2(self):
        c = BitfinexApi()
        # One real call without a mock
        try:
            self.assertEqual(c.brequest(2, "platform/status"), [1])
        except ExchangeApiException:  # pragma: no cover
            print("Error fetching bitfinex platform status. Network down?")
