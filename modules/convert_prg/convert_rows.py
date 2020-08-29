import emoji
import re
import sys

from bs4 import BeautifulSoup

from modules import utils
from modules.convert_prg import convert_header

def get_rows(file):
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

def check_contains(class_list, wclasses):
    if "all" in wclasses:
        return True

    for m in class_list:
        if m in wclasses:
            return True
        else:
            continue

    return False

def parse_body_row(row = None, replacement_lessons = None, get_vertretungs_classes = False, wclasses = None):
    line_together = {"text": "", "is_lesson_number": False, "is_vertretungs_data": False}

    data = row.findAll('p')
    lesson_number = data[0].text.replace("\xa0", "").replace("\n", "")
    school_class = data[1].text.replace("\xa0", "").replace("\n", "")
    would_have_hour = data[2].text.replace("\xa0", "").replace("\n", "")
    replacement = data[3].text.replace("\xa0", "").replace("\n", "")
    instead_of_lesson = data[4].text.replace("\xa0", "").replace("\n", "")

    if get_vertretungs_classes == True:
        # If get_vertretungs_classes is True this function will only return the school classes which have vertreung
        # it could be that duplicates occur. This is used by convert_header
        return school_class

    if lesson_number in replacement_lessons["reversed_no_vertretung"]:
        return line_together
    elif lesson_number in replacement_lessons and replacement_lessons[lesson_number] == False:
        return {"text": f"\n{emoji.emojize(':no_entry: Keine Vertretung für die ', use_aliases=True)} {lesson_number}.", "is_lesson_number": False, "is_vertretungs_data": True}

    if instead_of_lesson:
        instead_of_lesson = f"statt -> {instead_of_lesson}"

    data_sorted = [y for y in [school_class, would_have_hour, replacement, instead_of_lesson] if y] # Sort out items which are empty | with lesson_number

    if lesson_number and any(data_sorted):
        if school_class:
            class_list = utils.get_validate_classes(school_class)["successful"]
            contains = check_contains(class_list, wclasses)

            if contains:
                line_together["text"] = f"{lesson_number}:\n{' | '.join(data_sorted)}"
                line_together["is_lesson_number"] = True
                line_together["is_vertretungs_data"] = True
            else:
                line_together["text"] = f"{lesson_number}:"
                line_together["is_lesson_number"] = True
        else:
            line_together["text"] = f"{lesson_number}:\n{' | '.join(data_sorted)}"

    elif not lesson_number and any(data_sorted):
        if school_class:
            class_list = utils.get_validate_classes(school_class)["successful"]
            contains = check_contains(class_list, wclasses)

            if contains:
                line_together["text"] = f"{' | '.join(data_sorted)}"
                line_together["is_vertretungs_data"] = True
        else:
            line_together["text"] = f"{' | '.join(data_sorted)}"
            line_together["is_vertretungs_data"] = True

    elif lesson_number and not any(data_sorted) and replacement_lessons[lesson_number] == True:
        line_together["text"] = f"{lesson_number}:"
        line_together["is_lesson_number"] = True

    return line_together


def parse_footer_row(row):

    footer_paragraphs = row.findAll('p')
    footer_text = footer_paragraphs[0].text.replace("\n", "").replace("\xa0", "")

    footer_text = utils.remove_spaces(footer_text)

    footer_empty = convert_header.check_if_empty(check_strg = footer_text)

    if footer_empty:
        return None

    elif not footer_empty:
        return footer_text


def check_replacement_lessons(rows, wclasses):
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

            if school_class:
                class_list = utils.get_validate_classes(school_class)["successful"]
            else:
                class_list = []

            if lesson_number:
                current_lesson = lesson_number
                repl_lessons[current_lesson] = False

            if "all" in wclasses and any([class_list, would_have_hour, replacement, instead_of_lesson]):
                repl_lessons[current_lesson] = True
            else:
                if class_list and any([would_have_hour, replacement, instead_of_lesson]):
                    for wanted_class in wclasses:
                        if wanted_class in class_list:
                            repl_lessons[current_lesson] = True
                            continue

                elif not class_list and any([would_have_hour, replacement, instead_of_lesson]):
                    repl_lessons[current_lesson] = True

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

def convert_body(rows, wclasses):
    lines = []
    replacement_for_lessons = check_replacement_lessons(rows = rows, wclasses = wclasses)
    replacement_for_lessons = remove_no_representation(vertretungs_lessons = replacement_for_lessons)

    for row in rows:
        if len(row) == 11:
            body_line = parse_body_row(row = row, replacement_lessons = replacement_for_lessons, wclasses = wclasses)
            if body_line["text"]:
                if not (body_line["is_lesson_number"] and body_line["is_vertretungs_data"]):
                    lines.append(body_line)

                if body_line["is_lesson_number"] and body_line["is_vertretungs_data"]:
                    # Will be triggered if there is a lesson number in the table and on the same line also
                    # some vertretungs data

                    splited_lines = body_line["text"].split("\n")

                    if len(splited_lines) == 2:
                        lines.append({"text": splited_lines[0], "is_lesson_number": True, "is_vertretungs_data": False})
                        lines.append({"text": splited_lines[1], "is_lesson_number": False, "is_vertretungs_data": True})


        elif len(row) == 3:
            footer_row = parse_footer_row(row=row)
            if footer_row:
                lines.append({"text": footer_row, "is_lesson_number": False, "is_vertretungs_data": False})

    return lines
