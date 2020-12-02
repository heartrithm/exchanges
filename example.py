from exchanges import exchange_factory
import os

# Print account endpoint (balances) on binance
client = exchange_factory("binance")(key=os.getenv("binance_api_key"), secret=os.getenv("binance_api_secret"))
response = client.brequest(3, endpoint="account", authenticate=True)
print(response)

# Print margin maxBorrowable for USDT on margin API
client = exchange_factory("binance_margin")(key=os.getenv("binance_api_key"), secret=os.getenv("binance_api_secret"))
response = client.brequest(1, endpoint="margin/maxBorrowable", authenticate=True, params={"asset": "USDT"})
print(response)
