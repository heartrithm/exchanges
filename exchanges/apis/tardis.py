import json
import time

from loguru import logger
from ratelimiter import RateLimiter

from .base import BaseExchangeApi, ExchangeApiException

RATE_LIMIT_MAX_CALLS = 100
RATE_LIMIT_PERIOD = 1  # seconds


class TardisApi(BaseExchangeApi):

    RESULT_KEY = "result"  # corresponds to market_data sync result_key

    def parse_response(self, response):
        # Newline-delimited records where the first element of each record
        # is the tardis write timestamp (which is "%Y-%m-%dT%H:%M:%S.%f" and
        # always 28 characters) and the second one is the JSON payload.
        records = response.content.decode("utf-8").split("\n")

        # Take the first record, strip off the timestamp, then parse
        take_first_record = 0
        timestamp_length = 28
        out = json.loads(records[take_first_record][timestamp_length:])

        # Union of stats and info
        out[self.RESULT_KEY] = out["data"]["stats"] | out["data"]["info"]
        return out

    def brequest(
        self,
        api_version,
        endpoint=None,
        authenticate=False,  # ignored, we always supply the API key
        method="GET",
        params=None,
        data={},
    ):
        assert not endpoint.startswith(("/v1", "v1")), "endpoint should not be a full path, but the url after v1/"

        base_url = "https://api.tardis.dev"
        api_path = f"/v{api_version}/{endpoint}"
        headers = self.DEFAULT_HEADERS.copy()
        headers.update({"Authorization": f"Bearer {self.key}"})

        url = base_url + api_path

        limiter = RateLimiter(
            max_calls=RATE_LIMIT_MAX_CALLS,
            period=RATE_LIMIT_PERIOD,
            callback=lambda until: logger.info(
                f"Tardis.dev call rate limited, sleeping for {until - time.time():.1f}s"
            ),
        )
        with limiter:
            return self.request(url, method, params, data, headers)


class FTXException(ExchangeApiException):
    pass
