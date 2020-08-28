# File, which contains the settings for the vertretungsplan program for the fsg.
# Feel free to modify this file for your personal needs.


import os

BASE_DIR = os.path.expanduser(os.path.join("~", "Documents", "vertretungsplan"))

settings = {
    "backup_path": os.path.join(BASE_DIR, "backups"),
    "recent_info": os.path.join(BASE_DIR, "backups", "recent.info"), # Configparser file which stores the most recent stored vertretungsplan

    "configuration_path": { # Configparser configuration files for telegram (group id,...) and vertretungsplan setting
        "vp_website": os.path.join(BASE_DIR, "config", "vp_website.ini"),
        "telegram": os.path.join(BASE_DIR, "config", "telegram.ini"),
    },

    "updates_file": os.path.join(BASE_DIR, "data","updates_data.json"),
    "user_file": os.path.join(BASE_DIR, "data", "user_data.json"), # File containing data for registered users

    "messages": { # Pre-wrote messages
        "no_vertretung": os.path.join(BASE_DIR, "messages", "vertretungsplan", "no_vertretung.txt"),

        "main_keyboardmarkup": os.path.join(BASE_DIR, "messages", "main_keyboard_markup.txt"),

        "start": os.path.join(BASE_DIR, "messages", "start", "start.txt"),

        "setup": os.path.join(BASE_DIR, "messages", "setup", "setup.txt"),
        "setup_mode_finished": os.path.join(BASE_DIR, "messages", "setup", "setup_mode_finished.txt"),
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
}
