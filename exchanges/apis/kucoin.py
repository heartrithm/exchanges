from typing import Dict
import base64
import hashlib
import hmac
import json
import time

from loguru import logger
from ratelimiter import RateLimiter

from .base import BaseExchangeApi, ExchangeApiException


class KuCoinApi(BaseExchangeApi):
    api_prefix = "api"

    def __init__(self, passphrase=None, *args, **kwargs):
        self.passphrase = passphrase
        super().__init__(*args, **kwargs)

    def brequest(
        self,
        api_version,
        endpoint=None,
        authenticate=False,
        method="GET",
        params=None,
        data={},
    ):
        assert not endpoint.startswith(
            (f"/{self.api_prefix}", f"{self.api_prefix}")
        ), "endpoint should not be a full path, but the url after api/v1/"

        base_url = "https://api.kucoin.com"
        api_path = f"/{self.api_prefix}/v{api_version}/{endpoint}"
        headers = self.DEFAULT_HEADERS.copy()

        if authenticate:
            headers.update(self.auth_headers(api_version, method, api_path, data))

        url = base_url + api_path

        limiter = RateLimiter(
            max_calls=100,
            period=10,
            callback=lambda until: logger.info(f"KuCoin call rate limited, sleeping for {until - time.time():.1f}s"),
        )
        with limiter:
            return self.request(url, method, params, data, headers)

    def auth_headers(self, api_version: int, method: str, api_path: str, payload: Dict):
        """Refer to https://docs.kucoin.com/#authentication for more details"""
        assert api_version in [1]
        now = int(time.time() * 1000)
        str_to_sign = str(now) + method.upper() + api_path + json.dumps(payload)
        signature = base64.b64encode(
            hmac.new(self.secret.encode("utf-8"), str_to_sign.encode("utf-8"), hashlib.sha256).digest()
        )
        passphrase = base64.b64encode(
            hmac.new(self.secret.encode("utf-8"), self.passphrase.encode("utf-8"), hashlib.sha256).digest()
        )
        return {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-KEY": self.key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
        }


class KuCoinException(ExchangeApiException):
    pass
