#!/usr/bin/env python3

"""
Pull the Vertretungsplan from the Web and compare it to
the last stored version.
"""

import arrow
import datetime
import hashlib
import os
import re

from bs4 import BeautifulSoup

from modules.convert_prg import convert_rows
from modules.utils import get_date_from_page

def compare(stored_vp, current_vp):
    """
        First checks if the date from the recent vp is more back than from the stored vp. If so the
        recent vp is older than the stored vp, so no new one is found (nothing updated). False is returned.

        Uses sha256 algo to create a hash for the stored vertretungsplan and for the
        recent vertretungsplan, than compares them

        Returns True if the files diff and False if they are the same
    """

    # Uses CEST timezone (Central European Summer Time)

    cest = arrow.utcnow().to("CEST")
    today = arrow.get(datetime.date(cest.year, cest.month, cest.day)) # Will only contain year, month and day. Not hour, minute, seconds,...
                                                                      # So will be today at midnight

    if stored_vp:
        crt_vp_date_text = convert_rows.get_rows(file=current_vp)[0].findAll("p")[0].text
        srd_vp_date_text = convert_rows.get_rows(file=stored_vp)[0].findAll("p")[0].text

        try:
            crt_vp_date = get_date_from_page(crt_vp_date_text)
            srd_vp_date = get_date_from_page(srd_vp_date_text)
        except:
            return True

        if not (crt_vp_date >= srd_vp_date and crt_vp_date > today):
            print(f"Website-time {crt_vp_date}, stored-file-time: {srd_vp_date}, "\
                  f"but today is {today}.")
            return False

        crt_vp_hash = hashlib.sha256(current_vp.encode("UTF-8")).hexdigest()
        srd_vp_hash = hashlib.sha256(stored_vp.encode("UTF-8")).hexdigest()
        # Check if a new version was found or not
        if crt_vp_hash == srd_vp_hash:
            return False
        else:
            return True

    else:
        # If there is no stored_vp than only check if crt_vp_date is later than today at midnight
        crt_vp_date_text = convert_rows.get_rows(file=crt_vp)[0].findAll("p")[0].text
        try:
            crt_vp_date = get_date_from_page(crt_vp_date_text)
        except:
            return True

        if crt_vp_date > today:
            return True
        else:
            return False
