import os
import time
import sys

from binance.client import Client
#init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

pair_coin_symbol=sys.argv[1]

client = Client(api_key, api_secret)

coin_price = client.get_symbol_ticker(symbol=pair_coin_symbol)
print(coin_price["symbol"] + " : " + coin_price["price"])
