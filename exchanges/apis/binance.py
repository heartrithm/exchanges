from .base import BaseExchangeApi, ExchangeApiException
import base64
import re
import requests
import json
import ujson


class BinanceApi(BaseExchangeApi):
    def get_symbol(self, stake_currency, trade_currency):
        return self.make_symbol(trade_currency + "/" + stake_currency)

    def get_pair(self, symbol):
        return self.unmake_symbol(symbol)

    def unmake_symbol(self, symbol):
        symbols = requests.get("https://api.binance.com/api/v3/exchangeInfo").json().get("symbols")

        our_symbol = [x for x in symbols if x["symbol"] == symbol]
        assert our_symbol, f"Trading pair {symbol} not found on Binance."

        return f'{our_symbol[0]["baseAsset"]}/{our_symbol[0]["quoteAsset"]}'

    def make_symbol(self, symbol):
        pieces = symbol.split("/")
        return "{}{}".format(pieces[0], pieces[1])

    def brequest(
        self, api_version, endpoint=None, authenticate=False, method="GET", params=None, data=None,
    ):
        # different from bitfinex support, we support specifying any api version, because bitfinex always
        # seems to have some lengthy transitions.
        assert not endpoint.startswith("/api"), "endpoint should not be a full path, but the url after api/"

        base_url = "https://api.binance.com"

        api_path = f"/api/v{api_version}/{endpoint}"

        headers = self.DEFAULT_HEADERS

        # Required because data for the signature must match the data that is passed in the body as json, even if empty
        data = data or {}

        if authenticate:
            nonce = self.nonce()
            payload = self.generate_payload(api_version, api_path, nonce, data)
            headers.update(self.auth_headers(self.key, self.secret, api_version, nonce, payload))

        url = base_url + api_path
        try:
            return self.request(url, method, params, data, headers)
        except ExchangeApiException as exc:
            if exc.message in ["nonce: small", "Nonce is too small."]:
                raise BinanceNonceException(method, url, exc.status_code, exc.message)
            else:
                raise

    def generate_payload(self, api_version, api_path, nonce, data):
        """ Return the header's payload based on version """
        assert api_version in [1, 2]
        if api_version == 1:
            payload_object = {}
            payload_object["request"] = api_path
            payload_object["nonce"] = nonce
            payload_object.update(data)
            # Important to use json here, the format has to match what binance expects
            # (ujson strips extra space, which causes invalid api key)
            payload = json.dumps(payload_object)
        elif api_version == 2:
            # same note here about json
            payload = "/api" + api_path + nonce + json.dumps(data)
        return payload

    def auth_headers(self, key, secret, api_version, nonce, payload):
        """ Return the request headers based on version """
        assert api_version in [1, 2]
        headers = {}
        if api_version == 1:
            message = base64.b64encode(payload.encode("utf8"))
            headers["X-BFX-APIKEY"] = key
            headers["X-BFX-PAYLOAD"] = message
            headers["X-BFX-SIGNATURE"] = self.sign(secret, message)
        elif api_version == 2:
            message = payload.encode("utf8")
            headers["bfx-nonce"] = nonce
            headers["bfx-apikey"] = key
            headers["bfx-signature"] = self.sign(secret, message)
        return headers

    def parse_error_text(self, response):
        # Exchange-specific error handling
        try:
            error_json = ujson.loads(response.content)
            # V1
            # {"message":"Nonce is too small."}
            if "message" in error_json:
                return error_json["message"]

            # V2
            # ["error", 20060, "maintenance"]
            if type(error_json) == list and error_json[0] == "error":
                return error_json[2]

            # Valid json, but unrecognized format, just return it
            return response.text

        except ValueError:
            # HTML? Probably an error page from cloudflare. Grab the title if we can
            match = re.search("<title.*?>([^<]+)</title>", response.text)
            if match:
                return "HTML: %s" % match.groups()[0]
            else:
                # No title. We need to truncate in case it's an entire html page
                return (response.text[:50] + "...") if len(response.text) > 50 else response.text


class BinanceNonceException(ExchangeApiException):
    pass
