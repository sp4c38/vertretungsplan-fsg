import arrow

import check_updated
import poll_plan
import telegram
import utils

from settings import settings

from convert_prg import convert_header, convert_rows


def main():
    print(f"Session started {arrow.utcnow().format()}.\n")

    stored_vp = utils.get_stored(settings=settings)
    recent_vp = poll_plan.get_recent(settings=settings)

    updated = check_updated.compare(srd_vp=stored_vp, rct_vp=recent_vp)

    if updated:
        print("Updated.")
        if not settings["debug"]:
            utils.backup_vertretungsplan(settings=settings, to_save=recent_vp) # Save the vertretungsplan to backups
        # Find table and rows in that table
        rows = convert_rows.get_rows(file=recent_vp)
        # Convert header and create header variable
        print("Converting...")
        header = convert_header.parse_header(rows=rows)
        body = convert_rows.convert_rows(rows=rows)
        output = header + body

        output_file = open(settings["output_path"], "w") # This actually isn't needed by the program,
        output_file.write(output) # but is nice to have,
        output_file.close() # this code can be commented or deleted if wished

        if not settings["debug"]: # Only send message if debug mode is disabled
            telegram.send_message(settings=settings, message=output)
    else:
        print("Not updated.")

    print(f"\nSession ended {arrow.utcnow().format()}.")

if __name__ == '__main__':
    if settings["debug"]: # info: settings["debug"]: True
        main()
    else: # info: settings["debug"]: False
        try:
            main()
        except:
            print("The program was interrupted.")
    