import os

from ..base import ExchangeApiException
from exchanges import exchange_factory

import unittest


class LiveAPITest(unittest.TestCase):
    def __init__(self, *args, **kwargs):

        self.key = os.environ.get("API_KEY")
        self.secret = os.environ.get("API_SECRET")

        self.bitfinex_client = exchange_factory("bitfinex")(self.key, self.secret)
        super(LiveAPITest, self).__init__(*args, **kwargs)

    def test_wallets(self):
        if not all([self.key, self.secret]):
            unittest.skip("No API keys provided; skipping live auth checks")
            return True

        result = self.bitfinex_client.brequest(2, endpoint="auth/r/wallets", authenticate=True, method="POST")
