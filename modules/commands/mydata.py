from modules import telegram


def main(update, user, tele_config, tele_config_uniformly, settings):
    if not user["classes"]:
        classes_vertretung = "Keine"
    else:
        classes_vertretung = ", ".join(user["classes"])

    myinfo_text = open(settings["messages"]["myinfo"]).read().format(classes_vertretung, user["user_id"])
    chat_id_list = [user["chat_id"]]

    telegram.send_message(tele_config, tele_config_uniformly, chat_id_list, myinfo_text)
    print("Send a user his information.")
