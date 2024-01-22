"""
The goal of this script is to generate and initial mockup data for the instances.
"""
from pymongo import MongoClient
from bson import ObjectId, json_util
import json
import logging
import os
from dotenv import load_dotenv
from datetime import datetime


class odtpDatabase:
    def __init__(self):
        load_dotenv()
        url = os.getenv("ODTP_MONGO_SERVER")
        db_name = "odtp"
        dbManager = MongoManager(url, db_name)
        self.dbManager = dbManager
        logging.info("Connected to: %s", dbManager)

    def __enter__(self):
        return self.dbManager

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbManager.close()


class MongoManager:
    def __init__(self, mongodbUrl, db_name):
        """mongo db client"""
        self.client = MongoClient(mongodbUrl)
        self.db = self.client[db_name]

    def add_user(self, name, github, email):
        """add new user and return id"""
        users_collection = self.db["users"]
        user_data = {
            "displayName": name,
            "email": email,
            "github": github,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        return users_collection.insert_one(user_data).inserted_id

    def add_component(self, component_data):
        """add new component and return id"""
        components_collection = self.db["components"]
        return components_collection.insert_one(component_data).inserted_id

    def add_version(self, componentId, version_data):
        """add new version of a component and return id"""
        versions_collection = self.db["versions"]
        version_data["componentId"] = ObjectId(componentId)
        return versions_collection.insert_one(version_data).inserted_id

    def add_digital_twin(self, userRef, digital_twin_data):
        """add new digital twin alogn with user reference"""
        digital_twins_collection = self.db["digitalTwins"]
        digital_twin_data["userRef"] = userRef
        digital_twin_id = digital_twins_collection.insert_one(digital_twin_data).inserted_id
        self.db.users.update_one(
            {"_id": ObjectId(userRef)},
            {"$push": {"digitalTwins": digital_twin_id}}
        )
        return digital_twin_id

    def append_execution(self, digital_twin_id, execution_data):
        """append execution"""
        executions_collection = self.db["executions"]
        execution_data["digitalTwinRef"] = ObjectId(digital_twin_id)
        execution_id = executions_collection.insert_one(execution_data).inserted_id
        self.db.digitalTwins.update_one(
            {"_id": ObjectId(digital_twin_id)},
            {"$push": {"executions": ObjectId(execution_id)}}
        )
        return execution_id

    def append_step(self, execution_id, step_data):
        """add new step"""
        steps_collection = self.db["steps"]
        step_data["executionRef"] = execution_id
        step_id = steps_collection.insert_one(step_data).inserted_id
        self.db.executions.update_one(
            {"_id": execution_id},
            {"$push": {"steps": step_id}}
        )
        return step_id

    def append_output(self, step_id, user_id, output_data):
        """add new output"""
        steps_collection = self.db["outputs"]
        output_data["stepRef"] = step_id
        # TODO: Make its own function
        output_data["access_control"]["authorized_users"] = user_id

        output_id = steps_collection.insert_one(output_data).inserted_id

        # Update digital twin with execution reference
        self.db.digitalTwins.update_one(
            {"_id": step_id},  # Specify the document to update
            {"$set": {"field_name": output_id}}  # Use $set to replace the value of a field
        )
        return output_id

    def append_log(self, step_id, log_data):
        """add log entries"""
        steps_collection = self.db["steps"]
        steps_collection.update_one(
            {"_id": step_id},
            {"$push": {"logs": log_data}}
        )

    def add_result(self, digital_twin_id, execution_id, result_data):
        """add result"""
        results_collection = self.db["results"]
        result_data["digitalTwinRef"] = digital_twin_id
        result_data["executionRed"] = execution_id
        result_id = results_collection.insert_one(result_data).inserted_id
        return result_id

    def get_all_collections(self, as_json=False):
        """
        Retrieve all documents in all collections
        """
        all_data = {}
        for collection_name in self.db.list_collection_names():
            cursor = self.db[collection_name].find()
            all_data[collection_name] = [doc for doc in cursor]
        if as_json:
            return json.dumps(all_data, indent=2, default=str)
        return all_data

    def find_in_collection(self, collection, field_name, field_value, as_js=True):
        """
        Retrieve all documents that match in a collection
        """
        documents = self.db[collection].find({field_name: field_value})
        if as_js:
            json_output = json.dumps(documents, indent=4, default=json_util.default)
            return json_output
        return documents

    def get_all_documents(self, collection):
        cursor = self.db[collection].find()
        users = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            users.append(doc)
        return users

    def get_digital_twins_by_user_id(self, user_id_str):
        # Convert user_id string to ObjectId
        user_id = ObjectId(user_id_str)
        # Fetch digital twins by user_id
        cursor = self.db.digitalTwins.find(
            {"userRef": user_id},
            {"_id": 1, "userRef": 1,
             "executions[0].timestamp": 1,
             "executions[0].timestamp": 1}
        )
        digital_twins = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for pandas compatibility
            digital_twins.append(doc)
        return digital_twins

    def get_document_by_id(self, document_id, collection):
        # Skip to the digital twin specified by the given index and retrieve it
        document = self.db[collection].find_one({'_id': ObjectId(document_id)})
        try:
            # Navigate to the logs using the given execution index
            json_output = json.dumps(document, indent=4, default=json_util.default)
        except (IndexError, KeyError):
            print(f"No execution found for execution {document_id}.")
        return json_output

    def get_document_by_id_as_dict(self, document_id, collection):
        # Skip to the document specified by the given id and retrieve it
        document = self.db[collection].find_one({'_id': ObjectId(document_id)})
        if document:
            document["_id"] = str(document["_id"])  # Convert ObjectId to string
            return document
        else:
            return None

    def close(self):
        self.client.close()

    def deleteAll(self):
        # Connect to your database. Replace 'mydatabase' with your database name.
        db_odtp = self.db
        # Get a list of all collections in the database
        collections = db_odtp.list_collection_names()
        # Drop each collection
        for collection in collections:
            db_odtp.drop_collection(collection)
