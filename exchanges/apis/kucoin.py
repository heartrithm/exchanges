from .base import BaseExchangeApi, ExchangeApiException


class KuCoinApi(BaseExchangeApi):
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


class KuCoinException(ExchangeApiException):
    pass
