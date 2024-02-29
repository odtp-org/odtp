import re

FIELD_INPUT_DELIMTER_PATTERN = '[,|+|\s|;]+'


def parse_ports(input_field):
    if input_field:
        input_field_cleaned = re.split(FIELD_INPUT_DELIMTER_PATTERN, input_field)
    else:
        input_field_cleaned = None
    return input_field_cleaned
