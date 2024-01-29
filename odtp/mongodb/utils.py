import json


def output_as_json(db_output):
    return json.dumps(db_output, indent=2, default=str)


def print_output_as_json(db_output):
    print(output_as_json(db_output))


def get_list_from_cursor(cursor):
    document_list = []
    for document in cursor:
        document_list.append(document)
    return document_list
