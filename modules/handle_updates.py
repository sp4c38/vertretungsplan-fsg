from modules import handle_user
from modules.commands import start, setup, mydata, delete, help_me


def check_fields(update):
    # Checks if all required fileds are present
    # Return True if everything is O.K.
    # Return False if a/multiple field/fields is/are missing

    try:
        if (
            update["update_id"]
            and update["message"]["text"]
            and update["message"]["from"]["id"]
            and update["message"]["chat"]["id"]
        ):
            return True
        else:
            return False
    except:
        return False


def main(updates_storage, user_data, updates, tele_config, tele_config_uniformly, settings):
    current_update_ids = []

    for update in updates["result"]:

        fields_completely = check_fields(update)

        if not fields_completely:
            continue

        update_id = str(update["update_id"])
        current_update_ids.append(update_id)

        if not update_id in updates_storage["updates"]:

            user = handle_user.check_exists(user_data, update)  # Returns user information
            msg_text = update["message"]["text"].lower()

            if msg_text == "einrichten" or user["setup_mode"] == True:
                print(f"User {user['user_id']} requested \"einrichten\" or his setup mode is activated.")
                setup.main(update, user, tele_config, tele_config_uniformly, settings)

            if msg_text == "/start":
                print(f"User {user['user_id']} requested \"start\"")
                start.main(user, tele_config, tele_config_uniformly, settings)

            if msg_text == "löschen" or user["delete_mode"] == True:
                print(f"User {user['user_id']} requested \"löschen\" or his delete mode is activated.")
                delete.main(update, user, tele_config, tele_config_uniformly, settings)

            if msg_text == "meine daten":
                print(f"User {user['user_id']} requested \"meine daten\"")
                mydata.main(update, user, tele_config, tele_config_uniformly, settings)

            if msg_text == "hilfe":
                print(f"User {user['user_id']} requested \"hilfe\"")
                help_me.main(user, tele_config, tele_config_uniformly, settings)

            updates_storage["updates"].append(update_id)
        else:
            continue

    to_sort_out = []
    for x in updates_storage["updates"]:
        if not x in current_update_ids:
            to_sort_out.append(x)

    for y in to_sort_out:
        updates_storage["updates"].remove(y)
