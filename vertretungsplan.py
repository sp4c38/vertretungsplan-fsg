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
    vp_config = configparser.ConfigParser()
    vp_config.read(settings["configuration_path"]["vp_website_cfg"])
    vp_config = vp_config["creds"]

    tele_config = configparser.ConfigParser()
    tele_config.read(settings["configuration_path"]["telgram_cfg"])
    tele_config_all = tele_config["telegram_cfg"]

    tele_config_uniformly = configparser.ConfigParser()
    tele_config_uniformly.read(settings["configuration_path"]["telgram_cfg"])
    tele_config_uniformly = tele_config_uniformly["uniformly"] # Configurations which are uniformly

    user_data = json.load(open(settings["user_file"]))

    return vp_config, tele_config_all, tele_config_uniformly, user_data


def main():
    vp_config, tele_config_all, tele_config_uniformly, user_data = get_prerequisites(settings)
    # Have chat_id-recipient point at the classes wanted / "all" are all classes | i.e.: 123 -> 8b,6c or 321 -> "all"
    recipients = {user_data["users"][x]["chat_id"]:user_data["users"][x]["classes"] for x in user_data["users"]}

    reciving_groups = [y for y in tele_config_all["group_chat_ids"].split(",") if y]
    for g in reciving_groups:
        recipients[g] = ["all"]

    stored_vp = utils.get_stored(settings=settings)
    recent_vp = poll_plan.get_recent(config=vp_config)

    updated = check_updated.compare(srd_vp=stored_vp, rct_vp=recent_vp)

    if updated:
        print("Updated.")
        if not settings["debug"]:
            utils.backup_vertretungsplan(settings=settings, to_save=recent_vp) # Save the vertretungsplan to backups
        # Find table and rows in that table
        print("Converting...")
        rows = convert_rows.get_rows(file=recent_vp)
        # Pop to remove Klasse | Fach ... row from rows, because we aren't needing this.
        rows.pop(1)

        for r in recipients: # Convert for each recipient
            # wclasses: wanted classes
            header, date = convert_header.parse_header(rows=rows, wclasses=recipients[r]) # Get back the header and the date from the page
            body = convert_rows.convert_body_footer(rows=rows, wclasses=recipients[r]) # Convert the body and the footer

            # Body or header could be empty / if body is empty a message will tell the user that there's no vertretung:
            output = convert_rows.check_header_body(header, body, date, recipients[r], settings)

            if not settings["debug"]: # Only send message if debug mode is disabled
                chat_id_list = [r]
                print(f"Sending message to {r}")
                telegram.send_message(config=tele_config_all, config_uniformly=tele_config_uniformly, \
                                      chat_id_list=chat_id_list, message=output)
    else:
        print("Not updated.")


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
