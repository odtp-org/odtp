
import logging
import shutil
import os
import odtp.helpers.settings as config

log = logging.getLogger(__name__)

def create_folders(relative_paths, odtp_path = config.ODTP_PATH, exist_ok=False):
    for relative_path in relative_paths:
        full_path = os.path.join(odtp_path, relative_path)

        os.makedirs(full_path, exist_ok=exist_ok)

        log.debug(f"Folder created: {full_path}")


def delete_folders(relative_paths, odtp_path = config.ODTP_PATH):
    for relative_path in relative_paths:
        full_path = os.path.join(odtp_path, relative_path)

        shutil.rmtree(full_path)

        log.debug(f"Folder created: {full_path}")


def generate_user_path(user_doc):
    abs_user_path = os.path.join(config.ODTP_PATH, user_doc["displayName"])
    return 

def generate_digital_twin_path(user_doc, digital_twin_doc):
    user_name = user_doc["displayName"]
    dt_name = digital_twin_doc["name"]
    dt_path = os.path.join(user_name, dt_name)
    abs_dt_path = os.path.join(config.ODTP_PATH, dt_path)
    return abs_dt_path

def generate_execution_path(user_doc, digital_twin_doc, execution_doc):
    execution_name = execution_doc["title"]
    dt_path = generate_digital_twin_path(user_doc, digital_twin_doc)
    execution_path = os.path.join(dt_path, execution_name)
    abs_execution_path = os.path.join(config.ODTP_PATH, execution_path)
    return abs_execution_path