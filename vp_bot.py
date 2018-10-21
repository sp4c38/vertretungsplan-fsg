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

def main():
    bot_token = get_token()
    bot = telepot.Bot(bot_token)

    cache_file_path = utils.get_cache_file_path()
    with open(cache_file_path) as f:
        data = f.read()
    
    chat_id = get_chat_id()
    print("\nSending message...")
    bot.sendMessage(chat_id, text=data)
    print("--> Message sent.")



if __name__ == '__main__':
    main()