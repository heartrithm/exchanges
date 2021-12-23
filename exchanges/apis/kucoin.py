from base import BaseExchangeApi
from functools import reduce


class KucoinApi(BaseExchangeApi):
    api_prefix = "api"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def brequest(
        self,
        api_version,
        endpoint=None,
        authenticate=False,
        method="GET",
        params=None,
        data=None,
    ):
        assert not endpoint.startswith(
            (f"/{self.api_prefix}", f"{self.api_prefix}")
        ), "endpoint should not be a full path, but the url after api/v1/"

        base_url = "https://api.kucoin.com"
        api_path = f"/{self.api_prefix}/v{api_version}/{endpoint}"
        headers = self.DEFAULT_HEADERS.copy()

        data = data or {}

        # TODO: implement authentication for writes if needed
        if authenticate:
            pass

        url = base_url + api_path
        return self.request(url, method, params, data, headers)


if __name__ == "__main__":
    kucoin = KucoinApi()
    # Running the following gives a total sum of $88m
    sum = 0
    for currency in ["USDT"]:  # I initially added more stablecoins
        params = {"currency": currency}
        a = kucoin.brequest(1, "margin/market", params=params)
        sizes = [int(i["size"]) for i in a["data"]]
        if not sizes:
            continue
        value = reduce(lambda a, b: a + b, sizes)
        sum += value

    print("${:0,.0f}".format(sum))

    # Total amount borrowed in the past 2 minutes is $500k
    params = {"currency": "USDT"}
    a = kucoin.brequest(1, "margin/trade/last", params=params)
    sizes = [int(i["size"]) for i in a["data"]]
    print("${:0,.0f}".format(reduce(lambda a, b: a + b, sizes)))
