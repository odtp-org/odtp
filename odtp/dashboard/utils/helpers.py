import os
import re
ODTP_INPUT = "odtp-input"
ODTP_OUTPUT = "odtp-output"
ODTP_REPO = "repository"


def check_empty_output_folder(project_path):
    if not os.path.exists(project_path):
        return False
    elif not os.path.isdir(project_path):
        return False
    elif len(os.listdir(project_path)) !=0:
        return False
    return True


def check_output_folder(project_path):
    if not os.path.exists(project_path):
        return False
    elif not os.path.isdir(project_path):
        return False
    return True


def map_output_folder(project_path):
    project_content = {}
    output_path = os.path.join(project_path, ODTP_OUTPUT)
    input_path = os.path.join(project_path, ODTP_INPUT)
    if os.path.exists(output_path):
        project_content[ODTP_OUTPUT] = os.listdir(output_path)
    if os.path.exists(input_path):
        project_content[ODTP_INPUT] = os.listdir(input_path)
    print(project_content)
    return project_content


def check_docker_image_name(value):
    if not len(value) >= 4:
        return False
    if not re.match("^[a-z]+$", value):
        return False
    return True
