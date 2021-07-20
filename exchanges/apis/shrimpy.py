import base64
import hashlib
import hmac
import urllib

import arrow

from .base import BaseExchangeApi, ExchangeApiException


class ShrimpyApi(BaseExchangeApi):
    """Shrimpy doesn't have trading pairs, only positions of a currency, so the symbol methods are
    NotImplementedError"""

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

        base_url = "https://dev-api.shrimpy.io"
        api_path = f"/v{api_version}/{endpoint}"
        url = base_url + api_path

        headers = self.DEFAULT_HEADERS

        if authenticate:
            # proper representation for empty params or data, so it can be signed:
            data = data or ""
            params = params or ""
            if params:
                params = urllib.parse.urlencode(params)

            nonce = str(round(arrow.utcnow().float_timestamp * 1000))
            decoded_secret = base64.b64decode(self.secret)

            hash_str = api_path + params + method + nonce + data
            signature = (
                hmac.new(decoded_secret, msg=bytes(hash_str, "latin-1"), digestmod=hashlib.sha256).hexdigest().upper()
            )
            headers.update(
                {
                    "DEV-SHRIMPY-API-KEY": self.key,
                    "DEV-SHRIMPY-API-NONCE": nonce,
                    "DEV-SHRIMPY-API-SIGNATURE": base64.b64encode(bytes(signature, "latin-1")),
                }
            )

        return self.request(url, method, params, data or {}, headers)


class ShrimpyException(ExchangeApiException):
    pass
