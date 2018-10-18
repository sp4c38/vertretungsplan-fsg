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

import convert
import utils
import pull_plan


user = getpass.getuser()

def compare(latest_file=None):
    """ Creates a hash of the latest Vertretungsplan and a hash 
    of the newest Vertretungsplan (from the web)
    """

    # Pulls newest created file
    old_page = open(latest_file).read().encode('utf-8')

    # Pulls current page from the web and replaces '\r\n' with '\n'
    current_page = pull_plan.get_page()
    current_page = current_page.text.replace('\r\n', '\n').encode('utf-8')

    # Creates hash of current page and old page to compare if something changed
    old_hash = hashlib.sha256(old_page).hexdigest()
    new_hash = hashlib.sha256(current_page).hexdigest()
    print("Created hash: ", "\nold_hash= ", old_hash, "\nnew_hash= ", new_hash)
    
    # Checks if something changed between old_page and current_page
    if new_hash == old_hash:
        print("No new Vertretungsplan version found.")
        convert.main()
        sys.exit(0)
        return False
    else:
        print("New Vertretungsplan version found!")
        pull_plan.main()
        convert.main()
        return True

def check_requirements():
    backup_path = utils.get_raw_html_file_path()
    pathlib.Path(os.path.dirname(backup_path)).mkdir(parents=True,
     exist_ok=True)
    
    cache_file_path = utils.get_cache_file_path()
    pathlib.Path(os.path.dirname(cache_file_path)).mkdir(parents=True,
     exist_ok=True)

    if not os.path.isfile('creds.ini'):
        sys.stderr.write("E: Could not find creds.ini.\n")
        sys.exit(1)


def main():
    
    check_requirements()
    latest_file = utils.get_latest_file()
    compare(latest_file)
    

if __name__ == '__main__':
    main()
