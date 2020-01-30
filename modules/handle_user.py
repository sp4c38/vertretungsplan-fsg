def check_exists(user_data, update):
    # Checks if the user already exists in user_data
    # If the user exists return the user
    # If the user doesn't exists create user and return the user

    user_id = str(update["message"]["from"]["id"])
    chat_id = str(update["message"]["chat"]["id"])

    if user_id in user_data["users"]:
        return user_data["users"][user_id]
    elif not user_id in user_data["users"]:
        print("Yayy a new user is with us.")
        user_data["users"][user_id] = {"user_id": user_id, # Store it again to make processing easier.
                                       "chat_id": chat_id,
                                       "setup_mode": False,
                                       "is_bot": update["message"]["from"]["is_bot"],
                                       "language_code": update["message"]["from"]["language_code"],
                                       "classes": [],
                                      }

        return user_data["users"][user_id]

