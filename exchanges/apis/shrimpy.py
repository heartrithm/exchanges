import base64
import hashlib
import hmac
import urllib

import time

from .base import BaseExchangeApi, ExchangeApiException


class ShrimpyApi(BaseExchangeApi):

    accounts_cache = None
    """Shrimpy doesn't have trading pairs, only positions of a currency, so the symbol methods are
    NotImplementedError"""

    def __init__(self, key=None, secret=None):
        # For shrimpy, 500 is how they fail a bad request, invalid API auth, etc.
        # Don't retry these, as it swallows the problem
        self.HTTP_STATUSES_TO_RETRY.remove(500)
        super().__init__(key, secret)

    def get_symbol(self, stake_currency, trade_currency):
        raise NotImplementedError

    def get_pair(self, symbol):
        raise NotImplementedError

    def unmake_symbol(self, symbol):
        raise NotImplementedError

    def make_symbol(self, symbol):
        raise NotImplementedError

    def get_trade_history(self):
        """ Normalized view of trade history excluding deposits/withdrawals"""
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
            # proper representation for empty params or data, so it can be signed:
            data = data or ""
            params = params or ""
            if params:
                params = urllib.parse.urlencode(params)

            nonce = str(int(time.time() * 1000))
            message = (api_path + method + nonce + data).encode("ascii")
            hmac_key = base64.b64decode(self.secret)

            signature = hmac.new(hmac_key, message, hashlib.sha256)
            signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")
            headers.update(
                {"SHRIMPY-API-KEY": self.key, "SHRIMPY-API-NONCE": nonce, "SHRIMPY-API-SIGNATURE": signature_b64}
            )

        return self.request(url, method, params, data or {}, headers)

    def get_account_id_for_exchange(self, exchange):
        if self.accounts_cache is None:
            self.accounts_cache = self.brequest(1, "accounts", authenticate=True)

        for account in self.accounts_cache:
            if exchange == account["exchange"]:
                return account["id"]
        raise NotImplementedError(f"No shrimpy account found for {exchange}")


class ShrimpyException(ExchangeApiException):
    pass
