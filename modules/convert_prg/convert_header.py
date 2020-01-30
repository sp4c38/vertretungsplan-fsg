#!/usr/bin/python3

import emoji
import sys
import re

from modules import utils

from modules.convert_prg import convert_rows

def check_if_empty(check_strg=None):
    """
    We need a special method for checking, if specific things are empty. For example if 
    there are no classes, which are missing or if there are no teachers, which are missing.
    """
    seperator = check_strg.lower().find(':')
    second_part = check_strg[seperator+1:].replace('\xa0', '').replace('\n', '').replace(' ', '')

    if second_part:
        return False
    elif not second_part:
        return True

def sort_class_names(represen_classes=None):
    # Return a list of sorted class names
    duplicated_classes = [] # This list includes classes, but they could occur multiple times.
    
    for class_name in represen_classes:
        level = re.search('\d+', class_name) # The level of the school class a.e.: 2,4,7,10,12, re.search returns None if nothing is found and _sre.SRE_Match when a level is found

        if not level:
            continue

        level = int(level.group())
        letter_list = re.findall(r'[a-d]', class_name)

        if not letter_list:
            letter_list = ''

        if len(letter_list) > 1:
            for character in letter_list:
                duplicated_classes.append((level, character))
        else:
            duplicated_classes.append((level, "".join(letter_list)))

    duplicated_classes_together = ["{}{}".format(e[0], e[1]) for e in sorted(duplicated_classes)] # Sorts classes and stiches the level and letter together, some classes could still occure multiple times
    classes = [] # This list only includes classes, which don't occur more than one time

    for i in duplicated_classes_together:
        if not i in classes:
            classes.append(i)

    return classes

def parse_header(rows, wclasses):
    header_strg = ""

    header_row = rows[0].findAll("p")
    date_row = header_row[0]
    date_text = date_row.text.replace('\n', '')
        
    date = utils.get_date_from_page(date_text)

    day_relation = {
        1: "Montag",
        2: "Dienstag",
        3: "Mittwoch",
        4: "Donnerstag",
        5: "Freitag",
        6: "Samstag",
        7: "Sonntag",
    }

    header_date = f"Vertretungsplan für: {day_relation[int(date.format('d'))]}, "\
                  f"{date.day}.{date.month}.{date.year} {emoji.emojize(':exploding_head:', use_aliases=True )}"

    classes_text = header_row[1].find('span').text.replace("\n", "").replace("\xa0", "")
    
    # The classes_text could look like this: Fehlende Klassen  :  5b // too many 
    # of those spaces. This trys to remove them.
    classes_text = utils.remove_spaces(classes_text)

    classes_text_empty = check_if_empty(classes_text)
    if classes_text_empty:
        header_classes = None
    elif not classes_text_empty:
        header_classes = classes_text.replace("\n", "")


    teachers_text = header_row[2].find('span')
    teachers_replace = " ".join(str(i).replace('\n', '').replace('<i> </i>', '').replace('\xa0', '').replace('<i></i>', '')
                        for i in teachers_text.contents)

    # The teacher_text looks mostly like this: Fehlende Lehrer  :  ST;LE; STF // too many 
    # of those spaces. This trys to remove them.
    teachers_replace = utils.remove_spaces(teachers_replace)

    teachers_replace_empty = check_if_empty(teachers_replace)
    if teachers_replace_empty:
        header_teachers = None
    elif not teachers_replace_empty:
        header_teachers = teachers_replace

    represen_classes_unvalidated = [] # classes not validated
    represen_classes = [] # classes validated
    if "all" in wclasses:
        for row in rows:
            if len(row) == 11:
                school_class = convert_rows.parse_body_row(row=row, get_vertretungs_classes=True)
    
                if school_class:
                    represen_classes_unvalidated.append(school_class)
        
        for x in represen_classes_unvalidated:
            y = utils.get_validate_classes(x) # Validate classes
            for z in y["successful"]:
                represen_classes.append(z)

        if represen_classes:
            represen_classes = sort_class_names(represen_classes)
            represen_classes = f"Vertretung für: {', '.join(represen_classes)}"

    if header_date:
        header_strg += header_date + '\n'
    if header_classes:
        header_strg += header_classes + '\n'
    if header_teachers:
        header_strg += header_teachers + '\n'
    if represen_classes:
        header_strg += represen_classes + '\n'
    

    header_strg += "\nKlasse | Fach | Vertretung durch: (Fach) | statt\n"

    return header_strg