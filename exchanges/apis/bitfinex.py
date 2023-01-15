import base64
import json
import re

import ujson

from .base import BaseExchangeApi, ExchangeApiException


class BitfinexApi(BaseExchangeApi):
    # Don't retry 500, as Bitfinex will return that for errors that we should not retry
    HTTP_STATUSES_TO_RETRY = [408, 420, 501, 502, 503, 504, 520, 521, 522, 523, 524, 525]

    def get_symbol(self, stake_currency, trade_currency):
        return self.make_symbol(trade_currency + "/" + stake_currency)

    def get_pair(self, symbol):
        return self.unmake_symbol(symbol)

    def unmake_symbol(self, bitfinex_symbol):
        assert re.match("t[A-Z0-9]{3,}[:]?[A-Z0-9]{3,}", bitfinex_symbol), (
            "Format of bitfinex_symbol should be t$trade_currency$stake_currency or t$trade_currency:$stake_currency"
            " (for pairs with >3 chars on one side): {}".format(bitfinex_symbol)
        )
        if ":" in bitfinex_symbol:
            # tXAUT:USD -> XAUT/USD
            pieces = bitfinex_symbol.lstrip("t").split(":")
            return "{}/{}".format(pieces[0], pieces[1])
        else:
            # tETHUSD -> ETH/USD
            return "{}/{}".format(bitfinex_symbol[1:-3], bitfinex_symbol[-3:])

    def make_symbol(self, symbol):
        assert re.match(
            "[A-Z0-9]{3,}/[A-Z0-9]{3,}", symbol
        ), "Format of symbol should be $trade_currency/$stake_currency: {}".format(symbol)
        pieces = symbol.split("/")
        if len(pieces[0]) > 3 or len(pieces[1]) > 3:  # these will have a : between symbols
            # TESTBTC/TESTUSDT -> tTESTBTC:TESTUSDT
            return "t{}:{}".format(pieces[0], pieces[1])
        else:
            # ETH/USD -> tETHUSD
            return "t{}{}".format(pieces[0], pieces[1])

    def brequest(
        self, api_version, endpoint=None, authenticate=False, method="GET", params=None, data=None, nonce_increment=0
    ):
        # Inspired by https://raw.githubusercontent.com/faberquisque/pyfinex/master/pyfinex/api.py
        # Handle requests for both v1 and v2 versions of the API with one wrapper
        # Why both, you ask? v2 has better data, but does not support write requests (only in v2 websockets API)
        # So we have to use v1 for anything that writes

        assert api_version in [1, 2]
        assert not endpoint.startswith("/v"), "endpoint should not be a full path, but the url after v1/v2"

        base_url = "https://api.bitfinex.com"
        if api_version == 2 and authenticate is False:
            base_url = "https://api-pub.bitfinex.com"

        api_path = "/v%s/%s" % (api_version, endpoint)
        headers = self.DEFAULT_HEADERS.copy()

        # Required because data for the signature must match the data that is passed in the body as json, even if empty
        data = data or {}

        if authenticate:
            # Use the retry value to increment the nonce if needed
            nonce = self.nonce(nonce_increment)
            payload = self.generate_payload(api_version, api_path, nonce, data)
            headers.update(self.auth_headers(self.key, self.secret, api_version, nonce, payload))

        url = base_url + api_path

        try:
            return self.request(url, method, params, data, headers)
        except ExchangeApiException as exc:
            if exc.message in ["nonce: small", "Nonce is too small."]:
                if nonce_increment > 3:
                    raise BitfinexNonceException(method, url, exc.status_code, exc.message)
                return self.brequest(api_version, endpoint, authenticate, method, params, data, nonce_increment + 1)
            else:
                raise

    def generate_payload(self, api_version, api_path, nonce, data):
        """Return the header's payload based on version"""
        assert api_version in [1, 2]
        if api_version == 1:
            payload_object = {}
            payload_object["request"] = api_path
            payload_object["nonce"] = nonce
            payload_object.update(data)
            # Important to use json here, the format has to match what bitfinex expects
            # (ujson strips extra space, which causes invalid api key)
            payload = json.dumps(payload_object)
        elif api_version == 2:
            # same note here about json
            payload = "/api" + api_path + nonce + json.dumps(data)
        return payload

    def auth_headers(self, key, secret, api_version, nonce, payload):
        """Return the request headers based on version"""
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


class BitfinexNonceException(ExchangeApiException):
    pass
