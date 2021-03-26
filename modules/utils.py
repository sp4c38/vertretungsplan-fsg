# Generic code for the vertretungsplan program

import arrow
import configparser
import datetime
import os
import re
import sys

from modules.convert_prg import convert_rows

def get_level_letter(string):
    # Use regex to get the class level and the class letter and return it as a tuple
    # For example 5d will be converted to [("5", "d")]

    #                                                                      This part is optional (only if range like 5-12 level)
    #                                                                      |-----------------------------------------------------|
    regex = re.findall("(?P<level>1[0-2]|[1-9])[^-a-z]*(?P<letter>[a-z])*-*(?P<levelTwo>1[0-2]|[1-9])*[^a-z]*(?P<letterTwo>[a-z])*", string)
    all_classes_have_vertretung = False

    return_level_letter = []

    for match in regex:
        # Normally will only have one iteration
        if len(match) == 4:
            # import IPython;IPython.embed();import sys;sys.exit()
            if not match[2] and not match[3]:
                return_level_letter.append((match[0], match[1]))
            elif match[0] and match[2]:
                if not match[1] and not match[3]:
                    if (int(match[0]) - int(match[2])) == -7:
                        # Exact range 5-12
                        # All classes have vertretung
                        all_classes_have_vertretung = True

                    for level in range(int(match[0]), int(match[2]) + 1, 1): # regex makes sure that this doesn't result into errors
                        for letter in ["a", "b", "c", "d"]:
                            return_level_letter.append((str(level), letter))

    return all_classes_have_vertretung, return_level_letter

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

    return arrow.get(datetime.date(**date_match))

def backup_vertretungsplan(settings, to_save):
    # This function backs up the vertretungsplan. This is used to recognise that a vertretungsplan was already
    # send a previouse time and doesn't have to be send again,
    # but it is also useful for analyzing the data later.

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
    # Returns the successful validated classes and the unsuccessful validated classes

    # Example validations:
    # - 6d, 06d, 006d, 0006d converted to 6d
    # - 6abcd or 6abcdd is translated to 6abcd (no duplicated letters)
    # - 6 is translated to 6a,6b,6c,6d
    # - 6amdcpdbq is translated to 6adcb

    # Returned is a dictionary with {"successful": [], "unsuccessful": []}
    # Whereby successful includes all successfully validated single classes
    # So 6abcdpd would be {"successful": [6a,6b,6c,6d], "unsuccessful": [6p]}

    splited_msg = message.split(",")
    validation_classes = {"are_all": False, "successful": [], "unsuccessful": []} # are_all is set to True if all classes of the whole school are in "successful"

    are_all = False
    made_mistake = False # Set to True if any classes are added to unsuccessful
                         # Needed to set are_all in validation_classes to True if made_mistake stays False

    for msg in splited_msg:
        if msg:
            are_all, level_letter = get_level_letter(msg)

            if not level_letter:
                validation_classes["unsuccessful"].append(msg)
            else:
                for match in level_letter:
                    level = match[0]

                    if not level in ["5", "6", "7", "8", "9", "10", "11", "12"]: # Don't convert level to integer, could lead to errors
                        # Only classes from 5th grade on exist
                        validation_classes["unsuccessful"].append(msg)
                        continue

                    letters = list(set(match[1])) # Sort out duplicated class letters with set

                    if level and letters:
                        for letter in letters:
                            if letter in ["a", "b", "c", "d"]:
                                joined_class = "".join([level, letter])
                                validation_classes["successful"].append(joined_class)
                            else:
                                joined_class = "".join([level, letter])
                                validation_classes["unsuccessful"].append(joined_class)
                    elif level and not letters:
                        for letter in ["a", "b", "c", "d"]:
                            joined_class = "".join([level, letter])
                            validation_classes["successful"].append(joined_class)
                    elif not level:
                        validation_classes["unsuccessful"].append(msg)
                        continue

    if are_all == True and made_mistake == False:
        validation_classes["are_all"] = True

    # Remove duplicates out of successful and unsuccessful list
    if validation_classes["successful"]:
        validation_classes["successful"] = list(set(validation_classes["successful"]))

    if validation_classes["unsuccessful"]:
        validation_classes["unsuccessful"] = list(set(validation_classes["unsuccessful"]))

    return validation_classes
