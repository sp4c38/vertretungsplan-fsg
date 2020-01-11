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

def compare(srd_vp, rct_vp):
    """ 
        First checks if the date from the recent vp is more back than from the stored vp. If so the
        recent vp is older than the stored vp, so no new one is found (nothing updated). False is returned.

        Uses sha256 to create a hash (hashlib) for the stored vertretungsplan and for the
        recent vertretungsplan, than compares them

        Returns True if the files differentiates and False if they are the same

        ! srd_vp: stored vp
        ! rct_vp: recent vp
    """ 

    # Uses *MET* timezone (german: *MEZ* timezone)

    # Do it like that to dismis hour, minute and millisecond attributes (they will be 0)
    today = arrow.get(datetime.date(arrow.utcnow().year, arrow.utcnow().month, arrow.utcnow().day))
    
    if srd_vp:

        rct_vp_date_text = convert_rows.get_rows(file=rct_vp)[0].findAll("p")[0].text
        srd_vp_date_text = convert_rows.get_rows(file=srd_vp)[0].findAll("p")[0].text
        try:
            rct_vp_date = get_date_from_page(rct_vp_date_text)
            srd_vp_date = get_date_from_page(srd_vp_date_text)
        except:
            return True
            
        if rct_vp_date >= srd_vp_date and rct_vp_date > today:
            pass
        else:
            print(f"Website-time {rct_vp_date}, stored-file-time: {srd_vp_date}, "\
                  f"but today is {today}.")
            return False

        rct_vp_hash = hashlib.sha256(rct_vp.encode("UTF-8")).hexdigest()
        srd_vp_hash = hashlib.sha256(srd_vp.encode("UTF-8")).hexdigest()
        # Check if a new version was found or not
        if rct_vp_hash == srd_vp_hash:
            return False
        else:
            return True

    else:
        # If there is no srd_vp than only check if rct_vp_date is more further than today
        rct_vp_date_text = convert_rows.get_rows(file=rct_vp)[0].findAll("p")[0].text
        try:
            rct_vp_date = get_date_from_page(rct_vp_date_text)
        except:
            return True

        if rct_vp_date > today:
            return True
        else:
            return False
