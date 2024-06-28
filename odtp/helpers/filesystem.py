
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

