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

    # Running in a while-true loop with a time dela
    newest_update_id = 0 # The newest update id, is used to handle many messages with offset
    while True:
        print("Checking for updates...")
        if newest_update_id:
            headers = {"offset":str(newest_update_id)}
        else:
            headers = {}

        updates = json.loads(requests.get(get_updates_url, headers).text) # Updates from telegram api
        for x in updates["result"]: 
            if x["update_id"] > newest_update_id: 
                newest_update_id = x["update_id"]

        handle_updates.main(updates_storage, user_data, updates, tele_config, tele_config_uniformly, settings)
        json.dump(updates_storage, open(settings["updates_file"], "w"))
        json.dump(user_data, open(settings["user_file"], "w"))
        print("Saved files.")
        print()

        if settings["debug"]:
            time.sleep(5)
        else:
            time.sleep(0.5)

if __name__ == '__main__':
    if settings["debug"]: # settings["debug"]: True
        main()
    else: # settings["debug"]: False
        try:
            main()
        except requests.exceptions.ConnectionError:
            print("We had problems connecting to the internet.")
        except:
            print("The program was interrupted.")