#!/usr/bin/env python3
""" Short script to pull the Vertretungsplan from the Internet.
"""

import arrow
import configparser
import os
import pathlib
import requests
import sys

from modules import utils

def download_page(url, config):
    # Download the page by authenticating to the server.
    page_raw = requests.get(url=url, auth=(config["user"], config["password"]))
    # The downloaded page includes \r\n newline characters as the table on the site was probably generated
    # with some Windows tool like Excel. For standard newline characters on Unix systems, following converts
    # them to the proper \n newline symbol.
    page_bad_newline = page_raw.text
    page = page_bad_newline.replace("\r\n", "\n")
    return page

def get_weekday():
    # Gets todays weekday (timezone used: MET)

    weekdays = { # Mostly search for the vertretungsplan for next day
        1: "Dienstag", # On Monday search for the vertretungsplan for Tuesday
        2: "Mittwoch", # On Tuesday search for the vertretungsplan for Wednesday
        3: "Donnerstag", # On Wednesday search for the vertretungsplan for Thursday
        4: "Freitag", # On Thursday search for the vertretungsplan for Friday
        5: "Montag", # On Friday search for the vertretungsplan for Monday, because there is no new one at the weekends
        6: "Montag", # On Saturday search for the vertretungsplan for Monday, because there is no new one at the weekends
        7: "Montag"} # On Sunday search for the vertretungsplan for Monday

    today = arrow.utcnow().to("MET")
    return weekdays.get(today.isoweekday())

def get_recent(config):
    # Gets the vertretungsplan page from the internet

    search_wkd = get_weekday() # Weekday the script shall look for a vertretungsplan

    url = config["website"].format(search_wkd)
    page = download_page(url=url, config=config)
    print(f"Downloaded page from {url}")
    return page
