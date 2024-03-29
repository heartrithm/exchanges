# Exchange APIs

<img width="75" align="right" src="https://raw.githubusercontent.com/heartrithm/heart_token/main/assets/heartrithm-logo.png">

[![CircleCI](https://circleci.com/gh/heartrithm/exchanges.svg?style=svg)](https://circleci.com/gh/heartrithm/exchanges)

[![Coverage Status](https://coveralls.io/repos/github/heartrithm/exchanges/badge.svg?branch=master)](https://coveralls.io/github/heartrithm/exchanges?branch=master)

Reliably talk to supported exchange APIs, with a simple raw interface. Handles the barebones communication (authentication, HTTP handling, etc.), as well as some abstraction of common methods. Used in production at [HeartRithm](https://www.heartrithm.com) since 2017.

## Features

* Retry of `GET` requests upon failure, up to 3 times, with an exponential back-off
* Robust handling of connection, timeout, and HTTP errors, with grouping to `ExchangeApiException`.
* Parsing / handling of exchange error messages
* Thorough tests with mocks
* Proper python logging
* High performance json parsing with [ujson](https://pypi.org/project/ujson/)
* Methods to standardize symbol/pair names across exchanges

## Usage

Bitfinex

```python
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
* Binance spot API
* SFOX
* KuCoin
* Shrimpy
* Tardis
