# File, which contains the settings for the vertretungsplan program for the fsg.
# Feel free to modify this file for your personal needs.


import os

BASE_DIR = os.path.expanduser(os.path.join("~", "Documents", "vertretungsplan"))

settings = {
    "backup_path": os.path.join(BASE_DIR, "backups"),
    "recent_info": os.path.join(BASE_DIR, "backups", "recent.info"), # The file, which stored the most recent stored vertretungsplan, must be compatible with configparser (python build-in library)
    "output_path": os.path.join(BASE_DIR, "converted", "converted.txt"), # Output file for the converted content
    
    "configuration_path": { # The configuration files must be formated to be compatible, with configparser (pythons build-in library)
        "vp_website_cfg": os.path.join(BASE_DIR, "config", "vp_website.ini"),
        "telgram_cfg": os.path.join(BASE_DIR, "config", "telegram.ini"),
    },
    
    "updates_file": os.path.join(BASE_DIR, "data","updates_data.json"),
    "user_file": os.path.join(BASE_DIR, "data", "user_data.json"),
    "messages": { # Pre-wrote messages
        # Used by vertretungsplan
        "no_vertretung": os.path.join(BASE_DIR, "messages", "vertretungsplan", "no_vertretung.txt"),

        # Used by single_vertretungsplan
        "main_keyboardmarkup": os.path.join(BASE_DIR, "messages", "main_keyboard_markup.txt"),

        "start": os.path.join(BASE_DIR, "messages", "start", "start.txt"),

        "setup": os.path.join(BASE_DIR, "messages", "setup", "setup.txt"),
        "setup_mode_deactivated": os.path.join(BASE_DIR, "messages", "setup", "setup_mode_deactivated.txt"),
        "validation_successful": os.path.join(BASE_DIR, "messages", "setup", "validation_successful.txt"),
        "validation_unsuccessful": os.path.join(BASE_DIR, "messages", "setup", "validation_unsuccessful.txt"),
            
        "myinfo": os.path.join(BASE_DIR, "messages", "myinfo", "myinfo.txt"),

        "delete": os.path.join(BASE_DIR, "messages", "delete", "delete.txt"),
        "delete_keyboard_markup": os.path.join(BASE_DIR, "messages", "delete", "delete_keyboard_markup.txt"),
        "delete_mode_successful": os.path.join(BASE_DIR, "messages", "delete", "delete_mode_successful.txt"),
        "delete_mode_unsuccessful": os.path.join(BASE_DIR, "messages", "delete", "delete_mode_unsuccessful.txt"),
        "no_classes_to_delete": os.path.join(BASE_DIR, "messages", "delete", "no_classes_to_delete.txt"),

        "help": os.path.join(BASE_DIR, "messages", "help", "help.txt"),
    },

    "debug": False, # A extra setting which helps debugging the program

}
