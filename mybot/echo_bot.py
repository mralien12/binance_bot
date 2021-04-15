import os
import telebot
import datetime
import btalib
import time
import shutil
from binance.client import Client
from threading import Thread
import pandas as pd

CACHE_DIR = '/tmp/__binance_cache__'
KLINE_DIR = CACHE_DIR + '/kline/'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

if os.path.exists(KLINE_DIR):
    shutil.rmtree(KLINE_DIR)
os.makedirs(KLINE_DIR)

token = os.environ.get('tele_bot_binance_toke')
chat_id = os.environ.get('tele_bot_binance_chat_id')

api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
client = Client(api_key, api_secret)


bot = telebot.TeleBot(token, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how a u doing?")

@bot.message_handler(commands=['getAllSymbol'])
def get_all_symbol(message):
    bot.reply_to(message, "Getting list of USDT pair...")
    ticker_list = client.get_all_tickers()
    with open(CACHE_DIR + "/all_symbol.txt", 'w') as f:
        ### Get all symbol with USDT
        for ticker in ticker_list:
            if str(ticker['symbol'])[-4:] == 'USDT':
                f.write(ticker['symbol'] + '\n')
                # symbols.append(ticker['symbol']
        f.close()
    bot.reply_to(message, "GET ALL SYMBOL => DONE")

# @bot.message_handler(func=lambda m: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)

def load_candles(sym):
    print("Loading candle: " + sym)
    # get timestamp of earliest date data is available
    his_interval = '1h'
    # timestamp = datetime.datetime.now().timestamp() - 20 * 60 * 60 # 20 hours ago
    # timestamp = client._get_earliest_valid_timestamp(sym, his_interval)
    # data_kline = client.get_historical_klines(sym, Client.KLINE_INTERVAL_15MINUTE, "2 day ago UTC")
    data_kline = client.get_historical_klines(sym, Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC")
    # data_kline = client.get_historical_klines(sym, Client.KLINE_INTERVAL_1HOUR, "24 hours ago UTC")
    # data_kline = client.get_historical_klines(sym, Client.KLINE_INTERVAL_1HOUR, timestamp, limit=500)

    # delete unwanted data - just keep date, open, high, low, close
    for col in data_kline:
        del col[8:]
    coin_df = pd.DataFrame(data_kline, columns=['date', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'quote_vol'])
    coin_df.set_index('date', inplace=True)
    coin_df.to_csv(KLINE_DIR + sym + '.dat')


    coin_df = pd.read_csv(KLINE_DIR + sym + '.dat')
    print(coin_df.tail(1)['quote_vol'])
    exit()
    # coin_df.index = pd.to_datetime(coin_df.index, unit='ms')
    # # coin_df['sma_5'] = btalib.sma(coin_df.close, period=5).df
    # rsi = btalib.rsi(coin_df, period=6)
    # current_rsi = rsi.df.rsi[-1]
    # print(current_rsi)

ticker_list = client.get_all_tickers()
symbols = []
# count = 0
### Get all symbol with USDT
print("Get all symbols")
with open(CACHE_DIR + "/all_symbol.txt", 'w') as f:
    ### Get all symbol with USDT
    for ticker in ticker_list:
        if str(ticker['symbol'])[-4:] == 'USDT' and float(ticker['price']) != 0:
            f.write(ticker['symbol'] + '\n')
            symbols.append(ticker['symbol'])
            # count = count + 1
            # if count > 20:
            #     break
f.close()

# get 4h candles for symbols
print('Loading candle data for symbols...')
# fake_symbol = ['NEOUSDT', 'ADAUSDT']
# fake_symbol = ['LINKUSDT']
# for sym in symbols:
threads = []
with open(CACHE_DIR + '/all_symbol.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        symbol = line.strip()
        load_candles(symbol)
        # t = Thread(target=load_candles, args=(symbol,)).start()
        # threads.append(t)
        # load_candles(symbol)
f.close()

# for thread in threads:
#     thread.start()
#     time.sleep(5)

# for thread in threads:
#     threads.join()
# for sym in symbols:
#     # Thread(target=load_candles, args=(sym,)).start()
#     load_candles(sym)
# load_candles('1INCHUSDT')

# for sym in fake_symbol:

# while len(os.listdir(KLINE_DIR)) < len(symbols):
#     list_file_in_kdir = os.listdir(KLINE_DIR)
#     print('%s/%s loaded' %(len(list_file_in_kdir), len(symbols)), end='\r', flush=True)
#     time.sleep(0.1)

print("Bot is running!!!")
# bot.polling()