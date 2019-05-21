import sys
import re

class body():
    def convert_rows(rows=None, fout=None, get_substitute_classes=False):
        
        if not rows:
            print("No rows to convert.")
            sys.exit(1)

        if not fout:
            print("No file for output set.")
            sys.exit(1)


        def parse_row(row=None, get_vp_classes=False, fout=None):

            if not fout:
                print("No file for output set.")
                sys.exit(1)

            if not row:
                print("No row to convert provided.")
                sys.exit(0)

            data = row.findAll('p')

            lesson_number = " ".join(data[0].strings)
            klasse = " ".join(data[1].strings)
            would_have_hour = " ".join(data[2].strings)
            replacement = " ".join(data[3].strings)
            instead_of_lesson = " ".join(data[4].strings)
            
            

            if get_vp_classes == True:
                if klasse == '\xa0':
                    return    
                else:
                    if '\n' in klasse:
                        klasse = klasse.replace('\n', '')
                    return klasse

            
            if lesson_number == '\xa0':
                pass
            else:
                if '\n' in lesson_number: 
                    lesson_number.replace('\n', '')
                fout.write("\n")
                data = (lesson_number + ':')
                is_replacement = any(
                    [e and e != '\xa0' for e in [klasse, would_have_hour,
                                                replacement,instead_of_lesson]])

                if is_replacement:
                    fout.write(data)
                    fout.write('\n')
                    pass
                else:
                    fout.write("Keine Vertretung für die " + lesson_number + '.' + '\n')
            if klasse == '\xa0':
                pass
            else:
                if '\n' in klasse:
                    klasse.replace('\n', '')
                level = re.search('\d+', klasse)
                letter = re.findall(r'[a-d]', klasse)
                klasse = str(level.group() + (''.join(letter)))
                fout.write(klasse + ' | ')
            if would_have_hour == '\xa0':
                pass
            else:
                if '\n' in would_have_hour:
                    would_have_hour.replace('\n', '')
                fout.write(would_have_hour + ' | ')
            
            if replacement == '\xa0':
                pass
            else:
                if '\n' in replacement:
                    replacement.replace('\n', '')
                fout.write(replacement)
                if instead_of_lesson == '\xa0':
                    fout.write('\n')
            
            if instead_of_lesson == '\xa0':
                pass
            else:
                if '\n' in instead_of_lesson:
                    instead_of_lesson.replace('\n', '')
                fout.write(' | statt ->' + instead_of_lesson + '\n')

            return



        def parse_footer_row(row=None, fout=None):
            if not row:
                print("No footer row to convert.")
                sys.exit(1)
            if not fout:
                print("No output file provided.")
                sys.exit(1)

            data = row.findAll('p')
            data = data[0]
            data = data.string.replace('\xa0', '').replace('\n', '')
            fout.write('\n' + data)



        if get_substitute_classes == True:
            klasse = parse_row(row=rows, fout=fout, get_vp_classes=True)
            return klasse
        else:   
            rows.pop(0)
        
            for row in rows:
               # cells = row.findChildren(['td', 'p'])

                if len(row) == 11:
                    parse_row(row=row, fout=fout)
                elif len(row) == 3:
                    parse_footer_row(row=row, fout=fout)


