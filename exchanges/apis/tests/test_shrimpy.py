from exchanges import exchange_factory

import requests_mock
import unittest


class ShrimpyTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.client = exchange_factory("shrimpy")("key", "c2VjcmV0")
        super(ShrimpyTest, self).__init__(*args, **kwargs)

    def test_auth_v1(self):
        with requests_mock.mock() as m:
            m.post(
                requests_mock.ANY,
                text='{"balances": [{"asset": "BTC", "free": "0.10730199", "locked": "0.00000000"}]}',
            )
            # https://dev-api.shrimpy.io/v1/users/<userId>/accounts/<exchangeAccountId>/balance
            result = self.client.brequest(
                1, endpoint="users/555/accounts/666/balance", authenticate=True, method="POST"
            )
            self.assertEqual(result, {"balances": [{"asset": "BTC", "free": "0.10730199", "locked": "0.00000000"}]})
