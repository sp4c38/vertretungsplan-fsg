import json
import re

from modules import telegram, utils


def main(update, user, user_data, tele_config, tele_config_uniformly, settings):
    chat_id_list = [user["chat_id"]]

    if user["setup_mode"] == True and update["message"]["text"]:
        validation_classes =  utils.get_validate_classes(update["message"]["text"])
        successful_string = ", ".join(validation_classes["successful"])
        unsuccessful_string = ", ".join(validation_classes["unsuccessful"])

        if len(validation_classes["successful"]) > 0:
            if len(validation_classes["successful"]) == 1: # Do this if-function to use different messages for either singular or plural messages
                correct_msg = open(settings["messages"]["validation_successful"]).readlines()[0]
                correct_msg = correct_msg.format(successful_string).replace("\n", "")
            elif len(validation_classes["successful"]) > 1:
                correct_msg = open(settings["messages"]["validation_successful"]).readlines()[1]
                correct_msg = correct_msg.format(successful_string).replace("\n", "")
            
            for c in validation_classes["successful"]:
                if not c in user["classes"]:
                    user["classes"].append(c)
            
            print(f"Added {successful_string} to user {user['user_id']}.")

            if len(validation_classes["unsuccessful"]) == 0:
                user["setup_mode"] = False # Deactivate setup mode if only allowed classes were given
                print(f"Deactivated setup mode for user {user['user_id']}")

            telegram.send_message(tele_config, tele_config_uniformly, chat_id_list, correct_msg)
            print("Send validation successful message.")
            if not validation_classes["unsuccessful"] and len(user["classes"]) == 1: # Send a happy message and activate the main markup keyboard again
                stpmde_deactivated_msg = open(settings["messages"]["setup_mode_deactivated"]).readlines()[0] # Setup mode deactivated message
                keyboardmarkup = json.load(open(settings["messages"]["main_markupkeyboard"]))
                telegram.send_msg_with_keyboard_markup(tele_config, tele_config_uniformly, chat_id_list, stpmde_deactivated_msg, keyboardmarkup)
                print("Send setup mode deactivated message and reactivated the main markup keyboard.")
            elif not validation_classes["unsuccessful"] and len(user["classes"]) > 1:
                stpmde_deactivated_msg = open(settings["messages"]["setup_mode_deactivated"]).readlines()[1] # Setup mode deactivated message
                keyboardmarkup = json.load(open(settings["messages"]["main_markupkeyboard"]))
                telegram.send_msg_with_keyboard_markup(tele_config, tele_config_uniformly, chat_id_list, stpmde_deactivated_msg, keyboardmarkup)
                print("Send setup mode deactivated message and reactivated the main markup keyboard.")
            

        if len(validation_classes["unsuccessful"]) > 0:
            if len(validation_classes["unsuccessful"]) == 1: # Do this if-function to use different messages for either singular or plural messages
                not_correct_msg = open(settings["messages"]["validation_unsuccessful"]).readlines()[0]
                not_correct_msg = not_correct_msg.format(unsuccessful_string).replace("\n", "")
            elif len(validation_classes["unsuccessful"]) > 1:
                not_correct_msg = open(settings["messages"]["validation_unsuccessful"]).readlines()[1]
                not_correct_msg = not_correct_msg.format(unsuccessful_string).replace("\n", "")

            print(f"Could not add {unsuccessful_string} for user {user['user_id']}.")
            telegram.send_message(tele_config, tele_config_uniformly, chat_id_list, not_correct_msg)
            print("Send validation unsuccessful message.")

    else:
        user["setup_mode"] = True
        print(f"Enabled setup_mode for user {user['user_id']}")
    
        setup_text = open(settings["messages"]["setup"]).read()
    
        telegram.send_message(tele_config, tele_config_uniformly, chat_id_list, setup_text)
        print("Send setup info message.")