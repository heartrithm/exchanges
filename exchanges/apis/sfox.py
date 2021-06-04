from .base import BaseExchangeApi, ExchangeApiException
import arrow
import re
from decimal import Decimal as D


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

    def get_trade_history(self):
        """ Normalized view of trade history excluding deposits/withdrawals"""
        history = []
        for txn in self.brequest(1, "account/transactions", authenticate=True):
            if txn["action"] not in ["Buy", "Sell"]:
                continue
            history.append(
                {
                    "exchange_txn_id": str(txn["id"]),
                    "client_order_id": str(txn.get("client_order_id")),
                    "time": arrow.get(txn["day"]),
                    "action": txn["action"].lower(),
                    "stake_curr": "USD",  # always for SFOX
                    "trade_curr": txn["currency"].upper(),
                    "amount": D(txn["amount"]),
                    "price": D(txn["price"]),
                    "fees": D(txn["fees"]),
                }
            )
        return history

    def brequest(
        self,
        api_version=1,
        endpoint=None,
        authenticate=False,
        method="GET",
        params=None,
        data=None,
    ):
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
