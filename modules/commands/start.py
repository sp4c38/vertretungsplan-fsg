import json

from modules import telegram

def main(update, user, tele_config, tele_config_uniformly, settings):
    start_text = open(settings["messages"]["start"]).read()
    chat_id_list = [user["chat_id"]]

    keyboardmarkup = json.load(open(settings["messages"]["main_markupkeyboard"]))

    telegram.send_msg_with_keyboard_markup(tele_config, tele_config_uniformly, chat_id_list, start_text, keyboardmarkup)
    print("Send start message and activated the main markup keyboard.")