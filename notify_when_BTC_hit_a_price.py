import os
import telegram_api

from time import sleep
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

RES_LEVEL_1 = 57000
RES_LEVEL_2 = 58000

BELOW_RES_LEVEL_1 = 0
BETWEEN_RES_LEVEL_1_AND_2 = 1
OVER_RES_LEVEL_2 = 2
# init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
client = Client(api_key, api_secret)
price = {'BTCUSDT': None, 'error':False}
level = 0

def btc_pairs_trade(msg):
    ''' define how to process incoming WebSocket messages '''
    if msg['e'] != 'error':
        price['BTCUSDT'] = float(msg['c'])
    else:
        price['error']:True

bsm = BinanceSocketManager(client)
conn_key = bsm.start_symbol_ticker_socket('BTCUSDT', btc_pairs_trade)
bsm.start()

while not price['BTCUSDT']:
    # wait for WebSocket to start streaming data
    sleep(0.1)
    

while True:
    # error check to make sure WebSocket is working
    if price['error']:
        # stop and restart socket
        bsm.stop_socket(conn_key)
        bsm.start()
        price['error'] = False
        
    else:
        btc_price = price['BTCUSDT']
        if btc_price < RES_LEVEL_1:
            if level != BELOW_RES_LEVEL_1:
                telegram_api.send_msg("BTC price is below RES_LEVEL_1 (" + str(RES_LEVEL_1) + ")")
                level = BELOW_RES_LEVEL_1
        elif btc_price >= RES_LEVEL_1 and btc_price < RES_LEVEL_2:
            if level == BELOW_RES_LEVEL_1:
                telegram_api.send_msg("BTC price is over RES_LEVEL_1 (" + str(RES_LEVEL_1) + ")")
                level = BETWEEN_RES_LEVEL_1_AND_2
            elif level == OVER_RES_LEVEL_2:
                telegram_api.send_msg("BTC price is below RES_LEVEL_2 (" + str(RES_LEVEL_2) + ")")
                level = BETWEEN_RES_LEVEL_1_AND_2
        elif btc_price >= RES_LEVEL_2:
            if level != OVER_RES_LEVEL_2:
                telegram_api.send_msg("BTC price is over RES_LEVEL_2 (" + str(RES_LEVEL_2) + ")")
                level = OVER_RES_LEVEL_2
    sleep(0.1)

bsm.stop_socket(conn_key)
reactor.stop()
