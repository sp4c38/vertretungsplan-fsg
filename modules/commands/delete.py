import json

from modules import telegram, utils


def main(update, user, tele_config, tele_config_uniformly, settings):
    chat_id_list = [user["chat_id"]]

    if user["delete_mode"] == True:
        if update["message"]["text"] == "Ja":
            print("User wants to delete his classes.")
            classes_before = user["classes"] # The classes before the deletion

            user["delete_mode"] = False
            print(f"Delete mode was disabled for {user['user_id']}")
            user["classes"] = []
            print(f"The classes {', '.join(classes_before)} for {user['user_id']} were successfully deleted.")

            successfully_deleted = open(settings["messages"]["delete_mode_successful"]).readlines()[0]

            keyboardmarkup = json.load(open(settings["messages"]["main_keyboardmarkup"]))
            telegram.send_msg_keyboard_markup(tele_config, tele_config_uniformly, chat_id_list, successfully_deleted, keyboardmarkup)
            print("Sent deletion successful message and reactivated the main keyboard markup.")
            return
        else:
            print("User wants to keep his classes")
            user["delete_mode"] = False
            print(f"Delete mode was disabled for {user['user_id']}")

            not_deleted = open(settings["messages"]["delete_mode_unsuccessful"]).readlines()[0]

            keyboardmarkup = json.load(open(settings["messages"]["main_keyboardmarkup"]))
            telegram.send_msg_keyboard_markup(tele_config, tele_config_uniformly, chat_id_list, not_deleted, keyboardmarkup)
            print("Sent deletion unsuccessful message and reactivated the main keyboard markup.")
            return

    else:
        if user["classes"]:
            user["delete_mode"] = True
            print(f"Enabled delete_mode for user {user['user_id']}")

            delete_text = open(settings["messages"]["delete"]).read()
            delete_text = delete_text.format(", ".join(user["classes"]))

            keyboardmarkup = json.load(open(settings["messages"]["delete_keyboard_markup"]))

            telegram.send_msg_keyboard_markup(tele_config, tele_config_uniformly, chat_id_list, delete_text, keyboardmarkup)
            print("Sent delete validation message.")
            return

        elif not user["classes"]:
            no_classes_to_delete = open(settings["messages"]["no_classes_to_delete"]).read()
            telegram.send_message(tele_config, tele_config_uniformly, chat_id_list, no_classes_to_delete)
            print(f"Sent no-classes-to-delete message to user {user['user_id']}")
            return
