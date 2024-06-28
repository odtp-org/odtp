
import logging
import shutil
import os
import odtp.helpers.settings as config

def create_main_folders(odtp_path = config.ODTP_PATH):
    users_folder = os.path.join(odtp_path, 'users')

    os.makedirs(users_folder, exist_ok=True)

    logging.info("Folders created: %s, %s", users_folder)

def delete_main_folders(odtp_path = config.ODTP_PATH):
    users_folder = os.path.join(odtp_path, 'users')

    shutil.rmtree(users_folder)

    logging.info("Folders deleted: %s, %s", users_folder)