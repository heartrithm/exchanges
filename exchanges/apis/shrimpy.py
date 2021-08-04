from .base import BaseExchangeApi, ExchangeApiException
from requests.auth import AuthBase
import base64
import hashlib
import hmac
import time


class ShrimpyApi(BaseExchangeApi):

    """Shrimpy doesn't have trading pairs, only positions of a currency, so the symbol methods are
    NotImplementedError"""

    auth_provider = None

    def __init__(self, key=None, secret=None):
        super().__init__(key, secret)

        # For shrimpy, 500 is how they fail a bad request, invalid API auth, etc.
        # Don't retry these, as it swallows the problem
        if 500 in self.HTTP_STATUSES_TO_RETRY:
            self.HTTP_STATUSES_TO_RETRY.remove(500)

    def get_symbol(self, stake_currency, trade_currency):
        return "{}:{}".format(stake_currency, trade_currency)

    def get_pair(self, symbol):
        return symbol

    def unmake_symbol(self, symbol):
        return symbol

    def make_symbol(self, symbol):
        return symbol

    def get_trade_history(self):
        """Normalized view of trade history excluding deposits/withdrawals"""
        raise NotImplementedError

    def brequest(
        self,
        api_version,
        endpoint=None,
        authenticate=False,
        method="GET",
        params=None,
        data=None,
    ):

        base_url = "https://api.shrimpy.io"
        api_path = f"/v{api_version}/{endpoint}"
        url = base_url + api_path

        headers = self.DEFAULT_HEADERS.copy()

        if authenticate:
            self.auth_provider = ShrimpyAuthProvider(self.key, self.secret)
        else:
            self.auth_provider = None

        return self.request(url, method, params, data, headers)


class ShrimpyException(ExchangeApiException):
    pass


class ShrimpyAuthProvider(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        nonce = str(int(time.time() * 1000))

        message = "".join([request.path_url, request.method, str(nonce), (request.body or "")])
        headers = self.get_auth_headers(nonce, message, self.api_key, self.secret_key)
        request.headers.update(headers)
        return request

    def get_auth_headers(self, timestamp, message, api_key, secret_key):
        message = message.encode("ascii")
        hmac_key = base64.b64decode(secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")

        return {
            "SHRIMPY-API-KEY": api_key,
            "SHRIMPY-API-NONCE": timestamp,
            "SHRIMPY-API-SIGNATURE": signature_b64,
        }
