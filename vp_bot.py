import telepot
import os
import time
import configparser
import sys

import utils    

def get_token():
    credentials = configparser.ConfigParser()
    token_path = os.path.expanduser('~/.config/vertretungsplan/telegram.ini')
    credentials.read(token_path)
    return credentials.get('telegram', 'bot_token')

def get_chat_id():
    credentials = configparser.ConfigParser()
    token_path = os.path.expanduser('~/.config/vertretungsplan/telegram.ini')
    credentials.read(token_path)
    return credentials.get('telegram', 'chat_id')

def send_message(bot_token=None, chat_id=None, message=None):
    if bot_token == None:
        return
    if chat_id == None:
        chat_id = get_chat_id()
    if message == None:
        return

    bot = telepot.Bot(bot_token)
    print("--> sending message...")
    bot.sendMessage(chat_id, text=message)
    print("--> message sent.")

def read_latest_converted():
    cache_file_path = utils.get_cache_file_path()
    with open(cache_file_path) as f:
        vp_converted = f.read()
    send_message(bot_token=get_token() ,chat_id=get_chat_id(), message=vp_converted)

def main():
    bot_token = get_token()
    bot = telepot.Bot(bot_token)
    read_latest_converted()

if __name__ == '__main__':
    main()
