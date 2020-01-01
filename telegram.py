import configparser
import requests

def send_message(settings, message):
    print("Sending message...")

    config = configparser.ConfigParser()
    config.read(settings["configuration_path"]["telgram_cfg"])

    url = config["telegram"]["send_message_url"].format(config["telegram"]["bot_token"])

    data = {
        "chat_id": config["telegram"]["chat_id"],
        "text": message,
        "disable_notification": False,
    }

    requests.post(url=url, data=data)
    return True