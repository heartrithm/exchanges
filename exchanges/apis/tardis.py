import json
import time

from loguru import logger
from ratelimiter import RateLimiter
import arrow

from .base import BaseExchangeApi, ExchangeApiException

RATE_LIMIT_MAX_CALLS = 100
RATE_LIMIT_PERIOD = 1  # seconds


class TardisApi(BaseExchangeApi):

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"  # seconds resolution
    RESULT_KEY = "result"  # corresponds to market_data sync result_key

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
        url = base_url + api_path

        headers = self.DEFAULT_HEADERS.copy()
        headers.update({"Authorization": f"Bearer {self.key}"})

        if "from" in params:
            params["from"] = arrow.get(params["from"]).strftime(self.DATE_FORMAT)

        if "to" in params:
            params["to"] = arrow.get(params["to"]).strftime(self.DATE_FORMAT)

        limiter = RateLimiter(
            max_calls=RATE_LIMIT_MAX_CALLS,
            period=RATE_LIMIT_PERIOD,
            callback=lambda until: logger.info(
                f"Tardis.dev call rate limited, sleeping for {until - time.time():.1f}s"
            ),
        )
        with limiter:
            return self.request(url, method, params, data, headers)

    def parse_response(self, response):
        # Tardis only gives us new-line delimited JSON. The returned response only contains 
        # 1 minute of data.  When we newline-split the text we have a list with roughly 
        # 10 elements space about 6 seconds apart.  This means the request only honors 
        # `from` and for some reason ignores `to`.  Therefore we are forced to make a single 
        # request for every hour of data we want.  The first element in the list is closest 
        # to `from` so we'll keep that one and drop the rest.
        parsed = {self.RESULT_KEY: dict()}

        response_text = response.content.decode("utf-8")
        if not response_text:  # no data available
            logger.warning("empty response, nothing to parse")
            return parsed

        try:
            # Newline-delimited text where the first part of each record
            # is the tardis write timestamp (which is "%Y-%m-%dT%H:%M:%S.%f"
            # and always 28 characters) and the remaining portion the JSON.
            records = response_text.split("\n")

            # Take the first record, strip off the timestamp, then parse
            take_first = 0
            timestamp_length = 28
            out = json.loads(records[take_first][timestamp_length:])

            # union of `stats` and `info`
            parsed[self.RESULT_KEY] = out["data"]["stats"] | out["data"]["info"]
        except json.decoder.JSONDecodeError as exc:
            # log malformed response text (hopefully just missing data)
            logger.exception(str(exc))
            logger.debug(response_text)

        return parsed
