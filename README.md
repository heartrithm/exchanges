# Exchange APIs
<img width="75" align="right" src="http://www.heartrithm.com/img/logo.png">

[![CircleCI](https://circleci.com/gh/heartrithm/exchanges.svg?style=svg)](https://circleci.com/gh/heartrithm/exchanges)

[![codecov](https://codecov.io/gh/heartrithm/exchanges/branch/master/graph/badge.svg)](https://codecov.io/gh/heartrithm/exchanges)

 
Reliably talk to supported exchange APIs, with a simple raw interface. Handles the barebones communication (authentication, HTTP handling, etc.), but does not [yet?] handle abstraction of common methods. Used in production at [HeartRithm](https://www.heartrithm.com) for 3+ years.

## Features
* Retry of `GET` requests upon failure, up to 3 times, with an exponential back-off
* Robust handling of connection, timeout, and HTTP errors, with grouping to `ExchangeApiException`.
* Parsing / handling of exchange error messages
* Thorough tests with mocks
* Proper python logging
* High performance json parsing with [ujson](https://pypi.org/project/ujson/)

## Usage

Bitfinex

```
from exchanges import exchange_factory

# Public V2
client = exchange_factory("bitfinex")()
client.brequest(2, "platform/status")
# returns [1]

# Private V1
client = exchange_factory("bitfinex")("my key", "my secret")
result = client.brequest(1, "offer/cancel", authenticate=True, method="POST", data={"offer_id": 124124})
```

## Supported Exchanges

* Bitfinex, both V1 and V2 versions of the REST API
* Binance coming soon


