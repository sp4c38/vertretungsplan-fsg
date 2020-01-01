# File, which contains the settings for the vertretungsplan program for the fsg.
# Feel free to modify this file for your personal needs.


import os

BASE_DIR = os.path.expanduser(os.path.join("~", "Documents", "vertretungsplan"))

settings = {
    "backup_path": os.path.join(BASE_DIR, "backups"),
    "recent_info": os.path.join(BASE_DIR, "backups", "recent.info"), # The file, which stored the most recent stored vertretungsplan, must be compatible with configparser (python build-in library)
    "output_path": os.path.join(BASE_DIR, "converted", "converted.txt"),
    "configuration_path": { # The configuration files must be formated to be compatible, with configparser (python build-in library)
        "vp_website_cfg": os.path.join(BASE_DIR, "config", "vp_website.ini"),
        "telgram_cfg": os.path.join(BASE_DIR, "config", "telegram.ini"),
    },

}