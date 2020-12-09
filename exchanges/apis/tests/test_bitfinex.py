from ..base import ExchangeApiException
from ..bitfinex import BitfinexNonceException
from exchanges import exchange_factory
import requests_mock
import unittest


class BitfinexTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.client = exchange_factory("bitfinex")("key", "secret")
        super(BitfinexTest, self).__init__(*args, **kwargs)

    def test_auth_v1(self):
        with requests_mock.mock() as m:
            m.post("https://api.bitfinex.com/v1/offer/cancel", text='{"id": 124124}')
            result = self.client.brequest(
                1, "offer/cancel", authenticate=True, method="POST", data={"offer_id": 124124},
            )
            self.assertEqual(result["id"], 124124)

    def test_symbols(self):
        self.assertEqual("tETHUSD", self.client.get_symbol("USD", "ETH"))
        self.assertEqual("BTCF0/USTF0", self.client.get_pair("tBTCF0:USTF0"))
        self.assertEqual("XAUT/USD", self.client.get_pair("tXAUT:USD"))
        self.assertEqual("ETH/USD", self.client.get_pair("tETHUSD"))
        self.assertEqual("tXAUT:USD", self.client.get_symbol("USD", "XAUT"))
        self.assertEqual("tTESTBTC:TESTUSDT", self.client.get_symbol("TESTUSDT", "TESTBTC"))
        self.assertEqual("ETH/USD", self.client.unmake_symbol("tETHUSD"))
        self.assertEqual("TESTBTC/TESTUSDT", self.client.unmake_symbol("tTESTBTC:TESTUSDT"))

    def test_public_v1(self):
        with requests_mock.mock() as m:
            m.get("https://api.bitfinex.com/v1/pubticker/btcusd", text='{"mid":"244.755"}')
            self.assertEqual(self.client.brequest(1, "pubticker/btcusd"), {"mid": "244.755"})

    def test_auth_v2(self):
        with requests_mock.mock() as m:
            m.post(
                "https://api.bitfinex.com/v2/auth/r/wallets", text='[["funding", "USD", 24570.03334688, 0, 500.143]]',
            )
            result = self.client.brequest(2, endpoint="auth/r/wallets", authenticate=True, method="POST")
            self.assertEqual(result, [["funding", "USD", 24570.03334688, 0, 500.143]])

    def test_errors(self):
        # Error conditions
        with requests_mock.mock() as m:
            with self.assertRaises(ExchangeApiException):
                m.get(
                    "https://api.bitfinex.com/v1/error", text='{"message": "Invalid Request"}', status_code=400,
                )
                self.client.brequest(1, "error")

            with self.assertRaises(ExchangeApiException):
                m.get(
                    "https://api-pub.bitfinex.com/v2/error", text='["error", 2141, "Invalid Request"]', status_code=400,
                )
                self.client.brequest(2, "error")

            with self.assertRaises(ExchangeApiException):
                m.get(
                    "https://api.bitfinex.com/v1/badjson", text="{badjson", status_code=400,
                )
                self.client.brequest(1, "badjson")

            with self.assertRaises(ExchangeApiException):
                # Simulate cloudflare failure
                m.get(
                    "https://api.bitfinex.com/v1/html",
                    text="blah blah <title>Invalid Request</title>blah",
                    status_code=502,
                )
                self.client.brequest(1, "html")

            with self.assertRaises(BitfinexNonceException):
                m.get(
                    "https://api.bitfinex.com/v1/nonce", text='{"message":"Nonce is too small."}', status_code=400,
                )
                self.client.brequest(1, "nonce")

            with self.assertRaises(BitfinexNonceException):
                m.get(
                    "https://api-pub.bitfinex.com/v2/nonce", text='["error",10114,"nonce: small"]', status_code=500,
                )
                self.client.brequest(2, "nonce")

            with self.assertRaises(ExchangeApiException):
                m.get(
                    "https://api-pub.bitfinex.com/v2/newformat", text='{"newformat": true}', status_code=500,
                )
                self.client.brequest(2, "newformat")

    def test_public_v2(self):
        # One real call without a mock
        try:
            self.assertEqual(self.client.brequest(2, "platform/status"), [1])
        except ExchangeApiException:  # pragma: no cover
            print("Error fetching bitfinex platform status. Network down?")
