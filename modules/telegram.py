import json
import requests


def send_message(config, telegram_api, chat_id_list, message):
    # config contains general telegram bot api like getUpdates link or sendMessage (they don't include the bot token)
    # contains bot data and the group chat id's
    url = telegram_api["send_message_url"].format(config["bot_token"])

    for chat_id in chat_id_list:
        data = {
            "chat_id": chat_id,
            "text": message,
            "disable_notification": False,
        }

        requests.post(url=url, data=data)

    return True


def send_msg_keyboard_markup(config, telegram_api, chat_id_list, message, keyboardmarkup):
    # Send a normal message
    # If keyboardmarkup is qual False: the current keyboard markup is removed
    # If keyboardmarkup is a dictionary: this dict is send as the keyboard markup

    url = telegram_api["send_message_url"].format(config["bot_token"])

    for chat_id in chat_id_list:
        data = {
            "chat_id": chat_id,
            "text": message,
            "disable_notification": False,
        }
        if keyboardmarkup:
            data["reply_markup"] = json.dumps(keyboardmarkup)
        elif not keyboardmarkup:
            data["reply_markup"] = json.dumps({"remove_keyboard": True})

        requests.post(url, data)

    return True
