from .base import BaseExchangeApi, ExchangeApiException
import re


class SFOXApi(BaseExchangeApi):
    def get_symbol(self, stake_currency, trade_currency):
        return self.make_symbol(f"{trade_currency}/{stake_currency}")

    def get_pair(self, symbol):
        return self.unmake_symbol(symbol)

    def unmake_symbol(self, symbol):
        """ Just 3 chars support for now.. will likely change soon """
        return f"{symbol[:3]}/{symbol[3:]}".upper()

    def make_symbol(self, symbol):
        assert re.match(
            "[A-Z0-9]{3,}/[A-Z0-9]{3,}", symbol
        ), "Format of symbol should be $trade_currency/$stake_currency: {}".format(symbol)
        pieces = symbol.split("/")
        return f"{pieces[0]}{pieces[1]}".lower()

    def brequest(
        self, api_version=1, endpoint=None, authenticate=False, method="GET", params=None, data=None,
    ):
        # SFOX doesn't have versioned APIs.. :|

        if endpoint.startswith("candlesticks"):
            base_url = "https://chartdata.sfox.com"
            api_path = f"/{endpoint}"
        else:
            base_url = "https://api.sfox.com"
            api_path = f"/v{api_version}/{endpoint}"

        headers = self.DEFAULT_HEADERS

        if authenticate:
            headers.update({"Authorization": f"Bearer {self.key}"})

        url = base_url + api_path

        return self.request(url, method, params, data, headers)


class SFOXException(ExchangeApiException):
    pass
