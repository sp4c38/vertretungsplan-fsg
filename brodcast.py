# A program which makes it posible to make a easy brodcast to all groups and channels

import configparser
import json

from modules import telegram
from settings import settings

def get_chat_ids():
    telegram_cfg_uniformly = configparser.ConfigParser()
    telegram_cfg_uniformly.read(settings["configuration_path"]["telgram_cfg"])
    telegram_cfg_uniformly = telegram_cfg_uniformly["uniformly"] # Configurations which are uniformly

    telegram_cfg = configparser.ConfigParser()
    telegram_cfg.read(settings["configuration_path"]["telgram_cfg"])
    telegram_cfg = telegram_cfg["telegram_cfg"]

    user_data = json.load(open(settings["user_file"]))
    
    return telegram_cfg_uniformly, telegram_cfg, user_data

def ask_to_send():
    send_direct = input("Send to direct chat ids? (y)es/(n)o ")
    if "y" in send_direct:
        send_direct = True
    else:
        send_direct = False

    send_indirect = input("Send to indirect chat ids? (y)es/(n)o ")
    if "y" in send_indirect:
        send_indirect = True
    else:
        send_indirect = False

    return {"send_direct":send_direct, "send_indirect":send_indirect}

def main():
    text = open("/Users/sp4c38/text.txt", "r").read() #str(input("Enter text to brodcast:"))
    print(text)
    telegram_cfg_uniformly, telegram_cfg, user_data = get_chat_ids()

    direct_chat_ids = [user_data["users"][x]["chat_id"] for x in user_data["users"]] # Direct communication with the user
    indirect_chat_ids = [y for y in telegram_cfg["group_chat_ids"].split(",") if y] # Indirect communication (through groups) with the user

    print("We would send this message to:")
    print(f"Direct chat ids: {', '.join(direct_chat_ids)}")
    print(f"Indirect chat ids: {', '.join(indirect_chat_ids)}")

    send_to = ask_to_send()

    if send_to["send_direct"]:
        telegram.send_message(telegram_cfg, telegram_cfg_uniformly, [direct_chat_ids], text)

    if send_to["send_indirect"]:
        telegram.send_message(telegram_cfg, telegram_cfg_uniformly, [indirect_chat_ids], text)


if __name__ == '__main__':
    main()