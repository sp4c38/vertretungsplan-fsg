import json
import requests

def send_message(config, config_uniformly, chat_id_list, message):
    # config contains general telegram bot api like getUpdates link or sendMessage (they don't include the bot token)
    # contains bot data and the group chat id's
    url = config_uniformly["send_message_url"].format(config["bot_token"])

    for chat_id in chat_id_list:
        data = {
            "chat_id": chat_id,
            "text": message,
            "disable_notification": False,
        }

        requests.post(url=url, data=data)

    return True

def send_msg_with_keyboard_markup(config, config_uniformly, chat_id_list, message, keyboardmarkup):
    # Send a message with keyboard markup

    url = config_uniformly["send_message_url"].format(config["bot_token"])

    for chat_id in chat_id_list:
        data = {
            "chat_id": chat_id,
            "text": message,
            "disable_notification": False,
            "reply_markup": json.dumps(keyboardmarkup),
        }

        requests.post(url, data)
        
    return True