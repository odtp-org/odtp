from pymongo import MongoClient
from bson import ObjectId, json_util
import json
import logging
import datetime


#################################################################################
# Testing Class MongoManager with v.0.2.0 Schema version of ID.

class MongoManager:
    def __init__(self, mongodbUrl, db_name):
        self.client = MongoClient(mongodbUrl)
        self.db = self.client[db_name]

    def add_user(self, user_data):
        users_collection = self.db["users"]

        return users_collection.insert_one(user_data).inserted_id

    def add_component(self, component_data):
        components_collection = self.db["components"]

        return components_collection.insert_one(component_data).inserted_id

    def add_version(self, componentId, version_data):
        versions_collection = self.db["versions"]
        version_data["componentId"] = ObjectId(componentId)

        return versions_collection.insert_one(version_data).inserted_id

    def add_digital_twin(self, userRef, digital_twin_data):
        digital_twins_collection = self.db["digitalTwins"]
        digital_twin_data["userRef"] = userRef

        digital_twin_id = digital_twins_collection.insert_one(digital_twin_data).inserted_id

        # Add digital twin reference to user
        self.db.users.update_one(
            {"_id": ObjectId(userRef)},
            {"$push": {"digitalTwins": digital_twin_id}}
        )

        return digital_twin_id


    def append_execution(self, digital_twin_id, execution_data):
        executions_collection = self.db["executions"]
        execution_data["digitalTwinRef"] = ObjectId(digital_twin_id)

        execution_id = executions_collection.insert_one(execution_data).inserted_id

        # Update digital twin with execution reference
        self.db.digitalTwins.update_one(
            {"_id": ObjectId(digital_twin_id)},
            {"$push": {"executions": ObjectId(execution_id)}}
        )

        return execution_id


    def append_step(self, execution_id, step_data):
        steps_collection = self.db["steps"]
        step_data["executionRef"] = execution_id

        step_id = steps_collection.insert_one(step_data).inserted_id

        # Update execution with step reference
        self.db.executions.update_one(
            {"_id": execution_id},
            {"$push": {"steps": step_id}}
        )

        return step_id
    
    def append_output(self, step_id, user_id, output_data):
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
        steps_collection = self.db["steps"]
        steps_collection.update_one(
            {"_id": step_id},
            {"$push": {"logs": log_data}}
        )

    def add_result(self, digital_twin_id, execution_id, result_data):
        results_collection = self.db["results"]
        result_data["digitalTwinRef"] = digital_twin_id
        result_data["executionRed"] = execution_id
        
        result_id = results_collection.insert_one(result_data).inserted_id

        return result_id
    
    ######### Get methods

    def get_all_collections_as_dict(self):
            """
            Retrieve all documents in all collections as a dictionary.
            """
            all_data = {}
            for collection_name in self.db.list_collection_names():
                cursor = self.db[collection_name].find()
                all_data[collection_name] = [doc for doc in cursor]
            
            return all_data

    def get_all_collections_as_json_string(self):
        """
        Retrieve all documents in all collections as a JSON-formatted string.
        """
        all_data = self.get_all_collections_as_dict()
        return json.dumps(all_data, indent=2, default=str)  # default=str to handle datetime and ObjectId


    def print_all_collections_as_json(self):
        """
        Print all documents in all collections in JSON format.
        """
        for collection_name in self.db.list_collection_names():
            print(f"Collection: {collection_name}")
            cursor = self.db[collection_name].find()
            for doc in cursor:
                print(json.dumps(doc, indent=2, default=str))  # default=str is added to handle datetime and ObjectId
            print("-" * 50)  # separator line between collections


    def export_all_collections_as_json(self, filename):
        """
        Save all documents in all collections as a JSON file.
        """
        all_data = self.get_all_collections_as_dict()
        with open(filename, 'w') as json_file:
            json.dump(all_data, json_file, indent=2, default=str)  # default=str to handle datetime and ObjectId


    ######################################
    # USER METHOD

    def get_all_users(self):
        cursor = self.db.users.find({})

        users = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            users.append(doc)

        return users
    
    def get_digital_twins_by_user_id(self, user_id_str):
        # Convert user_id string to ObjectId
        user_id = ObjectId(user_id_str)
        
        # Fetch digital twins by user_id
        cursor = self.db.digitalTwins.find({"userRef": user_id}, {"_id": 1, "userRef": 1, "executions[0].timestamp": 1, "executions[0].timestamp": 1})
        
        digital_twins = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for pandas compatibility
            digital_twins.append(doc)
            
        return digital_twins
    
    # def print_logs_by_indices(self, twin_index, execution_index, step_index):
    #     # Skip to the digital twin specified by the given index and retrieve it
    #     digital_twin = self.db.digitalTwins.find().sort("_id", 1).skip(twin_index).limit(1).next()

    #     try:
    #         # Navigate to the logs using the given execution index
    #         logs = digital_twin["executions"][execution_index]["steps"][step_index]["logs"]
    #     except (IndexError, KeyError):
    #         print(f"No logs found for execution {execution_index} of digital twin {twin_index}.")

    #     return logs
    
    def get_document_by_id(self, execution_id, collection):
        # Skip to the digital twin specified by the given index and retrieve it
        document = self.db[collection].find_one({'_id': ObjectId(execution_id)})
        print(document)
        try:
            # Navigate to the logs using the given execution index
            json_output = json.dumps(document, indent=4, default=json_util.default)
        except (IndexError, KeyError):
            print(f"No execution found for execution {execution_id}.")

        return json_output

    ######################################
    # Closing & Deleting
    ######################################

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


