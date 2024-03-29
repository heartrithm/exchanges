import hashlib
import hmac
import json

from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import arrow
import requests


class BaseExchangeApi:

    # Internal state
    _session = key = secret = auth_provider = None

    # Settings
    # https://requests.readthedocs.io/en/master/user/advanced/#timeouts
    TIMEOUT = (7.5, 30)  # first is connect, second is read
    RETRIES = 3
    RETRY_BACKOFF_FACTOR = 0.5
    DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
    # Don't auto retry 429, that means we're going too fast
    HTTP_STATUSES_TO_RETRY = [408, 420, 500, 501, 502, 503, 504, 520, 521, 522, 523, 524, 525]

    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret

    def get_symbol(self, stake_currency, trade_currency):  # pragma: no cover
        # Return a str for how the exchange likes to see a symbol given the stake/trade currencies
        # Ex BTCUSDT
        raise NotImplementedError

    def get_pair(self, symbol):  # pragma: no cover
        # Return a str representing the pair, un-doing a get_symbol() with exchange-specific knowledge
        # Ex BTC/USDT
        raise NotImplementedError

    def get_trade_history(self):
        """Normalized view of executed trade history across exchanges - excludes deposits/withdrawals
        Format: [{"exchange_txn_id": str,
                    "client_order_id": str,  # if present
                    "time": arrow,
                    "action": str,  # ("buy" or "sell")
                    "stake_curr": str,
                    "trade_curr": str,
                    "amount": Decimal,
                    "price": Decimal,  # price per unit of trade_curr
                    "fees": Decimal,  # Always in stake_curr
                }, ...]
        """
        raise NotImplementedError

    @property
    def session(self):
        # Sessions are used to enable HTTP Keep-Alive when available
        # Reuse the client for multiple requests by storing it as an internal state variable
        if not self._session:
            self._session = requests.Session()

        def log_retry_response(response, *args, **kwargs):
            elapsed = response.elapsed.total_seconds()
            if response.status_code in self.HTTP_STATUSES_TO_RETRY:
                logger.warning(
                    f"Retrying {response.request.url} ({response.status_code}: "
                    + f"{response.reason} after {elapsed:.2f}s): {response.text}"
                )
            else:
                logger.debug(f"Request to {response.request.url} took {elapsed:.2f}s")

        self._session.hooks["response"] = [log_retry_response]

        retry = Retry(
            total=self.RETRIES + 1,
            read=self.RETRIES,
            connect=self.RETRIES,
            status=self.RETRIES,
            backoff_factor=self.RETRY_BACKOFF_FACTOR,
            status_forcelist=self.HTTP_STATUSES_TO_RETRY,
        )

        # Handle for all requests that start with http or https
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        return self._session

    def request(self, url, method="GET", params=None, data=None, headers=None, ignore_json=False):
        assert method in ["GET", "POST", "DELETE"]
        if method == "GET" and not params:
            assert not params, "GET must be used with params"
        if data:
            assert method == "POST", "POST must be used with data"

        logger.debug("Requesting %s %s with %s" % (method, url, params or data))
        if headers:
            logger.debug("Request Headers: %s" % headers)

        # If a string is passed in for data, assume it is already json as a string,
        # otherwise, assume it's a complex type and we pass it as json so it gets converted
        # Note: ujson strips spaces and breaks bitfinex
        if data and not isinstance(data, str):
            json_data = None
            data = json.dumps(data)
        else:
            json_data = data
            data = None

        # Simple workaround to prevent unwanted data to be attached to requests
        if ignore_json:
            json_data = None

        try:

            response = self.session.request(
                method,
                url,
                params=params,
                headers=headers,
                data=data,
                json=json_data,
                timeout=self.TIMEOUT,
                auth=self.auth_provider,
            )

            response.raise_for_status()
            if "custom_response_parsing" in self.__dict__:
                parsed = json.loads(
                    response.content.decode("utf-8").split(self.response_json_split_char, 1)[self.response_json_index]
                )
            else:
                parsed = json.loads(response.content)
            return parsed
        except requests.exceptions.Timeout:  # pragma: no cover
            raise ExchangeApiException(method, url, None, "Connection Timeout")
        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise ExchangeApiException(method, url, None, "Connection Error")
        except requests.exceptions.HTTPError:
            logger.debug(f"Request headers: {response.request.headers}")
            logger.debug(f"Response headers: {response.headers}")
            error_text = self.parse_error_text(response)
            raise ExchangeApiException(method, url, response.status_code, error_text)
        except ValueError as exc:
            raise ExchangeApiException(
                method,
                url,
                response.status_code,
                f"Could not decode JSON response: {exc}",
            )

    def parse_error_text(self, response):  # pragma: no cover
        # Exchange-specific error handling
        return response.text

    def nonce(self, increment=0):
        # Slightly larger than the default so we can continue using the same one for all APIs
        # Increment prevents nonce too small errors from being raised
        return str(int(round(arrow.utcnow().float_timestamp * 10000000)) + increment)

    def sign(self, secret, message):
        """Signs the payload with SHA384 algorithm

        Arguments:
            secret_key {str} -- secret api key
            payload {str} -- payload

        Returns:
            str -- signature
        """
        encoded_message = message.encode() if isinstance(message, str) else message

        return hmac.new(secret.encode("utf8"), encoded_message, hashlib.sha384).hexdigest()


class ExchangeApiException(Exception):
    def __init__(self, method, url, status_code, message):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"{self.method} {self.url} returned status code {self.status_code} with message: {self.message}"
