"""Generic code for Vertretungsplan
"""

import arrow
import configparser
import datetime
import os
import re
import sys

from modules.convert_prg import convert_rows

def get_level_letter(string):
    # Uses re to get the level and the letter from a given string
    regex = re.findall("(?P<level>1[0-2]|[1-9])[^a-z]*(?P<letter>[a-z]*)", string)

    return regex

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
    backup_file_path = os.path.join(backup_dir_path, f"{time.format('DD-MM-YYYY_HH:mm')}.html") # Directory and file path

    recent_info_path = settings["recent_info"]
    config = configparser.ConfigParser()
    config.read(recent_info_path)
    config["recent_stored"]["recent_stored_vertretungsplan"] = backup_file_path

    print("Saving backup to ->", backup_file_path)

    os.makedirs(backup_dir_path, exist_ok=True)
    with open(backup_file_path, "w") as backup_file:
        backup_file.write(to_save)

    with open(recent_info_path, "w") as info_file:
        config.write(info_file)
    
    return

def remove_spaces(string):
    # The teacher_text looks mostly like this: Fehlende Lehrer  :  ST;LE; STF // too many 
    # of those spaces. This trys to remove them:
    start_char = string.lower().find(':')
    while string[start_char-1] == ' ':
        string = "".join([
                string[:start_char-1],
                string[start_char:]
            ])
        start_char = string.lower().find(':')
    
    start_char = string.lower().find(':')
    try:
        while string[start_char+2] == ' ':
            string[start_char+2]
            string = "".join([
                    string[:start_char+2],
                    string[start_char+3:]
                ])
            start_char = string.lower().find(':')
    except:
        pass

    return string

def get_validate_classes(message):
    # Get the different classes of the message and validate them
    # Returns the successful validated classes and the unsuccessful validated classes as a dictionary

    # Allowed types of sending classes in setup mode:
    # - 06d (to 6d), 006d, 0006d... or 010d (to 10d), 0010d
    # - 6d
    # - 6abcd or 6abcdd is translated to 6abcd (no duplicated letters)
    # - 6 is translated to 6a,6b,6c,6d
    # - 6amdcpdbq is translated to 6adcb

    splited_msg = message.split(",")
    validation_classes = {"successful": [], "unsuccessful": []}
    
    for msg in splited_msg:
        if msg:
            regex = get_level_letter(msg)
    
            if not regex:
                validation_classes["unsuccessful"].append(msg)
            else:
                for match in regex:
                    level = match[0]
                    letters = list(set(match[1])) # Sort out duplicated letters and put all in a list
    
                    if level and len(letters) == 1:
                        if letters[0] in ["a", "b", "c", "d"]:
                            joined_class = "".join([level, letters[0]])
                            validation_classes["successful"].append(joined_class)
                        else:
                            validation_classes["unsuccessful"].append(msg)
                    elif level and len(letters) > 1:
                        for l in letters:
                            if l in ["a", "b", "c", "d"]:
                                joined_class = "".join([level, l])
                                validation_classes["successful"].append(joined_class)
                            else:
                                joined_class = "".join([level, l])
                                validation_classes["unsuccessful"].append(joined_class)
                    elif level and not letters:
                        for l in ["a", "b", "c", "d"]:
                            joined_class = "".join([level, l])
                            validation_classes["successful"].append(joined_class)
                    elif not level:
                        validation_classes["unsuccessful"].append(msg)

    return validation_classes
