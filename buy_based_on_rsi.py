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

if len(sys.argv) < 2:
    sys.exit()
# Define constant
pair_coin_symbol = sys.argv[1]
# print("Runing script to track RSI of " + pair_coin_symbol)
# valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
history_interval = '1h'
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
RSI_LEVEL_1_THRESHOLD = 25
RSI_LEVEL_2_THRESHOLD = 17 
RSI_LEVEL_3_THRESHOLD = 10
rsi_level = RSI_LEVEL_0

cache_dir = '__binance_cache__'
buy_temp_path = cache_dir + '/buy_' + pair_coin_symbol + '.txt'
buy_csv_data_path = cache_dir + 'buy_' + pair_coin_symbol + '_table.csv'

def init_bot(symbol):
    indicator_file = cache_dir + '/indicator_' + pair_coin_symbol + '.dat'
    config = configparser.ConfigParser()
    config['indicator'] = { 'rsi_level'             : '0',
                            'is_sma5_over_sma_10'   : '0',
                            'is_sma5_over_sma_20'   : '0'}

    with open(indicator_file, 'w') as configfile:
        config.write(configfile)

    print(indicator_file)
    exit

def send_tele_msg_one(text):
    return 
    text = '1h: ' + text
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    resp = requests.post('https://api.telegram.org/bot{}/sendMessage'.format(token), params)
    resp.raise_for_status()

def send_tele_msg(text):
    return
    text = '1h: ' + text
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    i = 0
    while i < reminder_msg_count:
        resp = requests.post('https://api.telegram.org/bot{}/sendMessage'.format(token), params)
        resp.raise_for_status()
        time.sleep(1)
        i = i + 1

def read_rsi_level(pair_coin_symbol):
    rsi_level = 0
    try:
        f = open(buy_temp_path)
        rsi_level = int(f.read())
        f.close()
    except (OSError, IOError) as e:
        # if file is not existed, defaul rsi_level is 0
        f = open(buy_temp_path, 'w')
        f.write(str(rsi_level))
        f.close()
    return rsi_level

def write_rsi_level(pair_coin_symbol, rsi_lv):
        f = open(buy_temp_path, 'w')
        f.write(str(rsi_lv))
        f.close()


#init
reminder_under_30 = 0
reminder_under_20 = 0
reminder_under_15 = 0
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
#init env
token = os.environ.get('tele_bot_binance_toke')
chat_id = os.environ.get('tele_bot_binance_chat_id')
client = Client(api_key, api_secret)

init_bot(pair_coin_symbol)

try:
    pair_coin_price = client.get_symbol_ticker(symbol=pair_coin_symbol)
    # get timestamp of earliest date data is available
    timestamp = client._get_earliest_valid_timestamp(pair_coin_symbol, history_interval)
    bars = client.get_historical_klines(pair_coin_symbol, '1h', timestamp, limit = 500)

    # delete unwanted data - just keep date, open, high, low, close
    for line in bars:
        del line[5:]
    coin_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
    coin_df.set_index('date', inplace=True)
    coin_df.to_csv(buy_csv_data_path)

    coin_df = pd.read_csv(buy_csv_data_path)
    coin_df.index = pd.to_datetime(coin_df.index, unit='ms')
    coin_df['sma_5'] = btalib.sma(coin_df.close, period=5).df

    rsi = btalib.rsi(coin_df, period=6)
    current_rsi = rsi.df.rsi[-1]
    print((pair_coin_symbol + ': RSI is ' + '{:.2f}').format(current_rsi))

    rsi_level = read_rsi_level(pair_coin_symbol)
    if rsi_level == RSI_LEVEL_0:
        if current_rsi < RSI_LEVEL_1_THRESHOLD:
            send_tele_msg("RSI is below " + str(RSI_LEVEL_1_THRESHOLD) + ".Buy " + pair_coin_symbol)
            # rsi_level = RSI_LEVEL_1
            write_rsi_level(pair_coin_symbol, RSI_LEVEL_1)
    elif rsi_level == RSI_LEVEL_1:
        if current_rsi < RSI_LEVEL_2_THRESHOLD:
            send_tele_msg("RSI is below " + str(RSI_LEVEL_2_THRESHOLD) + ".Buy " + pair_coin_symbol)
            # rsi_level = RSI_LEVEL_2
            write_rsi_level(pair_coin_symbol, RSI_LEVEL_2)
        if current_rsi > RSI_LEVEL_1_THRESHOLD + RSI_DELTA:
            send_tele_msg_one("RSI is over " + str(RSI_LEVEL_1_THRESHOLD) + ".Buy " + pair_coin_symbol)
            # rsi_level = RSI_LEVEL_0
            write_rsi_level(pair_coin_symbol, RSI_LEVEL_0)
    elif rsi_level == RSI_LEVEL_2:
        if current_rsi < RSI_LEVEL_3_THRESHOLD:
            send_tele_msg("RSI is below " + str(RSI_LEVEL_3_THRESHOLD) + ".Buy " + pair_coin_symbol)
            # rsi_level = RSI_LEVEL_3
            write_rsi_level(pair_coin_symbol, RSI_LEVEL_3)
        if current_rsi > RSI_LEVEL_2_THRESHOLD + RSI_DELTA:
            send_tele_msg("RSI is over " + str(RSI_LEVEL_2_THRESHOLD) + ".Buy " + pair_coin_symbol)
            # rsi_level = RSI_LEVEL_1
            write_rsi_level(pair_coin_symbol, RSI_LEVEL_1)
    elif rsi_level == RSI_LEVEL_3:
        if current_rsi > RSI_LEVEL_3_THRESHOLD + RSI_DELTA:
            send_tele_msg("RSI is over " + str(RSI_LEVEL_3_THRESHOLD) + ".Buy " + pair_coin_symbol)
            # rsi_level = RSI_LEVEL_2
            write_rsi_level(pair_coin_symbol, RSI_LEVEL_2)

            
    # Caculate SMA 5,SMA 10, SMA 20
    coin_df['sma_5'] = btalib.sma(coin_df.close, period=5).df
    coin_df['sma_10'] = btalib.sma(coin_df.close, period=10).df
    coin_df['sma_20'] = btalib.sma(coin_df.close, period=20).df

    if coin_df.sma_5[-1] > coin_df.sma_10[-1]:
        msg = pair_coin_symbol + ': SMA(5) is over SMA(10). Price: ' + str(pair_coin_price) + '. RSI: ' + str(current_rsi)
        print(msg)
    else:
        msg = pair_coin_symbol + ': SMA(5) is over SMA(10). Price: ' + pair_coin_price['price'] + '. RSI: ' + str(round(current_rsi))
        print(msg)

    print(coin_df.sma_5[-1])
    print(coin_df.sma_10[-1])
    print(coin_df.sma_20[-1])

except BinnaceAPIException as e:
    print('Something went wrong. Error occured at %s. Wait for 1 hour.' % (datetime.datetime.now()))
    sleep(3600)
    client = Client(api_key, api_secret)
