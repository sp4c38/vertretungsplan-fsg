# This program will check if the vertretungsplan has changed (based on backups)
# if so it will send it to user-specific chats and user-group chats

import arrow
import configparser
import json
import requests
import traceback

from modules import check_updated
from modules import  poll_plan
from modules import telegram
from modules import utils

from settings import settings

from modules.convert_prg import convert_header, convert_rows


def get_prerequisites(settings):
    # vertretungsplan config file
    vp_config_file = configparser.ConfigParser()
    vp_config_file.read(settings["configuration_path"]["vp_website"])

    vp_config = vp_config_file["creds"]

    # telegram config file
    telegram_config_file = configparser.ConfigParser()
    telegram_config_file.read(settings["configuration_path"]["telegram"])

    telegram_config = telegram_config_file["telegram_cfg"]
    telegram_api = telegram_config_file["telegram_api_urls"]

    # Data of registered users
    user_data = json.load(open(settings["user_file"]))

    return vp_config, telegram_config, telegram_api, user_data


def main():
    vp_config, telegram_config, telegram_api, user_data = get_prerequisites(settings)

    # Get all recipients (single users and telegram groups)
    # For single users assign the chat id as key to the classes the user will get vertretung
    # Add all groups to the recipients["all"] list because they get vertretung for all classes
    recipients = {"all": []}
    for user in user_data["users"]:
        recipients[user_data["users"][user]["chat_id"]] = user_data["users"][user]["classes"]

    for group in telegram_config["group_chat_ids"].split(","):
        recipients["all"].append(group)

    stored_vp = utils.get_stored(settings=settings) # Last local stored vertretungplan
    current_vp = poll_plan.get_recent(config=vp_config) # Current vertretungsplan from the website of the FSG

    updated = check_updated.compare(stored_vp=stored_vp, current_vp=current_vp)
    updated = True
    if updated:
        print("Updated")

        utils.backup_vertretungsplan(settings=settings, to_save=current_vp) # Save the vertretungsplan to backups
        # Find table and rows in that table

        print("Converting...")
        rows = convert_rows.get_rows(file=current_vp)

        # Pop to remove Klasse | Fach ... row from rows
        # This is added as hard-coded data later
        rows.pop(1)

        for rcpt in recipients: # Convert for each recipient
            # wclasses: wanted classes
            if rcpt == "all":
                header, date = convert_header.parse_header(rows = rows, wclasses = ["all"]) # Get back the header and the date from the page
                body = convert_rows.convert_body_footer(rows = rows, wclasses = ["all"]) # Convert the body and the footer

                # Merge the header and the body
                # If the body is empty a message will be inserted for the body which tells the user that there is not vertretung
                output = convert_rows.merge_header_body(header, body, date, ["all"], settings)

                print(f"Sending message to {recipients[rcpt]}.")
                telegram.send_message(config = telegram_config, telegram_api = telegram_api,
                                      chat_id_list = recipients[rcpt], message = output)
            else:
                header, date = convert_header.parse_header(rows = rows, wclasses = recipients[rcpt]) # Get back the header and the date from the page
                body = convert_rows.convert_body_footer(rows = rows, wclasses = recipients[rcpt]) # Convert the body and the footer

                # Merge the header and the body
                # If the body is empty a message will be inserted for the body which tells the user that there is not vertretung
                output = convert_rows.merge_header_body(header, body, date, recipients[rcpt], settings)

                print(f"Sending message to {rcpt}.")
                telegram.send_message(config = telegram_config, telegram_api = telegram_api,
                                      chat_id_list = [rcpt], message = output)
    else:
        print("Not updated")


if __name__ == '__main__':
    try:
        print(f"Session started {arrow.utcnow().format()}.\n")
        main()
        print(f"\nSession ended {arrow.utcnow().format()}.")

    except requests.exceptions.ConnectionError:
        print("Problems connecting to the internet.")
        print(f"\nSession ended {arrow.utcnow().format()}.")

    except Exception as exception:
        traceback.print_exc()
        print(f"\nSession ended {arrow.utcnow().format()}.")
