# Merges the header and the body to certain formats

def to_text(header, body, date, to_recive, settings):
    # header ... converted header
    # body ... converted body
    # date ... date from page as beautiful string
    # to_recive ... the classes which the user will recive
    merge_result = ""

    if not body:
        if "all" in to_recive:
            merge_result = open(settings["messages"]["no_vertretung"]).readlines()[0].replace("\n", "")
            merge_result = merge_result.format(date)
        else:
            merge_result = open(settings["messages"]["no_vertretung"]).readlines()[1].replace("\n", "")
            merge_result = merge_result.format(date)

    elif header and body:
        merge_result += header
        for line in body:
            if line["is_lesson_number"] and not line["is_vertretungs_data"]:
                merge_result += "\n"
                merge_result += line["text"]

            elif line["is_vertretungs_data"] and not line["is_lesson_number"]:
                merge_result += f"  {line['text']}"

            elif not line["is_vertretungs_data"] and not line["is_lesson_number"]:
                # Must be footer row
                merge_result += "\n"
                merge_result += line["text"]

            merge_result += "\n"

    return merge_result
