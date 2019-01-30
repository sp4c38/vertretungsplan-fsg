#!/usr/bin/env python3

import datetime
import emoji
import os
import pathlib
import re
import string
import sys
import time


from collections import defaultdict
from typing import NamedTuple, Optional
from bs4 import BeautifulSoup

import teacher_list
import utils

represen_classes = []

def cleanup_string(non_ascii_string):
    """Clean up string to only contain printable characters"""
    printable = set(string.printable)
    return "".join([s for s in non_ascii_string if s in printable])


def get_date_from_page(page: bytes) -> Optional[datetime.date]:
    """Return a datetime object of the date string found in page.
    If no date is found return None.
    """
    soup = BeautifulSoup(page, features="html.parser")
    vp_table = find_vp_table(soup)
    if not vp_table:
        return None
    rows = vp_table.findChildren(['tr'])
    if not rows:
        print("Could not find any row in the table {my_table} while checking the date",
              file=sys.stderr)
        return None

    # Parse header
    row = rows.pop(0)
    paragraphs = row.findAll('p')
    if not paragraphs:
        return None
    head = paragraphs[0].text
    date_match = re.search(r'.*\b(?P<day>\d{1,2})[. ]+(?P<month>\d{1,2})[. ]+(?P<year>\d{2,4})',
                           head[-12:])
    if not date_match:
        return None
    date_match = {k: int(v) for k, v in date_match.groupdict().items()}

    # The above dict comprehension means the following:
    # new_date_match = {}
    # for k, v in date_match.groupdict().items():
    #     new_date_match[k] = int(v)
    # date_match = new_date_match

    if date_match['year'] < 2000:
        # Add the current century
        date_match['year'] = date_match['year'] + 2000

    return datetime.date(**date_match)


def parse_row(row=None, fh=None, get_vp_classes=False):
    global represen_classes

    data = row.findAll('p')

    lesson_number = " ".join(data[0].strings)
    klasse = " ".join(data[1].strings)
    would_have_hour = " ".join(data[2].strings)
    replacement = " ".join(data[3].strings)
    instead_of_lesson = " ".join(data[4].strings)

    # Only gets classes (school classes) which have representation
    if get_vp_classes == True:
        if klasse == "\xa0":
            return None
        else:
            if "\n" in klasse:
                klasse = klasse.replace("\n", "")
            return klasse

    if lesson_number == '\xa0':
        pass
    else:
        if "\n" in lesson_number:
            lesson_number = lesson_number.replace("\n", "")
        fh.write("\n")
        data = (lesson_number + ":")
        is_replacement = any(
            [e and e != '\xa0' for e in [klasse, replacement,
                                         would_have_hour, instead_of_lesson]])
        if is_replacement:
            fh.write(data)
            fh.write("\n")
        else:
            fh.write("Keine Vertretung: " + lesson_number + "\n")
    if klasse == '\xa0':
        pass
    else:
        if "\n" in klasse:
            klasse = klasse.replace("\n", "")
        fh.write(klasse)
        fh.write(' | ')
    if would_have_hour == '\xa0':
        pass
    else:
        if "\n" in would_have_hour:
            would_have_hour = would_have_hour.replace("\n", "")
        fh.write(would_have_hour)
        fh.write(' | ')

    if replacement == '\xa0':
        pass
    else:
        if "\n" in replacement:
            replacement = replacement.replace("\n", "")
        fh.write(replacement)
        if instead_of_lesson == '\xa0':
            fh.write("\n")

    if instead_of_lesson == '\xa0':
        pass
    else:
        if "\n" in instead_of_lesson:
            instead_of_lesson = instead_of_lesson.replace("\n", "")
        
        fh.write(" | statt -> ")
        fh.write(instead_of_lesson)
        fh.write("\n")


def parse_footer_row(row=None, fh=None):
    paragraphs = row.findAll('p')
    footer_data = paragraphs[0]
    footer_data = footer_data.string.replace('\n', '')
    fh.write('\n')
    fh.write(footer_data)
    fh.write('\n')
    
    return footer_data


def find_vp_table(soup_page=None):
    """Return the Vertretungsplan table"""
    # soup_page is the full html page embeded in soup
    tables = soup_page.findChildren('table', attrs={'class': ['MsoNormalTable', 'tr']})
    
    if not tables:
        print(
            "Could not find the MsoNormalTable table in the HTML document.\n")
        sys.exit(1)

    # Just want to have first table, if there are >1 table it will not be the
    # one which will be converted
    vp_table = tables[0]

    return vp_table


def sort_class_names(unsorted):
    """Return a list of the unsorted class names."""

    classes = []
    for class_name in represen_classes:

        level = re.search('\d+', class_name)
        if not level:
            continue
        level = int(level.group())

        letter = re.search(r'[a-d]+', class_name)
        if letter:
            letter = letter.group()
        else:
            letter = ""

        classes.append((level, letter))
    
    return ["{}{}".format(e[0], e[1]) for e in sorted(classes)]


def parse_header(rows=None, fh=None):
    global represen_classes

    if rows is None:
        print("Err: no rows found.")

    if fh is None:
        print("Err: fh not found.")
    # Parse header
    row = rows.pop(0)
    paragraphs = row.findAll('p')

    header_date = paragraphs[0].find('span')
    header_date = header_date.string.replace('\n', '')
    
    days_list = {
        'montag': 'Mo',
        'dienstag': 'Di',
        'mittwoch': 'Mi',
        'donnerstag': 'Do',
        'freitag': 'Fr',
    }

    for day in days_list:
        if day in header_date.lower():
            start_char = header_date.lower().find(day)
            header_date = "".join(
                [
                    header_date[:start_char],
                    days_list.get(day),
                    header_date[start_char + len(day):],
                ]
            )
        else:
            pass

    header_date = (header_date + emoji.emojize(" :grinning_face:", use_aliases=True))
    header_classes = paragraphs[1].find('span')
    header_classes = header_classes.string

    header_teacher = paragraphs[2].find('span')
    header_teacher = " ".join(
        str(i).replace('\n', '').replace('<i> </i>', '').replace('\xa0', '')
        for i in header_teacher.contents
    )
    for teacher in teacher_list.teacher_list:
        if teacher in header_teacher.lower():
            start_char = header_teacher.lower().find(teacher)
            header_teacher = "".join(
                [
                    header_teacher[:start_char],
                    teacher_list.teacher_list.get(teacher),
                    header_teacher[start_char + len(teacher):],
                ]
            )
    else:
        pass

    for row in rows:
        cells = row.findChildren(['td', 'p'])

        if len(row) == 11:
            klasse = parse_row(row=row, fh=fh, get_vp_classes=True)
            if klasse == None:
                pass
            else:
                if klasse.lower() == "klasse":
                    pass  
                else:
                    represen_classes += [klasse]
        elif len(row) == 3:
            pass

    # Removes all classes which are >1 times in represen_classes
    represen_classes = set(represen_classes)
    # Converts represen_classes to list
    represen_classes = list(represen_classes)
    
    if represen_classes:
        represen_classes = sort_class_names(represen_classes)
        represen_classes = ("\nVertretung für: " + ", ".join(represen_classes))


    fh.write(header_date + "\n")
    fh.write(header_classes + "\n")
    fh.write(header_teacher + "\n")
    if represen_classes:
        fh.write(represen_classes + "\n")
    fh.write("\n-> Klasse | Fach | Vertretung durch: (Fach) | statt\n")

def convert(rows=None, fh=None):
    # removes Klasse; Fach; Vertretung durch: (Fach); statt
    row = rows.pop(0)

    for row in rows:

        cells = row.findChildren(['td', 'p'])

        if len(row) == 11:
            parse_row(row=row, fh=fh)
        elif len(row) == 3:
            parse_footer_row(row=row, fh=fh)
        time.sleep(0.01)

def find_table(latest_file=None):
    
    if latest_file is None:
        print("no latets_file found, please run check_update.py")
        sys.exit()

    with open(latest_file) as fp:
        fp = fp.read()
        soup = BeautifulSoup(fp, features="html.parser")

    my_table = find_vp_table(soup)

    rows = my_table.findChildren(['tr'])
    if not rows:
        print("Could not find any row in the table {my_table}", file=sys.stderr)
        sys.exit(1)
    return rows

def find_raw_html_file(raw_file_path=None):

    cache_file_path = utils.get_cache_file_path()

    pathlib.Path(os.path.dirname(cache_file_path)).mkdir(parents=True, exist_ok=True)
    
    return cache_file_path

def main(file=None):
    global represen_classes
    latest_file = utils.get_latest_file(print_result=False) 
    if not latest_file:
        print("Didn't find latest file.")

    if file:
        cache_file_path = find_raw_html_file(raw_file_path=file)
    else:
        cache_file_path = find_raw_html_file(latest_file)
        
    fh = open(cache_file_path, 'w')
    rows = find_table(latest_file)
    
    parse_header(rows=rows, fh=fh)
    
    convert(rows=rows, fh=fh)
    # Closes fh file from editing process
    fh.close()

if __name__ == '__main__':
    main()
