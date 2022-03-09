from typing import Dict
import time

from loguru import logger
from ratelimiter import RateLimiter

from .base import BaseExchangeApi, ExchangeApiException

RATE_LIMIT_MAX_CALLS = 100
RATE_LIMIT_PERIOD = 1  # seconds


class TardisApi(BaseExchangeApi):

    def __init__(self, key=None, secret=None):
        self.key = key
        self.custom_response_parsing = True
        self.response_json_split_char = " "
        self.response_json_index = 1
        super().__init__(key=key, secret=secret)

    def brequest(
        self,
        api_version,
        endpoint=None,
        authenticate=False,  # ignored, we always supply the API key
        method="GET",
        params=None,
        data={},
    ):
        assert not endpoint.startswith(
            (f"/v1", f"v1")
        ), "endpoint should not be a full path, but the url after v1/"

        base_url = "https://api.tardis.dev"
        api_path = f"/v{api_version}/{endpoint}"
        headers = self.DEFAULT_HEADERS.copy()
        headers.update({"Authorization": f"Bearer {self.key}"})

        url = base_url + api_path

        limiter = RateLimiter(
            max_calls=RATE_LIMIT_MAX_CALLS,
            period=RATE_LIMIT_PERIOD,
            callback=lambda until: logger.info(f"Tardis.dev call rate limited, sleeping for {until - time.time():.1f}s"),
        )
        with limiter:
            return self.request(url, method, params, data, headers)


class FTXException(ExchangeApiException):
    pass
