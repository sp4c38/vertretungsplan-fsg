#!/usr/bin/python3

import emoji
import sys
import re

import utils

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

def header(rows=None):  
    header_strg = ""

    header_row = rows.pop(0).findAll("p")
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
                  f"{date.day}.{date.month}.{date.year} {emoji.emojize(':exploding_head:', use_aliases=True)}"

    
    classes_text = header_row[1].find('span').text.replace("\n", "").replace("\xa0", "")
 
    classes_text_empty = check_if_empty(classes_text)

    # The classes_text could look like this: Fehlende Klassen  :  5b // too many 
    # of those spaces. This trys to eliminate them:

    start_char = classes_text.lower().find(':')

    while classes_text[start_char-1] == ' ':
        classes_text = "".join([
                classes_text[:start_char-1],
                classes_text[start_char:]
            ])
        start_char = classes_text.lower().find(':')

    start_char = classes_text.lower().find(':')
    
    try:
        classes_text[start_char+2] == ' '

        while classes_text[start_char+2] == ' ':
            classes_text = "".join([
                    classes_text[:start_char+2],
                    classes_text[start_char+3:]
                ])
            try:
                classes_text[start_char+2] == ' '
            except:
                break
    except:
        pass

    if classes_text_empty:
        header_classes = None
    elif not classes_text_empty:
        header_classes = classes_text.replace("\n", "")


    teachers_text = header_row[2].find('span')
    teachers_replace = " ".join(str(i).replace('\n', '').replace('<i> </i>', '').replace('\xa0', '').replace('<i></i>', '')
                        for i in teachers_text.contents)

    # The teacher_text looks mostly like this: Fehlende Lehrer  :  ST;LE; STF // too many 
    # of those spaces. This trys to eliminate them:
    start_char = teachers_replace.lower().find(':')
    while teachers_replace[start_char-1] == ' ':
        teachers_replace = "".join([
                teachers_replace[:start_char-1],
                teachers_replace[start_char:]
            ])
        start_char = teachers_replace.lower().find(':')

    start_char = teachers_replace.lower().find(':')
    
    try:
        classes_text[start_char+2] == ' '

        while teachers_replace[start_char+2] == ' ':
            teachers_replace = "".join([
                    teachers_replace[:start_char+2],
                    teachers_replace[start_char+3:]
                ])
            try:
                teachers_replace[start_char+2] == ' '
            except:
                break
    except:
        pass

    teachers_replace_empty = check_if_empty(teachers_replace)
    if teachers_replace_empty:
        header_teachers = None
    elif not teachers_replace_empty:
        header_teachers = teachers_replace


    # represen_classes = []
    # for row in rows:
    #     if len(row) == 11:
    #         klasse = body.convert_rows(rows=row, fout=fout, get_vertretungs_classes=True)
            
    #         if klasse == None:
    #             pass
    #         else:
    #             if klasse.lower() == 'klasse':
    #                 pass
    #             else:
    #                 represen_classes.append(klasse)
   
    
    # if represen_classes:
    #     l = -1
    #     for c in represen_classes:
    #         l += 1
    #         for s in awkward_symbols:
    #             represen_classes[l] = represen_classes[l].replace(s, '')
    #     represen_classes = sort_class_names(represen_classes)
    #     represen_classes = set(represen_classes);represen_classes = list(sorted(represen_classes))
    #     represen_classes = sort_class_names(represen_classes)
    #     represen_classes = ("Vertretung für: " + ", ".join(represen_classes))
    if header_date:
        header_strg += header_date + '\n'
    if header_classes:
        header_strg += header_classes + '\n'
    if header_teachers:
        header_strg += header_teachers + '\n'
    # if represen_classes:
        # fout.write(represen_classes + '\n')
    
    # Pop to remove Klasse | Fach ... row from rows. We are not taking the content from this row,
    # just add a custom string (next +=)
    rows.pop(0)
    header_strg += "\nKlasse | Fach | Vertretung durch: (Fach) | statt\n"

    return header_strg

    def sort_class_names(represen_classes=None):
        """Return a list of the unsorted class names."""
        
        if represen_classes is None:
            print("No classes to sort given.")
            return None
        classes = []
        
        for class_name in represen_classes:
            level = re.search('\d+', class_name)
            if not level:
                continue
            level = int(level.group())
            letter = re.findall(r'[a-d]', class_name)

            # len() gets the number of items in an list e.g. l=['hi', 'bye', 'ok']
            # than len(l) is 3
            if len(letter) > 1:
                for i in letter:
                    classes.append((level, i))
            else:
                classes.append((level, "".join(letter)))
            
            if not letter:
                letter = ''
            # append only takes one argument, level and letter have to be linked together
            # that is why there are two brackets: output: e.g. [(10, 'a'), ('6', 'a'), ('9', 'd')]
        return ["{}{}".format(e[0], e[1]) for e in sorted(classes)]


