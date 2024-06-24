
import logging
import shutil
import os
import odtp.helpers.settings as config

def create_main_folders(odtp_path = config.ODTP_PATH):
    components_folder = os.path.join(odtp_path, 'components')
    users_folder = os.path.join(odtp_path, 'users')

    os.makedirs(components_folder, exist_ok=True)
    os.makedirs(users_folder, exist_ok=True)

    logging.info("Folders created: %s, %s", components_folder, users_folder)

def deleted_main_folders(odtp_path = config.ODTP_PATH):
    components_folder = os.path.join(odtp_path, 'components')
    users_folder = os.path.join(odtp_path, 'users')

    shutil.rmtree(components_folder)
    shutil.rmtree(users_folder)

    logging.info("Folders deleted: %s, %s", components_folder, users_folder)