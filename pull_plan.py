#!/usr/bin/env python3
""" Short script to pull the Vertretungsplan from the Internet.
"""

import configparser
import os
import pathlib
import sys

from datetime import datetime

import arrow
import requests

import utils


def get_weekday():
    today = arrow.utcnow()
    
    weekdays = {
        1: "Dienstag",
        2: "Mittwoch",
        3: "Donnerstag",
        4: "Freitag",
        5: "Montag",
        6: "Montag",
        7: "Montag"}

    return weekdays.get(today.isoweekday())


def get_raw_page(url, user, password):
    raw = requests.get(url, auth=(user, password))
    return raw

def get_page():
    url = "https://www.sachsen.schule/~gym-grossroehrsdorf/docs/vt/{}.htm".format
    url = url(get_weekday())
    user, password = get_creds()

    try: 
        raw_page = get_raw_page(url, user, password)
    except requests.exceptions.RequestException as err:
        print("Connection error: ", err)
        sys.exit(1)

    return raw_page


def safe_page(page):
    backup_path = utils.get_raw_html_file_path()
    pathlib.Path(os.path.dirname(backup_path)).mkdir(parents=True, exist_ok=True)
    with open(backup_path, "w") as text:
        text.write(str(page.text))
    print(f"Wrote raw html to: {backup_path}")


def get_creds():
    credentials = configparser.ConfigParser()
    config_path = os.path.expanduser('~/.config/vertretungsplan/creds.ini')
    credentials.read(config_path)
    return credentials.get('creds', 'user'), credentials.get('creds', 'password')


def main():
    page = get_page()

    if not page:
        print("Could not fetch Vertretungsplan with created url.")
        sys.exit(1)

    safe_page(page)


if __name__ == '__main__':
    main()
    
