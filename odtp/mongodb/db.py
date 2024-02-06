"""
Connect to the Mongo DB
"""
import logging
from datetime import datetime

from bson import ObjectId
from dotenv import dotenv_values
from pymongo import MongoClient

import odtp.mongodb.utils as utils

config = dotenv_values(".env")
mongodb_url = config["ODTP_MONGO_SERVER"]
db_name = config["ODTP_MONGO_DB"]
collection_users = "users"
collection_components = "components"
collection_versions = "versions"
collection_digital_twins = "digitalTwins"
collection_executions = "executions"
collection_steps = "steps"


def get_db():
    """Retrieve all documents from the db"""
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        all_data = {}
        for collection_name in db.list_collection_names():
            cursor = db[collection_name].find()
            all_data[collection_name] = [doc for doc in cursor]
    return all_data


def get_collection(collection):
    """Retrieve all documents from a collection"""
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        cursor = db[collection].find({})
    return utils.get_list_from_cursor(cursor)


def get_all_collections():
    """
    Retrieve all documents in all collections
    """
    all_data = {}
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        for collection_name in db.list_collection_names():
            cursor = db[collection_name].find()
            all_data[collection_name] = [doc for doc in cursor]
        return all_data


def get_document_by_id(document_id, collection):
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        document = db[collection].find_one({"_id": ObjectId(document_id)})
    return document


def delete_document_by_id(document_id, collection):
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        document = db[collection].delete_one({"_id": ObjectId(document_id)})
        logging.info(f"Document with ID {document_id} was deleted")


def get_sub_collection_items(collection, sub_collection, item_id, ref_name):
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        collection_item = db[collection].find_one({"_id": ObjectId(item_id)})
        if not collection_item:
            return []
        sub_collection_ids = collection_item.get(ref_name)
        if not sub_collection_ids:
            return []
        cursor = db[sub_collection].find({"_id": {"$in": sub_collection_ids}})
        documents = utils.get_list_from_cursor(cursor)
        return documents


def add_user(name, github, email):
    """add new user and return id"""
    user_data = {
        "displayName": name,
        "email": email,
        "github": github,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    with MongoClient(mongodb_url) as client:
        user_id = client[db_name][collection_users].insert_one(user_data).inserted_id
    logging.info("User added with ID {}".format(user_id))
    return user_id


def add_component_version(
    component_name,
    repository,
    odtp_version,
    component_version,
    commit_hash,
):
    """add component and component version"""
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        component = db[collection_components].find_one({"repoLink": repository})
        if not component:
            component_data = {
                "author": "Test",
                "componentName": component_name,
                "repoLink": repository,
                "status": "active",
                "title": "Title for ComponentX",
                "description": "Description for ComponentX",
                "tags": ["tag1", "tag2"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "versions": [],
            }
            component_id = (
                db[collection_components].insert_one(component_data).inserted_id
            )
        else:
            component_id = component["_id"]
        version_data = {
            "odtp_version": odtp_version,
            "component_version": component_version,
            "commitHash": commit_hash,
            "dockerHubLink": "",
            "parameters": {},
            "title": "Title for Version v1.0",
            "description": "Description for Version v1.0",
            "tags": ["tag1", "tag2"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        version_id = db[collection_versions].insert_one(version_data).inserted_id
        logging.info("Version added with ID {}".format(version_id))
        db[collection_components].update_one(
            {"_id": ObjectId(component_id)}, {"$push": {"versions": version_id}}
        )
    return component_id, version_id


def add_digital_twin(userRef, name):
    """add digital twin"""
    digital_twin_data = {
        "name": name,
        "status": "active",
        "public": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "executions": [],
    }
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        digital_twin_data["userRef"] = userRef
        digital_twin_id = (
            db[collection_digital_twins].insert_one(digital_twin_data).inserted_id
        )
        logging.info(f"Digital Twin added with ID {digital_twin_id}")

        # Add digital twin reference to user
        db[collection_users].update_one(
            {"_id": ObjectId(userRef)}, {"$push": {"digitalTwins": digital_twin_id}}
        )
    return digital_twin_id


def add_execution(
    dt_id,
    name,
    components,
    versions,
    workflow,
    ports,
):
    """add and execution to the database"""
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        components = [ObjectId(c) for c in components.split(",")]
        versions = [ObjectId(v) for v in versions.split(",")]
        components_list = [
            {"component": c, "version": v} for c, v in zip(components, versions)
        ]
        execution_data = {
            "title": name,
            "description": "Description for Execution",
            "tags": ["tag1", "tag2"],
            "workflowSchema": {
                "workflowExecutor": "odtpwf",
                "workflowExecutorVersion": "0.2.0",
                "components": components_list,  # Array of ObjectIds for components
                "workflowExecutorSchema": [int(i) for i in workflow.split(",")],
            },
            "start_timestamp": datetime.utcnow(),
            "end_timestamp": datetime.utcnow(),
            "steps": [],  # Array of ObjectIds referencing Steps collection. Change in a future by DAG graph
        }
        execution_id = append_execution(db, dt_id, execution_data)
        logging.info(f"Execution added with ID {execution_id}")

        steps_ids = []
        for c in components_list:
            step_data = {
                "timestamp": datetime.utcnow(),
                "start_timestamp": datetime.utcnow(),
                "end_timestamp": datetime.utcnow(),
                "type": "ephemeral",
                "logs": [],
                "inputs": {},
                "outputs": {},
                "component": c["component"],
                "component_version": c["version"],
                "parameters": {},
                "ports": ports,
            }
            step_id = append_step(db, execution_id, step_data)
            steps_ids.append(step_id)
        logging.info(f"STEPS added with ID {steps_ids}")
        return (execution_id, steps_ids)


def append_execution(db, digital_twin_id, execution_data):
    executions_collection = db[collection_executions]
    execution_data["digitalTwinRef"] = ObjectId(digital_twin_id)
    execution_id = executions_collection.insert_one(execution_data).inserted_id
    # Update digital twin with execution reference
    db.digitalTwins.update_one(
        {"_id": ObjectId(digital_twin_id)},
        {"$push": {"executions": ObjectId(execution_id)}},
    )
    return execution_id


def append_step(db, execution_id, step_data):
    steps_collection = db[collection_steps]
    step_data["executionRef"] = execution_id
    step_id = steps_collection.insert_one(step_data).inserted_id
    # Update execution with step reference
    db.executions.update_one({"_id": execution_id}, {"$push": {"steps": step_id}})
    return step_id


def delete_collection(collection):
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        db.drop_collection(collection)


def delete_all():
    with MongoClient(mongodb_url) as client:
        db = client[db_name]
        # Get a list of all collections in the database
        collections = db.list_collection_names()
        # Drop each collection
        for collection in collections:
            db.drop_collection(collection)
