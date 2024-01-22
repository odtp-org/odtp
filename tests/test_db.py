"""
test_db.py
~~~~~~~~~~~~~~~
This module contains unit tests for the connection and setting of the database 
using mongoDB
"""

import unittest
import logging
from odtp import db

from dotenv import dotenv_values

config = dotenv_values(".env")
import os

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

class DBTests(unittest.TestCase):
    """
    Test suite for dabate operation
    """

    def createCollections(self):
        """
        Test permission to create collections
        """
        db_odtp = self.dbManager.client["odtp"]
        db_odtp.create_collection("users")
        db_odtp.create_collection("components")
        db_odtp.create_collection("versions")
        db_odtp.create_collection("digitalTwins")
        db_odtp.create_collection("results")

    # Basic connection
    def setUp(self):
        """Set up logging for the tests."""
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        dbManager = db.MongoManager(config["MONGOURL"], "odtp")

        self.dbManager = dbManager


    def tearDown(self):
        # Connect to your database. Replace 'mydatabase' with your database name.
        db_odtp = self.dbManager.client["odtp"]

        # Get a list of all collections in the database
        collections = db_odtp.list_collection_names()

        # Drop each collection
        for collection in collections:
            db_odtp.drop_collection(collection)

        self.dbManager.client.close()

    def test_connection(self):
        """
        Test the connection to the database
        """

        self.logger.info(f'Connected to {self.dbManager.client}')
        self.assertEqual(self.dbManager.client.odtp.name, "odtp")

        self.createCollections()

    def test_add_user(self):
        """
        Test the creation of users
        """

        user_data = {
            "displayName": "Marta",
            "email": "marta@example.com",
            "github": "marta"
        }

        out = self.dbManager.add_user(user_data["displayName"],
                                user_data["email"],
                                user_data["github"])
        
        self.logger.info(out)


if __name__ == "__main__":
    unittest.main()