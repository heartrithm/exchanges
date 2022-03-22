from typing import Dict
import hmac
import json
import time
import urllib

from loguru import logger
from ratelimiter import RateLimiter

from .base import BaseExchangeApi, ExchangeApiException

RATE_LIMIT_MAX_CALLS = 60
RATE_LIMIT_PERIOD = 1  # seconds


class FTXApi(BaseExchangeApi):
    api_prefix = "api"

    def __init__(self, passphrase=None, subaccount=None, key=None, secret=None):
        self.passphrase = passphrase
        self.subaccount = subaccount
        super().__init__(key=key, secret=secret)

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
        ), "endpoint should not be a full path, but the url after api/"

        base_url = "https://ftx.com"
        api_path = f"/{self.api_prefix}/{endpoint}"
        headers = self.DEFAULT_HEADERS.copy()

        if authenticate:
            headers = headers | self.auth_headers(method, api_path, data)

        url = base_url + api_path

        limiter = RateLimiter(
            max_calls=RATE_LIMIT_MAX_CALLS,
            period=RATE_LIMIT_PERIOD,
            callback=lambda until: logger.info(f"FTX call rate limited, sleeping for {until - time.time():.1f}s"),
        )
        with limiter:
            return self.request(url, method, params, data, headers)

    def auth_headers(self, method: str, api_path: str, payload: Dict = None):
        ts = int(time.time() * 1000)
        signature_payload = f"{ts}{method}{api_path}"

        if payload:
            signature_payload += json.dumps(payload)

        signature_payload = signature_payload.encode()
        signature = hmac.new(self.secret.encode(), signature_payload, "sha256").hexdigest()

        out = {
            "FTX-KEY": self.secret,
            "FTX-SIGN": signature,
            "FTX-TS": str(ts),
        }

        if self.subaccount:
            out["FTX-SUBACCOUNT"] = urllib.parse.quote(self.subaccount)
        return out


class FTXException(ExchangeApiException):
    pass
