from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
import hmac
import requests
import time
import ujson
from loguru import logger


class BaseExchangeApi:

    # Internal state
    _session = key = secret = None

    # Settings
    TIMEOUT = (3, 10)  # Connect, Read
    RETRIES = 2
    RETRY_BACKOFF_FACTOR = 0.3
    RETRY_STATUSES = (500, 502, 503, 504)
    DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

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

    @property
    def session(self):
        # Sessions are used to enable HTTP Keep-Alive when available
        # Reuse the client for multiple requests by storing it as an internal state variable
        if not self._session:
            self._session = requests.Session()

        # Set up retry that will re-issue the request on connect errors and http status codes in RETRY_STATUSES
        retry = Retry(
            total=self.RETRIES, read=self.RETRIES, connect=self.RETRIES, backoff_factor=self.RETRY_BACKOFF_FACTOR,
        )

        # Handle for all requests that start with http or https
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        return self._session

    def request(self, url, method="GET", params=None, data=None, headers=None):
        assert method in ["GET", "POST"]
        if method == "GET" and not params:
            assert not params, "GET must be used with params"
        if data:
            assert method == "POST", "POST must be used with data"

        logger.debug("Requesting %s %s with %s" % (method, url, params or data))
        if headers:
            logger.debug("Request Headers: %s" % headers)

        try:
            if method == "GET":
                response = self.session.request(method, url, params=params, headers=headers, timeout=self.TIMEOUT,)
            else:
                response = self.session.request(
                    method, url, params=params, json=data, headers=headers, timeout=self.TIMEOUT,
                )
            response.raise_for_status()
            parsed = ujson.loads(response.content)
            return parsed
        except requests.exceptions.Timeout:  # pragma: no cover
            raise ExchangeApiException(method, url, None, "Connection Timeout")
        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise ExchangeApiException(method, url, None, "Connection Error")
        except requests.exceptions.HTTPError:
            print(f"Request headers: {response.request.headers}")
            print(f"Response headers: {response.headers}")
            error_text = self.parse_error_text(response)
            raise ExchangeApiException(method, url, response.status_code, error_text)
        except ValueError as exc:
            raise ExchangeApiException(
                method, url, response.status_code, "Could not decode JSON response: %s" % exc,
            )

    def parse_error_text(self, response):  # pragma: no cover
        # Exchange-specific error handling
        return response.text

    def nonce(self):
        # Slightly larger than the default so we can continue using the same one for all APIs
        return str(int(round(time.time() * 10000000)))

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
        super().__init__("%s %s returned status code %s with message: %s" % (method, url, status_code, message))
