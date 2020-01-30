import configparser
import json
import requests
import time

# import our settings
from modules import handle_updates
from settings import settings

def get_config(settings):
    tele_config = configparser.ConfigParser() # The telegram config for single_vertretungsplan
    tele_config.read(settings["configuration_path"]["telgram_cfg"])
    tele_config = tele_config["single_telegram_cfg"]

    # Uniformly configurations are used both in single_ver* and all_ver* 
    tele_config_uniformly= configparser.ConfigParser() # The uniformly (einheitlich) config
    tele_config_uniformly.read(settings["configuration_path"]["telgram_cfg"])
    tele_config_uniformly = tele_config_uniformly["uniformly"]

    return tele_config, tele_config_uniformly


def main():
    updates_storage = json.load(open(settings["updates_file"])) # Stores data for updates
    user_data = json.load(open(settings["user_file"])) # Stores users

    tele_config, tele_config_uniformly = get_config(settings)

    get_updates_url = tele_config_uniformly["get_updates_url"].format(tele_config["bot_token"])

    # Running in a while-true loop with a time delay
    while True:
        print("Checking for updates...")
        updates = json.loads(requests.get(get_updates_url).text) # json.load(open("/home/leon/Desktop/data.txt")) # Updates from telegram api
        handle_updates.main(updates_storage, user_data, updates, tele_config, tele_config_uniformly, settings)
        
        json.dump(updates_storage, open(settings["updates_file"], "w"))
        json.dump(user_data, open(settings["user_file"], "w"))
        print("Saved files.")
        print()
        time.sleep(5)

if __name__ == '__main__':
    main()