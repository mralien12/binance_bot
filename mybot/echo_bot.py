import os
import telebot
import datetime
import btalib
from binance.client import Client
from threading import Thread
import pandas as pd

CACHE_DIR = '__binance_cache__'
KLINE_DIR = CACHE_DIR + '/kline/'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

if not os.path.exists(KLINE_DIR):
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
    import btalib
    print("Loading candle: " + sym)
    # get timestamp of earliest date data is available
    his_interval = '1h'
    # timestamp = datetime.datetime.now().timestamp() - 20 * 60 * 60 # 20 hours ago
    # timestamp = client._get_earliest_valid_timestamp(sym, his_interval)
    data_kline = client.get_historical_klines(sym, Client.KLINE_INTERVAL_15MINUTE, "2 day ago UTC")
    # data_kline = client.get_historical_klines(sym, Client.KLINE_INTERVAL_1HOUR, "24 hours ago UTC")
    # data_kline = client.get_historical_klines(sym, Client.KLINE_INTERVAL_1HOUR, timestamp, limit=500)

    # delete unwanted data - just keep date, open, high, low, close
    for col in data_kline:
        del col[8:]
    coin_df = pd.DataFrame(data_kline, columns=['date', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'quote_vol'])
    # coin_df = pd.DataFrame(data_kline, columns=['date', 'open', 'high', 'low', 'close'])
    coin_df.set_index('date', inplace=True)
    coin_df.to_csv(KLINE_DIR + sym + '.dat')

    coin_df = pd.read_csv(KLINE_DIR + sym + '.dat')
    coin_df.index = pd.to_datetime(coin_df.index, unit='ms')
    # coin_df['sma_5'] = btalib.sma(coin_df.close, period=5).df
    rsi = btalib.rsi(coin_df, period=6)
    current_rsi = rsi.df.rsi[-1]
    print(current_rsi)

ticker_list = client.get_all_tickers()
symbols = []
### Get all symbol with USDT
print("Get all symbols")
for ticker in ticker_list:
    if str(ticker['symbol'])[-4:] == 'USDT':
        symbols.append(ticker['symbol'])

# get 4h candles for symbols
print('Loading candle data for symbols...')
# fake_symbol = ['ADAUSDT', 'LINKUSDT']
fake_symbol = ['LINKUSDT']
# for sym in symbols:
for sym in fake_symbol:
    Thread(target=load_candles, args=(sym,)).start()

# for sym in fake_symbol:

# while len(candles) < len(symbols):
#     print('%s/%s loaded' %(len(candles), len(symbols)), end='\r', flush=True)
#     time.sleep(0.1)
print("Bot is running!!!")
# bot.polling()