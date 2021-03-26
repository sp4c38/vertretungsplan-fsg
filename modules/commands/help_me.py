from modules import telegram

# must use help_me, because help isn't valid


def main(user, tele_config, tele_config_uniformly, settings):
    help_text = open(settings["messages"]["help"]).read()
    chat_id_list = [user["chat_id"]]

    telegram.send_message(tele_config, tele_config_uniformly, chat_id_list, help_text)
    print(f"Send help message to user {user['user_id']}.")
