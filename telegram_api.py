import requests
import os

REMINDER_MSG_REPETITION = 1
#init env
token = os.environ.get('tele_bot_binance_toke')
chat_id = os.environ.get('tele_bot_binance_chat_id')

def send_msg(text):
    print(text)
    text = '1h: ' + text
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    resp = requests.post('https://api.telegram.org/bot{}/sendMessage'.format(token), params)
    resp.raise_for_status()

def send_msg_repetition(text):
    text = '1h: ' + text
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    i = 0
    while i < REMINDER_MSG_REPETITION:
        resp = requests.post('https://api.telegram.org/bot{}/sendMessage'.format(token), params)
        resp.raise_for_status()
        time.sleep(1)
        i = i + 1