#!/usr/bin/env python3
""" Short script to pull the Vertretungsplan from the Internet.
"""

import arrow
import configparser
import os
import pathlib
import requests
import sys

import utils

def download_page(url, settings):
    # Get the vertretungsplan website config as configparser.ConfigParser object
    vp_conf = configparser.ConfigParser()
    vp_conf.read(settings["configuration_path"]["vp_website_cfg"])

    # download the page (authenticate with username and password from vp_conf)

    return requests.get(url=url, auth=(vp_conf["creds"]["user"], vp_conf["creds"]["password"])).text


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

def get_recent(settings):
    # Gets the vertretungsplan page from the internet

    search_wkd = get_weekday() # The weekday for which the program shall look for a vertretungsplan

    url = f"https://www.sachsen.schule/~gym-grossroehrsdorf/docs/vt/{search_wkd}.htm"
    page = download_page(url=url, settings=settings)
    print(f"Downloaded page from {url}")
    return page