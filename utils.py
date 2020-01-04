"""Generic code for Vertretungsplan
"""

import arrow
import configparser
import datetime
import os
import re
import sys

from convert_prg import convert_rows

def get_stored(settings):
    # Gets the most recent stored vertretungsplan file and return the path to it, if none is found None is returned
    
    config = configparser.ConfigParser()
    config.read(settings["recent_info"])

    if config["recent_stored"]["recent_stored_vertretungsplan"]:
        try:
            return open(config["recent_stored"]["recent_stored_vertretungsplan"]).read()
        except:
            return None
    else:
        return None

def get_date_from_page(text=None):
    """Return a datetime object of the date string found in page.
    If no date is found return None.
    """

    date_match = re.search(r'.*\b(?P<day>\d{1,2})[. ]+(?P<month>\d{1,2})[. ]+(?P<year>\d{2,4})',
                           text[-12:])

    if not date_match:
        return None

    date_match = {k: int(v) for k, v in date_match.groupdict().items()}

    # The above dict comprehension means the following:
    # new_date_match = {}
    # for k, v in date_match.groupdict().items():
    #     new_date_match[k] = int(v)
    # date_match = new_date_match

    if date_match['year'] < 2000:
        # Add the current century
        date_match['year'] += 2000

    return  arrow.get(datetime.date(**date_match))

def backup_vertretungsplan(settings, to_save):
    # This function backs up the vertretungsplan. This is used to recognise that a vertretungsplan was already
    # send a previouse time and doesn't have to be send again, 
    # but it is also usefull for analyzing the data later (to do some stats).
    
    time = arrow.utcnow().to("MET")
    backup_dir_path = os.path.join(settings["backup_path"], str(time.year), time.format("MM")) # Only directory path
    backup_file_path = os.path.join(backup_dir_path, time.format("DD-MM-YYYY_HH:mm.txt")) # Directory and file path

    recent_info_path = settings["recent_info"]
    config = configparser.ConfigParser()
    config.read(recent_info_path)
    config["recent_stored"]["recent_stored_vertretungsplan"] = backup_file_path

    print("Saving backup to -> ", backup_file_path)

    os.makedirs(backup_dir_path, exist_ok=True)
    with open(backup_file_path, "w") as backup_file:
        backup_file.write(to_save)

    with open(recent_info_path, "w") as info_file:
        config.write(info_file)

    return