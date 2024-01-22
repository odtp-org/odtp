"""
The goal of this script is to generate and initial mockup data for the instances.
"""
from odtp.mongodb.db import MongoManager
from odtp.mongodb.db import odtpDatabase
from .storage import s3Manager

import logging
import os
from dotenv import load_dotenv


class mongoDatabase(odtpDatabase):

    def create_collections(self):
        db_odtp = self.dbManager.db

        db_odtp.create_collection("users")
        db_odtp.create_collection("components")
        db_odtp.create_collection("versions")
        db_odtp.create_collection("digitalTwins")
        db_odtp.create_collection("results")

        logging.info("Collections created")

    def insert_mockup_data(self):
        dataEmulator = MockDataEmulator(self.dbManager)
        dataEmulator.emulate_data()

        logging.info("Mockup data generated and uploaded")

    def run_initial_setup(self):
        self.create_collections()
        self.insert_mockup_data()

        logging.info("Initial setup finished")

    def deleteAll(self):
        self.dbManager.deleteAll()
        self.dbManager.close()

        logging.info("DB deleted and client closed")

    def close(self):
        self.dbManager.close()

##################################################################################

class s3Database:
    def __init__(self):
        load_dotenv()
        s3Server = os.getenv("ODTP_S3_SERVER")
        bucketName = os.getenv("ODTP_BUCKET_NAME")
        accessKey = os.getenv("ODTP_ACCESS_KEY")
        secretKey = os.getenv("ODTP_SECRET_KEY")

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


##################################################################################
# Testing the DB with mockup data

from datetime import datetime, timedelta

from random import choice
from bson.objectid import ObjectId

class MockDataEmulator:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def emulate_data(self):
        # Emulating some users
        user_ids = [
            self.db_manager.add_user({
                "displayName": "John Doe",
                "email": "john@example.com",
                "github": "johnDoeRepo",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }),
            self.db_manager.add_user({
                "displayName": "Alice Smith",
                "email": "alice@example.com",
                "github": "aliceSmithRepo",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }),
            self.db_manager.add_user({
                "displayName": "Bob Johnson",
                "email": "bob@example.com",
                "github": "bobJohnsonRepo",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        ]

        # Emulating some components  

        for i in range(3):
            component_data = {
                "author": "author test",
                "componentName": f"Component_{i+1}",
                "status": "active",
                "title": f"Title for Component_{i+1}",
                "description": f"Description for Component_{i+1}",
                "tags": ["tag1", "tag2"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            component_id = self.db_manager.add_component(component_data)
            
            # Emulating 3 versions for some components
            for i in range(3):
                version_data = {
                    "version": f"v{i+1}.0",
                    "component_version": f"{i+1}.0.0",
                    "repoLink": "https://github.com/...",
                    "dockerHubLink": "https://hub.docker.com/...",
                    "parameters": {"a": "a", "b": "b"},
                    "title": "Title for Version v1.0",
                    "description": "Description for Version v1.0",
                    "tags": ["tag1", "tag2"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }

                version_id = self.db_manager.add_version(component_id, version_data)


        # Emulating a digital twin for a user
        digital_twins_data = {
            "userRef": choice(user_ids),
            "status": "active",
            "public": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "executions": []  
        }
        digital_twin_id = self.db_manager.add_digital_twin(choice(user_ids), digital_twins_data)

        execution_timestamp = datetime.now().isoformat()
        step_timestamp = (datetime.now() + timedelta(minutes=10)).isoformat()  # for demonstration

        # Emulating 2 executions for the digital twin
        for i in range(2):
            execution_data = {
                "title": f"Title for Execution {i+1}",
                "description": "Description for Execution",
                "tags": ["tag1", "tag2"],
                "workflowSchema": {
                    "workflowExecutor": "barfi",
                    "workflowExecutorVersion": "v2.0",
                    "components": [{"component": component_id,
                                    "version": version_id }],  # Array of ObjectIds for components. only one for testing
                    "WorkflowExecutorSchema": {}
                },
                "start_timestamp": datetime.utcnow(),
                "end_timestamp": datetime.utcnow(),
                "steps": []  # Array of ObjectIds referencing Steps collection. Change in a future by DAG graph.
            }

            execution_id = self.db_manager.append_execution(digital_twin_id, execution_data)

            # Emulating 2 steps
            for i in range(2):
                step_data = {
                    "timestamp": datetime.utcnow(),
                    "start_timestamp": datetime.utcnow(),
                    "end_timestamp": datetime.utcnow(),
                    "type": "ephemeral",
                    "logs": [],
                    "inputs": {},
                    "outputs": {},
                    "component": component_id,
                    "component_version": version_id,
                    "parameters": {"a":"a", "b":"b"},
                    "snapshot": ""
                }

                step_id = self.db_manager.append_step(execution_id, step_data)

                output_data = {
                    "s3_bucket": "bucket_name",  
                    "s3_key": "path/to/snapshot",
                    "output_type": "output",
                    "file_name": "snapshot_file_name",  
                    "file_size": 123456, 
                    "file_type": "image/jpeg",
                    "created_at": datetime.utcnow(),  
                    "updated_at": datetime.utcnow(),  
                    "metadata": {  # Additional metadata as
                        "description": "Description of the snapshot",
                        "tags": ["tag1", "tag2"],
                        "other_info": "Other relevant information"
                    },
                    "access_control": {  
                        "public": False,  
                        "authorized_users": [],  
                    }
                }

                output_id = self.db_manager.append_output(step_id, user_ids[0], output_data)

                # Using the append_log method to add logs to the above step
                for _ in range(3):  # adding 3 logs for demonstration purposes
                    log_data = {
                        "timestamp": datetime.now().isoformat(),
                        "type": "INFO",
                        "logstring": f"Emulated log entry {_+1}..."
                    }

                    self.db_manager.append_log(step_id, log_data)

            # Emulating results for the executed digital twin
            result_data = {
                "output": [output_id], #Last output saved as result
                "title": "Title for Result",
                "description": "Description for Result",
                "tags": ["tag1", "tag2"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            # Here, we'll use the `dt_id` as the execution reference for demonstration purposes
            # In a real scenario, the executionRef would point to a specific execution within a digital twin
            self.db_manager.add_result(digital_twin_id, execution_id, result_data)


##################################################################################