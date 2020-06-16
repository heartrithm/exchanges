from .base import BaseExchangeApi, ExchangeApiException
import base64
import re
import simplejson
import ujson


class BitfinexApi(BaseExchangeApi):
    def get_symbol(self, exchange, stake_currency, trade_currency):
        return "t{}{}".format(trade_currency, stake_currency)

    def brequest(self, api_version, endpoint=None, authenticate=False, method="GET", params=None, data=None):
        # Inspired by https://raw.githubusercontent.com/faberquisque/pyfinex/master/pyfinex/api.py
        # Handle requests for both v1 and v2 versions of the API with one wrapper
        # Why both, you ask? v2 has better data, but does not support write requests (they push that to v2 websockets API)
        # So we have to use v1 for anything that writes

        assert api_version in [1, 2]
        assert not endpoint.startswith("/v"), "endpoint should not be a full path, but the url after v1/v2"

        base_url = "https://api.bitfinex.com"
        if api_version == 2 and authenticate is False:
            base_url = "https://api-pub.bitfinex.com"

        api_path = "/v%s/%s" % (api_version, endpoint)

        headers = self.DEFAULT_HEADERS

        # This is required because data for the signature must match the data that is passed in the body as json, even if empty
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
                raise BitfinexNonceException(method, url, exc.status_code, exc.message)
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
            # Important to use simplejson here, the format has to match what bitfinex expects (ujson strips extra space, which causes invalid api key)
            payload = simplejson.dumps(payload_object)
        elif api_version == 2:
            # Important to use simplejson here, the format has to match what bitfinex expects (ujson strips extra space, which causes invalid api key)
            payload = "/api" + api_path + nonce + simplejson.dumps(data)
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

        except ValueError:
            # HTML? Probably an error page from cloudflare. Grab the title if we can
            match = re.search("<title.*?>([^<]+)</title>", response.text)
            if match:
                return "HTML: %s" % match.groups()[0]
            else:
                # No title. We need to truncate in case it's an entire html page
                return (response.text[:50] + "...") if len(response.text) > 50 else response.text

        # All else
        return response.text


class BitfinexNonceException(ExchangeApiException):
    pass
