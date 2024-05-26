from odtp.storage import s3Manager

import logging
import shutil



class s3Database:
    def __init__(self):
        storageManager = s3Manager()
        self.storageManager = storageManager
        logging.info("Connected to: %s", storageManager)

    def create_folders(self, structure):
        self.storageManager.createFolderStructure(structure)
        logging.info("Folder structure generated")

    def close(self):
        self.storageManager.close()

    def deleteAll(self):
        self.storageManager.deleteAll()
        self.storageManager.close()
        logging.info("S3 deleted and client closed")

    def download(self, item):
        pass


class folderStructure:
    def __init__(self):
        self.odtp_path = config.ODTP_PATH

    def create_folders(self):
        components_folder = os.path.join(self.odtp_path, 'components')
        users_folder = os.path.join(self.odtp_path, 'users')
        
        os.makedirs(components_folder, exist_ok=True)
        os.makedirs(users_folder, exist_ok=True)
        
        logging.info("Folders created: %s, %s", components_folder, users_folder)

    def deleted_folders(self):
        components_folder = os.path.join(self.odtp_path, 'components')
        users_folder = os.path.join(self.odtp_path, 'users')
        
        shutil.rmtree(components_folder)
        shutil.rmtree(users_folder)
        
        logging.info("Folders deleted: %s, %s", components_folder, users_folder)
