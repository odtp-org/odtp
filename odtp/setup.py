"""
The goal of this script is to generate and initial mockup data for the instances.
"""
from odtp.db import MongoManager
from odtp.storage import s3Manager

import logging
import odtp.helpers.settings as config


class s3Database:
    def __init__(self):
        s3Server = config.ODTP_S3_SERVER
        bucketName = config.ODTP_BUCKET_NAME
        accessKey = config.ODTP_ACCESS_KEY
        secretKey = config.ODTP_SECRET_KEY
        storageManager = s3Manager(s3Server, bucketName, accessKey, secretKey)
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
