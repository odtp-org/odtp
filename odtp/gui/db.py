from pymongo import MongoClient
from bson import ObjectId
import json

#################################################################################
# Testing Class MongoManager with v.0.2.0 Schema version of ID.

class MongoManager:
    def __init__(self, mongodbUrl,db_name):
        self.client = MongoClient(mongodbUrl)
        self.db = self.client[db_name]

    def add_user(self, displayName, email, github):
        users_collection = self.db["users"]
        user_data = {
            "displayName": displayName,
            "email": email,
            "github": github
        }
        return users_collection.insert_one(user_data).inserted_id

    def add_component(self, author_id, componentName):
        components_collection = self.db["components"]
        component_data = {
            "author": author_id,
            "componentName": componentName
        }
        return components_collection.insert_one(component_data).inserted_id

    def add_version(self, componentId, version, repoLink, dockerHubLink, parameters={}):
        versions_collection = self.db["versions"]
        version_data = {
            "componentId": componentId,
            "version": version,
            "repoLink": repoLink,
            "dockerHubLink": dockerHubLink,
            "parameters": parameters
        }
        return versions_collection.insert_one(version_data).inserted_id

    def add_digital_twin(self, userRef, version, components, barfiSchema={}, public=True, execution=[]):
        digital_twins_collection = self.db["digitalTwins"]
        digital_twin_data = {
            "userRef": userRef,
            "workflowSchema": {
                "version": version,
                "components": components,
                "barfiSchema": barfiSchema,
                "public": public
            },
            "executions": execution
        }
        return digital_twins_collection.insert_one(digital_twin_data).inserted_id

    def add_result(self, execution_ref, execution_timestamp, outputs):
        """
        Add a result entry to the results collection.

        :param execution_ref: Reference to an execution in DigitalTwins.execution.
        :param outputs: Outputs associated with the result.
        :return: The ObjectId of the created result document.
        """
        results_collection = self.db["results"]
        result = {
            "executionRef": execution_ref,
            "execution.timestamp": execution_timestamp,
            "outputs": outputs
        }
        return results_collection.insert_one(result).inserted_id
    
    def append_execution(self, digital_twin_id, execution_data):
        """
        Append a new execution to a specific digital twin.

        :param digital_twin_id: ObjectId of the digital twin.
        :param execution_data: The execution data to append.
        """
        digital_twins_collection = self.db["digitalTwins"]
        digital_twins_collection.update_one(
            {"_id": digital_twin_id},
            {"$push": {"executions": execution_data}}
        )

    def append_step(self, digital_twin_id, execution_timestamp, step_data):
        """
        Append a step to a specific execution within a digital twin.

        :param digital_twin_id: ObjectId of the digital twin.
        :param execution_timestamp: Timestamp of the specific execution.
        :param step_data: The step data to append.
        """
        digital_twins_collection = self.db["digitalTwins"]
        digital_twins_collection.update_one(
            {"_id": digital_twin_id, "execution.timestamp": execution_timestamp},
            {"$push": {"executions.$.steps": step_data}}
        )

    def append_log(self, digital_twin_id, execution_timestamp, step_timestamp, log_entry):
        """
        Append a log entry to a specific step of a specific execution within a digital twin.

        :param digital_twin_id: ObjectId of the digital twin.
        :param execution_timestamp: Timestamp of the specific execution.
        :param step_timestamp: Timestamp of the specific step.
        :param log_entry: The log entry (dictionary) to append.
        """
        digital_twins_collection = self.db["digitalTwins"]
        
        # Get the document with the specific digital twin ID
        doc = digital_twins_collection.find_one({"_id": digital_twin_id})
        
        # Find the index of the specific execution and step
        execution_index = -1
        step_index = -1
        for i, execution in enumerate(doc["executions"]):
            if execution["timestamp"] == execution_timestamp:
                execution_index = i
                for j, step in enumerate(execution["steps"]):
                    if step["timestamp"] == step_timestamp:
                        step_index = j
                        break
                break

        # If the execution and step are found, update the logs for that step
        if execution_index != -1 and step_index != -1:
            update_path = f"executions.{execution_index}.steps.{step_index}.logs"
            digital_twins_collection.update_one(
                {"_id": digital_twin_id},
                {"$push": {update_path: log_entry}}
            )

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

    ######################################

    def close(self):
        self.client.close()


##################################################################################
# Testing the DB with mockup data

from datetime import datetime, timedelta

from random import choice

class MockDataEmulator:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def emulate_data(self):
        # Emulating some users
        user_ids = [
            self.db_manager.add_user("John Doe", "john@example.com", "johnDoeRepo"),
            self.db_manager.add_user("Alice Smith", "alice@example.com", "aliceSmithRepo"),
            self.db_manager.add_user("Bob Johnson", "bob@example.com", "bobJohnsonRepo")
        ]

        # Emulating some components for each user
        component_ids = [
            self.db_manager.add_component(user_id, f"Component_{i}")
            for i, user_id in enumerate(user_ids, 1)
        ]

        # Emulating versions for each component
        version_links = [
            ("https://github.com/John/Component_1", "https://hub.docker.com/John/Component_1"),
            ("https://github.com/Alice/Component_2", "https://hub.docker.com/Alice/Component_2"),
            ("https://github.com/Bob/Component_3", "https://hub.docker.com/Bob/Component_3")
        ]

        for i, component_id in enumerate(component_ids):
            self.db_manager.add_version(
                component_id,
                f"v{i+1}.0",
                version_links[i][0],
                version_links[i][1]
            )

        # Emulating a digital twin for a user
        dt_id = self.db_manager.add_digital_twin(
            choice(user_ids),
            "v1.0",
            component_ids
        )

        execution_timestamp = datetime.now().isoformat()
        step_timestamp = (datetime.now() + timedelta(minutes=1)).isoformat()  # for demonstration

        step_data = {
            "timestamp": step_timestamp,
            "logs": [],  # start with empty logs
            "inputs": {"input1": "data1"},
            "outputs": {"output1": "result1"},
            "component": choice(component_ids),
            "component_version": "v1.0",
            "parameters": {"param1": "value1"},
            "snapshot": "Snapshot data..."
        }

        execution_data = {
            "timestamp": execution_timestamp,
            "steps": [step_data]
        }
        
        self.db_manager.append_execution(dt_id, execution_data)

        # Using the append_log method to add logs to the above step
        for _ in range(3):  # adding 3 logs for demonstration purposes
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "logstring": f"Emulated log entry {_+1}..."
            }
            self.db_manager.append_log(dt_id, execution_timestamp, step_timestamp, log_entry)

        # Emulating results for the executed digital twin
        outputs = {
            "finalOutput1": "finalResult1",
            "finalOutput2": "finalResult2"
        }
        # Here, we'll use the `dt_id` as the execution reference for demonstration purposes
        # In a real scenario, the executionRef would point to a specific execution within a digital twin
        self.db_manager.add_result(dt_id, execution_timestamp, outputs)


##################################################################################