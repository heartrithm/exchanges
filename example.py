from exchanges import exchange_factory
import os

# Print account endpoint (balances) on binance

client = exchange_factory("binance")(key=os.getenv("binance_api_key"), secret=os.getenv("binance_api_secret"))

response = client.brequest(3, endpoint="account", authenticate=True)
print(response)
