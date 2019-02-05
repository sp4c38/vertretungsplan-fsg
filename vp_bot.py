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

def send_message(bot_token=None, chat_id=None, message=None, telegram_config=None):
    if telegram_config == None:
        telegram_config = utils.get_telegram_config_data()
    
    if bot_token == None:
        bot_token = telegram_config.get('telegram', 'bot_token')    
    if chat_id == None:
        chat_id = telegram_config.get('telegram', 'chat_id')
        chat_id2 = telegram_config.get('telegram', 'chat_id2')
   
    if message == None:
        print("\'message\' is None")
        return
    if not message:
        print("\'message\' has no content")
        return

    bot = telepot.Bot(bot_token)
    bot.sendMessage(chat_id, text=message)
    bot.sendMessage(chat_id2, text=message)
    print("--> message successfully sent")
    
def read_latest_converted():
    cache_file_path = utils.get_cache_file_path()
    with open(cache_file_path) as f:
        vp_converted = f.read()
    return vp_converted

def main():
    latest_converted = read_latest_converted()
    """ The function 'send_message' sends the message, and (if not given) gets
    the latest converted file, chat id, bot token and telegram config data """
    send_message(message=latest_converted)

if __name__ == '__main__':
    main()
