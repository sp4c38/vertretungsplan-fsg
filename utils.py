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
        return open(config["recent_stored"]["recent_stored_vertretungsplan"]).read()
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

