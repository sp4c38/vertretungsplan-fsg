import emoji
import re
import sys

from bs4 import BeautifulSoup

from convert_prg import convert_header


def get_rows(file=None):
    beautiful_file = BeautifulSoup(file, features="html.parser")
    tables = beautiful_file.findChildren('table', attrs={'class': ['MsoNormalTable']})

    if not tables:
        print("Could not find the MsoNormalTable table in the document.")
        sys.exit(1)

    table = tables[0]
        
    rows = table.findChildren(['tr'])
    
    if not rows:
        print("Could not find any rows in the MsoNormalTable.")
        sys.exit(1)
    
    return rows

def parse_body_row(row=None, replacement_lessons=None, get_vertretungs_classes=False):
    row_strg = ""

    data = row.findAll('p')
    lesson_number = data[0].text.replace("\xa0", "").replace("\n", "")
    school_class = data[1].text.replace("\xa0", "").replace("\n", "")
    would_have_hour = data[2].text.replace("\xa0", "").replace("\n", "")
    replacement = data[3].text.replace("\xa0", "").replace("\n", "")
    instead_of_lesson = data[4].text.replace("\xa0", "").replace("\n", "")

    if get_vertretungs_classes == True:
        # If get_vertretungs_classes is True the programm will only return the school classes which have vertreung
        # it could be that duplicates occur. This is used by convert_header
        return school_class

    if lesson_number in replacement_lessons["reversed_no_vertretung"]:
        return ""
    elif lesson_number in replacement_lessons and replacement_lessons[lesson_number] == False:
        return f"\n{emoji.emojize(':cross_mark: Keine Vertretung für die ', use_aliases=True)} {lesson_number}.\n"

    if instead_of_lesson:
        instead_of_lesson = f"statt -> {instead_of_lesson}"

    data_list = [
        school_class,
        would_have_hour,
        replacement,
        instead_of_lesson,
    ]

    data_sorted = [y for y in data_list if y] # Sort out items which are empty ("", None,...)

    if lesson_number and any(data_list):
        data_together = f"\n{lesson_number}:\n {' | '.join(data_sorted)}\n"

    elif not lesson_number and any(data_list):
        data_together = f" {' | '.join(data_sorted)}\n"

    elif lesson_number and not any(data_list):
        data_together = f"\n{lesson_number}:\n"

    else:
        data_together = ""

    return data_together
    
    
def parse_footer_row(row=None):

    footer_paragraphs = row.findAll('p')
    footer_text = footer_paragraphs[0].text

    start_char = footer_text.lower().find(':')
    while footer_text[start_char-1] == ' ':
        footer_text = "".join([
                footer_text[:start_char-1],
                footer_text[start_char:]
            ])
        start_char = footer_text.lower().find(':')


    start_char = footer_text.lower().find(':')
    try:
        footer_text[start_char+2] == ' '

        while footer_text[start_char+2] == ' ':
            footer_text = "".join([
                    footer_text[:start_char+2],
                    footer_text[start_char+3:]
                ])
            try:
                footer_text[start_char+2] == ' '
            except:
                break
    except:
        pass

    footer_empty = convert_header.check_if_empty(check_strg=footer_text)

    if footer_empty:
        return None
    elif not footer_empty:
        return footer_text


def check_replacement_lessons(rows=None):
    # Return a dictionary, with all lesson
    # Each lesson has a value: True if there is any data in the colums between (a.e. 1.Std. until 2.Std.)
    #                          False if there isn't any data in the colums between (a.e. 2.Std. until 3.Std.)

    repl_lessons = {"reversed_no_vertretung": []}

    current_lesson = None
    for row in rows:
        if len(row) == 11:
            data = row.findAll("p")
            lesson_number = data[0].text.replace("\xa0", "").replace("\n", "")
            school_class = data[1].text.replace("\xa0", "").replace("\n", "")
            would_have_hour = data[2].text.replace("\xa0", "").replace("\n", "")
            replacement = data[3].text.replace("\xa0", "").replace("\n", "")
            instead_of_lesson = data[4].text.replace("\xa0", "").replace("\n", "")
            
            # print(lesson_number, school_class, would_have_hour, replacement, instead_of_lesson)

            if lesson_number:
                current_lesson = lesson_number
                repl_lessons[current_lesson] = False

            if any([school_class, would_have_hour, replacement, instead_of_lesson]):
                repl_lessons[current_lesson] = True

            reset = False

    return repl_lessons

def remove_no_representation(vertretungs_lessons):
    # The function looks from the reversed order on vertretungs_lessons. Now it sorts all
    # lessons which have no vertretung into vertretungs_lessons["reversed_no_vertretung"] until
    # it finds one which has vertretung. This is used that we don't display "Keine Vertretung fü...."
    # for lessons which have no following lessons with vertretung. Don't display them -> to keep an overview.


    for lesson in sorted(vertretungs_lessons, reverse=True): # Use sorted to iterate over list (dictionary) in reversed way
        if vertretungs_lessons[lesson] == False:
            vertretungs_lessons.pop(lesson)
            vertretungs_lessons["reversed_no_vertretung"].append(lesson)
        elif vertretungs_lessons[lesson] == True:
            break

    return vertretungs_lessons

def convert_rows(rows=None, get_vertretungs_classes=False):
    body_strg = ""

    replacement_for_lessons = check_replacement_lessons(rows=rows)
    replacement_for_lessons = remove_no_representation(vertretungs_lessons=replacement_for_lessons)

    for row in rows:
        if len(row) == 11:
            body_strg += parse_body_row(row=row, replacement_lessons=replacement_for_lessons)
        elif len(row) == 3:
            footer = parse_footer_row(row=row)

    if body_strg and footer:
        return body_strg + "\n" + footer
    elif body_strg:
        return body_strg