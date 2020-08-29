import arrow
import configparser
import json
import requests
import time
import traceback

# import our settings
from modules import handle_updates
from settings import settings

def get_prerequisites(settings):
    telegram_config_file = configparser.ConfigParser()
    telegram_config_file.read(settings["configuration_path"]["telegram"])

    telegram_config = telegram_config_file["telegram_cfg"]
    telegram_api = telegram_config_file["telegram_api_urls"]

    updates_storage = json.load(open(settings["updates_file"])) # Stores data for updates
    user_data = json.load(open(settings["user_file"])) # Stores users

    return telegram_config, telegram_api, updates_storage, user_data


def main():
    telegram_config, telegram_api, updates_storage, user_data = get_prerequisites(settings)

    get_updates_url = telegram_api["get_updates_url"].format(telegram_config["bot_token"])

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

        handle_updates.main(updates_storage, user_data, updates, telegram_config, telegram_api, settings)
        json.dump(updates_storage, open(settings["updates_file"], "w"))
        json.dump(user_data, open(settings["user_file"], "w"))
        print("Saved files.")
        print()

        time.sleep(2)

if __name__ == '__main__':
    try:
        print(f"Session started {arrow.utcnow().format()} UTC.\n")
        main()
        print(f"\nSession ended {arrow.utcnow().format()} UTC.")

    except requests.exceptions.ConnectionError:
        print("Problems connecting to the internet.")
        print(f"\nSession ended {arrow.utcnow().format()} UTC.")

    except Exception as exception:
        traceback.print_exc()
        print(f"\nSession ended {arrow.utcnow().format()} UTC.")
