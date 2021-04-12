#!/usr/bin/python

import os
import time
import json
import csv
import sys
import btalib
import requests
import datetime
import configparser

from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor
import pandas as pd

import telegram_api

LOG_TAG = '[BUY] '

if len(sys.argv) < 3:
    sys.exit()
# Define constant
symbol = sys.argv[1]
# print("Runing script to track RSI of " + symbol)
# valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
his_interval = sys.argv[2]

# The number of msg sent to telegram when condition happens
reminder_msg_count = 1
# Reminder will trigger reminder_count per 1 condition
reminder_count = 2
recal_interval = 60 * 5 # seconds
RSI_LEVEL_0 = 0
RSI_LEVEL_1 = 1
RSI_LEVEL_2 = 2
RSI_LEVEL_3 = 3
RSI_DELTA = 3

# RSI_LEVEL_0_THRESHOLD = 30
RSI_LEVEL_1_THRESHOLD = 90
RSI_LEVEL_2_THRESHOLD = 17 
RSI_LEVEL_3_THRESHOLD = 10

SMA_5_LEVEL_0 = 0 # sma_5 < sma_10
SMA_5_LEVEL_1 = 0 # sma_5 >= sma_10 && sma_5 < sma_20
SMA_5_LEVEL_1 = 0 # sma_5 >= sma_10 && sma_5 < sma_20
RSI_DELTA = 3

reminder_under_30 = 0
reminder_under_20 = 0
reminder_under_15 = 0

CACHE_DIR = '__binance_cache__'

def init_indicator_file(symbol):
    config = configparser.ConfigParser()
    config['indicator'] = { 'rsi_level'             : '0',
                            'sma_5_level'           : '0',
                            'is_sma5_over_sma_20'   : '0'}

    with open(indicator_file, 'w') as configfile:
        config.write(configfile)

    print(indicator_file + " is created")

def read_rsi_level(symbol):
    rsi_level = RSI_LEVEL_0
    # print(sys._getframe().f_code.co_name)
    if os.path.isfile(indicator_file):
        config = configparser.ConfigParser()
        config.read(indicator_file)
        rsi_level = config['indicator']['rsi_level']
    else:
        init_indicator_file(symbol)

    return rsi_level

def write_rsi_level(symbol, rsi_lv):
    config = configparser.ConfigParser()
    config.read(indicator_file)
    indicator = config['indicator']
    indicator['rsi_level'] = str(rsi_lv)
    with open(indicator_file, 'w') as configfile:
        config.write(configfile)

def read_sma_5_level(symbol):
    rsi_level = RSI_LEVEL_0
    # print(sys._getframe().f_code.co_name)
    if os.path.isfile(indicator_file):
        config = configparser.ConfigParser()
        config.read(indicator_file)
        rsi_level = config['indicator']['sma_5_level']
    else:
        init_indicator_file(symbol)

    return rsi_level

def write_sma_5_level(symbol, sma_5_lv):
    config = configparser.ConfigParser()
    config.read(indicator_file)
    indicator = config['indicator']
    indicator['sma_5_level'] = str(sma_5_lv)
    with open(indicator_file, 'w') as configfile:
        config.write(configfile)

print(telegram_api.token)
print(telegram_api.chat_id)
#init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
#init env
token = os.environ.get('tele_bot_binance_toke')
chat_id = os.environ.get('tele_bot_binance_chat_id')
client = Client(api_key, api_secret)
indicator_file = CACHE_DIR + '/indicator_' + symbol + '.dat'

buy_temp_path = CACHE_DIR + '/buy_' + symbol + '.txt'
buy_csv_data_path = CACHE_DIR + 'buy_' + symbol + '_table.csv'

# try:
pair_coin_price = client.get_symbol_ticker(symbol=symbol)
# get timestamp of earliest date data is available
timestamp = client._get_earliest_valid_timestamp(symbol, his_interval)
bars = client.get_historical_klines(symbol, his_interval, timestamp, limit = 500)

# delete unwanted data - just keep date, open, high, low, close
for line in bars:
    del line[5:]
coin_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
coin_df.set_index('date', inplace=True)
coin_df.to_csv(buy_csv_data_path)

coin_df = pd.read_csv(buy_csv_data_path)
coin_df.index = pd.to_datetime(coin_df.index, unit='ms')
coin_df['sma_5'] = btalib.sma(coin_df.close, period=5).df

#### 1. Notify RSI level
rsi = btalib.rsi(coin_df, period=6)
current_rsi = rsi.df.rsi[-1]
# print((symbol + ': RSI is ' + '{:.2f}').format(current_rsi))
rsi_level = int(read_rsi_level(symbol))

if rsi_level == RSI_LEVEL_0:
    if current_rsi < RSI_LEVEL_1_THRESHOLD:
        telegram_api.send_msg(symbol + " : " + LOG_TAG + "RSI " + his_interval + " is below " + str(RSI_LEVEL_1_THRESHOLD))
        # rsi_level = RSI_LEVEL_1
        write_rsi_level(symbol, RSI_LEVEL_1)
elif rsi_level == RSI_LEVEL_1:
    if current_rsi < RSI_LEVEL_2_THRESHOLD:
        telegram_api.send_msg(symbol + " : " + LOG_TAG + "RSI " + his_interval + " is below " + str(RSI_LEVEL_2_THRESHOLD))
        # rsi_level = RSI_LEVEL_2
        write_rsi_level(symbol, RSI_LEVEL_2)
    if current_rsi > RSI_LEVEL_1_THRESHOLD + RSI_DELTA:
        telegram_api.send_msg(symbol + " : " + LOG_TAG + "RSI " + his_interval + " is over " + str(RSI_LEVEL_1_THRESHOLD))
        # rsi_level = RSI_LEVEL_0
        write_rsi_level(symbol, RSI_LEVEL_0)
elif rsi_level == RSI_LEVEL_2:
    if current_rsi < RSI_LEVEL_3_THRESHOLD:
        telegram_api.send_msg(symbol + " : " + LOG_TAG + "RSI " + his_interval + " is below " + str(RSI_LEVEL_3_THRESHOLD))
        # rsi_level = RSI_LEVEL_3
        write_rsi_level(symbol, RSI_LEVEL_3)
    if current_rsi > RSI_LEVEL_2_THRESHOLD + RSI_DELTA:
        telegram_api.send_msg(symbol + " : " + LOG_TAG + "RSI " + his_interval + " is over " + str(RSI_LEVEL_2_THRESHOLD))
        # rsi_level = RSI_LEVEL_1
        write_rsi_level(symbol, RSI_LEVEL_1)
elif rsi_level == RSI_LEVEL_3:
    if current_rsi > RSI_LEVEL_3_THRESHOLD + RSI_DELTA:
        telegram_api.send_msg(symbol + " : " + LOG_TAG + "RSI " + his_interval + " is over " + str(RSI_LEVEL_3_THRESHOLD))
        # rsi_level = RSI_LEVEL_2
        write_rsi_level(symbol, RSI_LEVEL_2)

        
### 2. Notify sma_5 level
# Caculate SMA 5,SMA 10, SMA 20
sma_5 = btalib.sma(coin_df.close, period=5).df
sma_10 = btalib.sma(coin_df.close, period=10).df
sma_20 = btalib.sma(coin_df.close, period=20).df
sma_5_level = read_sma_5_level(symbol)

if sma_5_level == SMA_5_LEVEL_0:
    if sma_5 > sma_10:
        msg = symbol + ': SMA(5) is over SMA(10). Price: ' + str(pair_coin_price) + '. RSI: ' + str(current_rsi)
        telegram_api.send_msg(msg)
        write_rsi_level(symbol, RSI_LEVEL_1)
elif sma_5_level == SMA_5_LEVEL_1:
    if sma_5 > sma_20:
        msg = symbol + ': SMA(5) is over SMA(10). Price: ' + str(pair_coin_price) + '. RSI: ' + str(current_rsi)
        telegram_api.send_msg(msg)
        write_rsi_level(symbol, RSI_LEVEL_1)
    if sma_5 < sma_10 - 
        write_rsi_level(symbol, RSI_LEVEL_1)
    msg = symbol + ': SMA(5) is over SMA(10). Price: ' + pair_coin_price['price'] + '. RSI: ' + str(round(current_rsi))
    print(msg)

# print(coin_df.sma_5[-1])
# print(coin_df.sma_10[-1])
# print(coin_df.sma_20[-1])

# except BinnaceAPIException as e:
#     print('Something went wrong. Error occured at %s. Wait for 1 hour.' % (datetime.datetime.now()))
#     sleep(3600)
#     client = Client(api_key, api_secret)
