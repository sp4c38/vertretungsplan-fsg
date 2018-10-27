#!/usr/bin/env python3

import datetime
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


class StandInData(NamedTuple):
    lesson_number: str
    klasse: str
    would_have_hour: str
    instead_of: str
    insted_of_statt: str


def cleanup_string(non_ascii_string):
    """Clean up string to only contain printable characters"""
    printable = set(string.printable)
    return "".join([s for s in non_ascii_string if s in printable])


def get_date_from_page(page: bytes) -> Optional[datetime.date]:
    """Return a datetime object of the date string found in page"""
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
        return False
    head = paragraphs[0].text
    date_match = re.match(r'.*(?P<day>\d{2})\.(?P<month>\d{1,2})\.(?P<year>\d{2,4})$', head[-10:])
    if not date_match:
        return False
    date_match = {k: int(v) for k, v in date_match.groupdict().items()}
    if date_match['year'] < 2000:
        # Add the current century
        date_match['year'] = date_match['year'] + 2000

    return datetime.date(**date_match)


def parse_row(row=None, fh=None):
    lesson_number = ""
    klasse = ""
    instead_of = ""

    data = row.findAll('p')

    lesson_number = data[0]
    klasse = data[1]
    would_have_hour = data[2]
    instead_of = data[3]
    insted_of_statt = data[4]

    items_dict = {
        lesson_number: lesson_number.string,
        klasse: klasse.string,
        would_have_hour: would_have_hour.string,
        instead_of: instead_of.string,
        insted_of_statt: insted_of_statt.string,
    }

    if lesson_number.string == '\xa0':
        pass
    else:
        data = items_dict.get(lesson_number)
        fh.write("\n")
        fh.write(data)
        fh.write(":\n")
    if klasse.string == '\xa0':
        pass
    else:
        data = items_dict.get(klasse)
        fh.write(data)
        fh.write(' | ')
    if would_have_hour.string == '\xa0':
        pass
    else:
        data = items_dict.get(would_have_hour)
        fh.write(data)
        fh.write(' | ')
    if instead_of.string == '\xa0':
        pass
    else:
        data = items_dict.get(instead_of)
        fh.write(data)
        fh.write(" ")
    if instead_of.string == '\xa0':
        pass
    else:
        data = items_dict.get(insted_of_statt)
        fh.write(data)
        fh.write("\n")

    return StandInData(
        lesson_number.string,
        klasse.string,
        would_have_hour.string,
        instead_of.string,
        insted_of_statt.string,
    )


def parse_footer_row(row=None, fh=None):
    paragraphs = row.findAll('p')
    footer_data = paragraphs[0]
    footer_data = footer_data.string.replace('\n', '')

    fh.write('\n')
    fh.write(footer_data)
    fh.write('\n')


def find_vp_table(soup_page):
    """Return the Vertretungsplan table"""
    tables = soup_page.findChildren('table', attrs={'class': ['MsoNormalTable', 'tr']})

    if not tables:
        return False

    vp_table = tables[0]
    return vp_table


def main(file=None):
    print("Converting...")

    raw_file_path = file
    if file is None:
        latest_file = utils.get_latest_file(print_result=False)
        raw_file_path = latest_file

    cache_file_path = utils.get_cache_file_path()

    pathlib.Path(os.path.dirname(cache_file_path)).mkdir(parents=True, exist_ok=True)

    fh = open(cache_file_path, 'w')

    with open(raw_file_path) as fp:
        fp = fp.read()
        soup = BeautifulSoup(fp, features="html.parser")

    my_table = find_vp_table(soup)
    if not my_table:
        print(
            "Could not find the MsoNormalTable table in the HTML document.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    rows = my_table.findChildren(['tr'])
    if not rows:
        print("Could not find any row in the table {my_table}", file=sys.stderr)
        sys.exit(1)

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

    fh.write(header_date)
    fh.write("\n")
    fh.write(header_classes)
    fh.write("\n")
    fh.write(header_teacher)
    fh.write("\n")
    fh.write("\nKlasse | Fach | Vertretung durch: (Fach) | statt")
    fh.write("\n")

    stand_in_data = defaultdict(list)

    # removes Klasse; Fach; Vertretung durch: (Fach); statt
    row = rows.pop(0)
    i = 0
    row_count = 0

    for row in rows:
        row_count += 1

    row_count = 100.5 / row_count

    for row in rows:

        i += row_count
        if not os.environ.get('UNATTENDED', False):
            sys.stdout.write("\r{}%".format(int(i)))
            sys.stdout.flush()

        cells = row.findChildren(['td', 'p'])

        if len(row) == 11:

            row_stand_in_data = parse_row(row=row, fh=fh)

            lesson_number = row_stand_in_data.lesson_number
            klasse = row_stand_in_data.klasse
            would_have_hour = row_stand_in_data.would_have_hour
            instead_of = row_stand_in_data.instead_of
            insted_of_statt = row_stand_in_data.insted_of_statt

            stand_in_data[lesson_number].append(row_stand_in_data)
        elif len(row) == 3:
            parse_footer_row(row=row, fh=fh)

        time.sleep(0.01)

    fh.close()


if __name__ == '__main__':
    main()
