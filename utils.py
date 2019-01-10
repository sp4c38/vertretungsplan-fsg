"""Generic code for Vertretungsplan
"""

import configparser
import os
import pathlib
import glob
import sys

from datetime import datetime

import pull_plan

def get_telegram_config_data():
    telegram_config = configparser.ConfigParser()
    telegram_config_path = os.path.expanduser('~/.config/vertretungsplan/telegram.ini')
    telegram_config.read(telegram_config_path)
    return telegram_config


def get_config():
    config = configparser.ConfigParser()
    config_path = os.path.expanduser('~/.config/vertretungsplan/config.ini')
    config.read(config_path)
    return config

def get_cache_file_path():
    config = get_config()

    cache_path = os.path.join(config.get('storage', 'base_dir'),
                              config.get('storage', 'cache_dir'),
                              'converted.txt')
    cache_path = os.path.expanduser(cache_path)
    
    return cache_path

def get_raw_html_file_path(date=None):
    """Return the path of the raw html file name for a
    given day

    :param date: The date as a datetime object
    """
    config = get_config()

    if date is None:
        date = datetime.now()

    backup_path = os.path.join(config.get('storage', 'base_dir'),
                               config.get('storage', 'backup_dir'))

    backup_path = os.path.expanduser(backup_path)
    
    raw_html_path = os.path.join(backup_path, str(date.year), str(date.month),
                                 (f"{date.year}-{date.month}-{date.day}"
                                  f"_{date.hour}:{date.minute}.html"))
    
    return raw_html_path

def get_latest_file(print_result=True):

    todays_path = os.path.dirname(get_raw_html_file_path())

    list_of_files = glob.glob(os.path.join(todays_path, '*'))
    
    # Handels if there are no files in todays_path
    if not list_of_files:
        print(f"No files found in {todays_path}")
        return

    latest_file = sorted(list_of_files, key=os.path.getctime, reverse=True)[0]

    if print_result == True:
        print("Latest created file: ", latest_file)
    else:
        pass
    
    return latest_file