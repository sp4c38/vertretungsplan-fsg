#!/usr/bin/python3

from bs4 import BeautifulSoup
import pathlib
import os
import sys

from convert_prg.convert_header import header
from convert_prg.convert_rows import body

import utils

def get_rows(file2conv=None, no_dict=False):
    if not file2conv:
        print("No file provided to get rows.")
        sys.exit()

    beautiful_file = BeautifulSoup(file2conv, features="html.parser")
    tables = beautiful_file.findChildren('table', attrs={'class': ['MsoNormalTable', 'tr']})

    if not tables:
        print("Could not find the MsoNormalTable table in the document.")
        sys.exit(1)

    table = tables[0]
        
    rows = table.findChildren(['tr'])
    
    if not rows:
        print("Could not find any rows in the MsoNormalTable.")
        sys.exit(1)
    
    return rows

def get_cache_file_path():
    cache_file_path = utils.get_cache_file_path()
    pathlib.Path(os.path.dirname(cache_file_path)).mkdir(parents=True, exist_ok=True)
    return cache_file_path


def check_file_2_conv(file=None):
    if not file:
        file = utils.get_latest_file(print_result=False)
        if not file:
            print("No file found to convert.")
            sys.exit(1)
        else:
            return(file)
    else:
        check_if_exists = os.path.isfile(file)
        if check_if_exists is False:
            print("Given file doesn't exist.")
            sys.exit(1)
        else:
            return(file)


def main(file_2_convert=None):
    # ! conv = convert
    file_2_convert = check_file_2_conv(file=file_2_convert)
    print(f"Converting file: \'{file_2_convert}\'")    
    
    # Gets output file ((with config) (~/.config/vertretungsplan by default))
    # fcache = file cache
    output_file = get_cache_file_path()
    fout = open(output_file, 'w')
    print(f"Output file: \'{output_file}\'")
    # Opens file_2_convert 
    f2conv = open(file_2_convert, 'r')
    # Find table and rows
    rows = get_rows(f2conv)
    
    # Convert header
    header.convert_header(rows=rows, fout=fout)
    
    # Convert all other rows in table
    # removes Klasse; Fach; Vertretung durch: (Fach); statt

    body.convert_rows(rows=rows, fout=fout)

    f2conv.close()


if __name__ == '__main__':
    main()