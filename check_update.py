#!/usr/bin/env python3

"""
Pull the Vertretungsplan from the Web and compare it to
the last stored version.
"""

import os
import getpass
import hashlib
import datetime
import sys
import pathlib
import re

from typing import NamedTuple, Optional
from bs4 import BeautifulSoup
from convert import get_rows

import convert
import utils
import pull_plan
import vp_bot

user = getpass.getuser()

__version__ = '0.1'
__authors__ = ('Léon Becker <lb@space8.me>', 'Frank Becker <fb@alien8.de>')


def get_date_from_page(page: bytes) -> Optional[datetime.date]:
    """Return a datetime object of the date string found in page.
    If no date is found return None.
    """

    soup = BeautifulSoup(page, features="html.parser")
    
    rows = get_rows(file2conv=page)
    
    if not rows:
        print("Could not find any row in the table while checking the date",
              file=sys.stderr)
        return None

    # Parse header
    row = rows.pop(0)
    paragraphs = row.findAll('p')
    if not paragraphs:
        return None
    head = paragraphs[0].text
    date_match = re.search(r'.*\b(?P<day>\d{1,2})[. ]+(?P<month>\d{1,2})[. ]+(?P<year>\d{2,4})',
                           head[-12:])
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
        date_match['year'] = date_match['year'] + 2000

    return datetime.date(**date_match)

def compare(latest_file=None):
    """ Creates a hash of the latest Vertretungsplan and a hash
    of the newest Vertretungsplan (from the web)
    """
    # Pulls newest created file
    if latest_file:
        old_page = open(latest_file).read().encode("utf-8")

    # Pulls current page from the web and replaces '\r\n' with '\n'
    current_page = pull_plan.get_page()
    current_page = current_page.text.replace("\r\n", "\n").encode("utf-8")

    # Parse the header to find the date of the page. It might be that the date
    # is older than the file name makes us think.
    page_date = get_date_from_page(current_page)

    if not page_date:
        print(f"Did not find a date in the header of the HTML Vertretungsplan page.")

    today = datetime.date.today()

    # example: page_date = 20 today = 21, checks if 20 < 21, also works with 30.04 < 01.05 beacuse it is a datetime attribut
    if page_date < today:
        print(f"The date found in the header of the VP HTML page is: {page_date}. "
            f"But today is: {today}")
        return False

    # Creates hash of current page and old page to compare if something changed
    if latest_file:
        old_hash = hashlib.sha256(old_page).hexdigest()
    
    new_hash = hashlib.sha256(current_page).hexdigest()

    # Checks if something changed between old_page and current_page
    if latest_file:
        if new_hash == old_hash:
            print("-> no new Vertretungsplan version found.")
            convert.main()
            return False
        else:
            print("-> new Vertretungsplan version found!")
            pull_plan.main()
            convert.main()
            vp_bot.main()
            return True
    else:
        print("-> pulling newest vertretungsplan version.")
        pull_plan.main()
        convert.main()
        vp_bot.main()
        return True

def check_requirements():
    creds_path = os.path.expanduser('~/.config/vertretungsplan/creds.ini')
    config_path = os.path.expanduser('~/.config/vertretungsplan/config.ini')
    telegram_path = os.path.expanduser('~/.config/vertretungsplan/telegram.ini')

    if not os.path.isfile(creds_path):
        sys.stderr.write(
            f"No creds.ini file in: {creds_path}\n"
        )
        sys.exit(1)

    if not os.path.isfile(config_path):
        sys.stderr.write(
            f"No config.ini file in: {config_path}\n"
        )
        sys.exit(1)
    if not os.path.isfile(telegram_path):
        sys.stderr.write(
            f"No telegram.ini file in: {telegram_path}\n"
        )
        sys.exit(1)

    backup_path = utils.get_raw_html_file_path()
    pathlib.Path(os.path.dirname(backup_path)).mkdir(parents=True, exist_ok=True)

    cache_file_path = utils.get_cache_file_path()
    pathlib.Path(os.path.dirname(cache_file_path)).mkdir(parents=True, exist_ok=True)


def main():
    date = datetime.datetime.now()
    print(
        "--- Session started: ", date, " ---"
    )  # example: --- Session started: 2018-10-21 11:00:01.875420  ---

    check_requirements()
    latest_file = utils.get_latest_file()
    compare(latest_file)

    date = datetime.datetime.now()
    print(
        "--- Session ended: ", date, " ---"
    )  # example: --- Session ended: 2018-10-21 11:00:01.875420 ---


if __name__ == "__main__":
    main()
