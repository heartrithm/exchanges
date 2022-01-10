import unittest

import requests_mock

from ..base import BaseExchangeApi, ExchangeApiException


class BaseTest(unittest.TestCase):
    def test_nonce(self):
        c = BaseExchangeApi()
        nonce1 = c.nonce()
        nonce2 = c.nonce()

        self.assertGreater(nonce2, nonce1)

    def test_init(self):
        c = BaseExchangeApi()  # No arg calls is safe
        self.assertIsNone(c.key)
        self.assertIsNone(c.secret)

        c = BaseExchangeApi("my key", "my secret")
        self.assertEqual(c.key, "my key")
        self.assertEqual(c.secret, "my secret")

    def test_sign(self):
        c = BaseExchangeApi()
        signature = c.sign("my secret", "The message to sign")
        self.assertEqual(
            signature,
            "697c3fe5856f6bee86b6cd7379a44b305fa2a24196a7676268cbaaf636e469490d75f73d7834113e5d167b0d3b6ac8e2",
        )

    def test_request(self):
        c = BaseExchangeApi()

        with requests_mock.mock() as m:
            # https
            m.get("https://example.com/empty", text="[]")
            response = c.request("https://example.com/empty")
            self.assertEqual(response, [])

            # http
            m.get("http://example.com/empty", text="[]")
            response = c.request("http://example.com/empty")
            self.assertEqual(response, [])

            # POST
            m.post("http://example.com/POST", text="[]")
            response = c.request("http://example.com/post", "POST", data={"one": 1})
            self.assertEqual(response, [])

            # GET with params (check url encoding)
            m.get("http://example.com/x?param=data%20and%20%3C%2C%20stuff", text="[]")
            response = c.request("http://example.com/x", params={"param": "data and <, stuff"})
            self.assertEqual(response, [])

            # Invalid JSON
            with self.assertRaises(ExchangeApiException):
                m.get("http://example.com/badjson", text="[']")
                response = c.request("http://example.com/badjson")
