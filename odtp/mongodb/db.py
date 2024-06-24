"""
Connect to the Mongo DB
"""
import logging
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING

import odtp.helpers.git as git_helpers
import odtp.helpers.utils as odtp_utils
import odtp.mongodb.utils as mongodb_utils
from odtp.helpers.settings import ODTP_MONGO_DB, ODTP_MONGO_SERVER

collection_users = "users"
collection_components = "components"
collection_versions = "versions"
collection_digital_twins = "digitalTwins"
collection_executions = "executions"
collection_steps = "steps"
collection_results = "results"
collection_logs = "logs"
collection_outputs = "outputs"


log = logging.getLogger(__name__)


def get_db():
    """Retrieve all documents from the db"""
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        all_data = {}
        for collection_name in db.list_collection_names():
            cursor = db[collection_name].find()
            all_data[collection_name] = [doc for doc in cursor]
    return all_data


def check_connection():
    with MongoClient(ODTP_MONGO_SERVER, serverSelectionTimeoutMS = 2000) as client:
        return client.server_info()


def get_collection_names():
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        db.list_collection_names()


def get_collection(collection):
    """Retrieve all documents from a collection"""
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        cursor = db[collection].find({})
        return mongodb_utils.get_list_from_cursor(cursor)


def get_all_collections():
    """
    Retrieve all documents in all collections
    """
    all_data = {}
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        for collection_name in db.list_collection_names():
            cursor = db[collection_name].find()
            all_data[collection_name] = [doc for doc in cursor]
        return all_data


def get_document_by_id(document_id, collection):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        document = db[collection].find_one({"_id": ObjectId(document_id)})
    return document


def get_document_by_ids_in_collection(document_ids, collection):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        cursor = db[collection].find(
            {"_id": {"$in": [ObjectId(id) for id in document_ids]}}
        )
        documents = mongodb_utils.get_list_from_cursor(cursor)
    return documents


def get_collection_sorted(collection, sort_tuples):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        collection = collection_versions
        cursor = db[collection].find().sort([("component.componentName", ASCENDING), ("component_version", DESCENDING)])
        documents = mongodb_utils.get_list_from_cursor(cursor)
    return documents


def check_document_ids_in_collection(document_ids, collection):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        document_ids_in_db = db[collection].find(
            {"_id": {"$in": [ObjectId(id) for id in document_ids]}}, {"_id": 1}
        )
        document_ids_missing_in_db = [
            document_id
            for document_id in document_ids
            if document_id not in document_ids_in_db
        ]
        if not document_ids_missing_in_db:
            raise mongodb_utils.OdtpDbMongoDBValidationException(
                f"document with {document_ids} does not exist in collection {collection}"
            )


def check_document_id_in_collection(document_id, collection):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        document = get_document_by_id(document_id=document_id, collection=collection)
        if not document:
            raise mongodb_utils.OdtpDbMongoDBValidationException(
                f"document with {document_id} does not exist in collection {collection}"
            )


def delete_document_by_id(document_id, collection):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        document = db[collection].delete_one({"_id": ObjectId(document_id)})
        log.info(f"Document with ID {document_id} was deleted")


def get_sub_collection_items(collection, sub_collection, item_id, ref_name, sort_by=None):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        collection_item = db[collection].find_one({"_id": ObjectId(item_id)})
        if not collection_item:
            return []
        sub_collection_ids = collection_item.get(ref_name)
        if not sub_collection_ids:
            return []
        cursor = db[sub_collection].find({"_id": {"$in": sub_collection_ids}})
        if sort_by:
            cursor.sort(sort_by)
        documents = mongodb_utils.get_list_from_cursor(cursor)
        return documents


def get_document_id_by_field_value(field_path, field_value, collection):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        document = db[collection].find_one({field_path: field_value}, {"_id": 1})
        if document:
            return str(document["_id"])
        else:
            return None
        
def get_component_version(component_name, version_tag):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        cursor = db[collection_versions].find({
            "component.componentName": component_name,
            "component_version": version_tag
        })
        version_documents = mongodb_utils.get_list_from_cursor(cursor)
    return version_documents


def add_user(name, github, email):
    """add new user and return id"""
    user_data = {
        "displayName": name,
        "email": email,
        "github": github,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    with MongoClient(ODTP_MONGO_SERVER) as client:
        user_id = (
            client[ODTP_MONGO_DB][collection_users].insert_one(user_data).inserted_id
        )
    log.info("User added with ID {}".format(user_id))
    return user_id


def add_component_version(
    repo_info,
    component_name,
    component_version,
    type,
    ports,
):
    """add component and component version"""

    # check first
    try:
        mongodb_utils.check_component_ports(ports)
        mongodb_utils.check_component_type(type)
        commit_hash = git_helpers.get_commit_of_component_version(
            repo_info=repo_info,
            component_version=component_version,
        )
        repo_url = repo_info.get("html_url")
        tagged_versions = repo_info.get("tagged_versions")
        version_commit = [version["commit"] for version in tagged_versions
                          if version["name"] == component_version]
        if not version_commit:
            raise Exception("Version does not exist in repo")
    except Exception as e:
        e.add_note("-> Component Version not valid: was not stored in mongodb")
        raise (e)
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        component = db[collection_components].find_one({"repoLink": repo_url})
        if component:
            component_id = component["_id"]
            log.info(
                f"Component with ID {component_id} already existed for repo {repo_url}"
            )
        else:
            component_data = {
                "author": "Test",
                "componentName": component_name,
                "repoLink": repo_url,
                "status": "active",
                "title": "Title for ComponentX",
                "type": type,
                "description": "Description for ComponentX",
                "tags": ["tag1", "tag2"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "versions": [],
            }
            component_id = (
                db[collection_components].insert_one(component_data)
            ).inserted_id
            log.info(f"Component added with ID {component_id}")
            component = db[collection_components].find_one({"_id": component_id})
        version = db[collection_versions].find_one(
            {
                "component_version": component_version,
                "componentId": component_id,
            }
        )
        if version:
            log.info(
                f"Version {component_version} already existed"
            )
            raise mongodb_utils.OdtpDbMongoDBValidationException(
                f"document for repository {repo_url} and version {component_version} already exists"
            )
        else:
            version_data = {
                "componentId": component_id,
                "component": {
                    "componentId": component_id,
                    "componentName": component.get("componentName"),
                    "repoLink": component.get("repoLink"),
                    "type": component.get("type"),
                },
                "odtp_version": odtp_utils.get_odtp_version(),
                "component_version": component_version,
                "commitHash": commit_hash,
                "dockerHubLink": "",
                "parameters": {},
                "title": "Title for Version v1.0",
                "description": "Description for Version v1.0",
                "tags": ["tag1", "tag2"],
                "ports": ports,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            # set optional properties
            if component_version:
                version_data["component_version"] = component_version
            if ports:
                version_data["ports"] = ports
            version_id = db[collection_versions].insert_one(version_data).inserted_id
            log.info("Version added with ID {}".format(version_id))
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
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "executions": [],
    }
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        digital_twin_data["userRef"] = userRef
        digital_twin_id = (
            db[collection_digital_twins].insert_one(digital_twin_data).inserted_id
        )
        log.info(f"Digital Twin added with ID {digital_twin_id}")

        # Add digital twin reference to user
        db[collection_users].update_one(
            {"_id": ObjectId(userRef)}, {"$push": {"digitalTwins": digital_twin_id}}
        )
    return digital_twin_id


def set_document_timestamp(document_id, collection_name, timestamp_name):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        collection = db[collection_name]
        collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {timestamp_name: datetime.now(timezone.utc)}},
        )


def add_execution(
    dt_id,
    name,
    versions,
    parameters,
    ports,
):
    """add and execution to the database"""
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        try:
            mongodb_utils.check_parameters_for_execution(parameters)
            mongodb_utils.check_port_mappings_for_execution(ports)
            check_document_ids_in_collection(
                document_ids=versions, collection=collection_versions
            )
            check_document_id_in_collection(
                document_id=dt_id, collection=collection_digital_twins
            )
            workflow = odtp_utils.get_workflow(versions)
            execution = {
                "title": name,
                "description": "Description for Execution",
                "tags": ["tag1", "tag2"],
                "workflowSchema": {
                    "workflowExecutor": "odtpwf",
                    "workflowExecutorVersion": "0.2.0",
                    "component_versions": versions,
                    "workflowExecutorSchema": workflow,
                },
                "start_timestamp": datetime.now(timezone.utc),
                "end_timestamp": datetime.now(timezone.utc),
                # Array of ObjectIds referencing Steps collection. Change in a future by DAG graph
                "steps": [],
            }
            steps = []
            for i, version in enumerate(versions):
                step = {
                    "timestamp": datetime.now(timezone.utc),
                    "start_timestamp": datetime.now(timezone.utc),
                    "end_timestamp": datetime.now(timezone.utc),
                    "type": "ephemeral",
                    "logs": [],
                    "inputs": {},
                    "outputs": {},
                    "component_version": versions[i],
                    "parameters": parameters[i] or {},
                    "ports": ports[i],
                }
                steps.append(step)
            execution_id = append_execution_to_digital_twin(db, dt_id, execution)
            log.info(f"Execution added with ID {execution_id}")
            steps_ids = []
            for step in steps:
                step_id = append_step_to_execution(db, execution_id, step)
                steps_ids.append(step_id)
            log.info(f"STEPS added with ID {steps_ids}")
        except Exception as e:
            e.add_note("-> Execution not valid: was not stored in mongodb")
            raise (e)
        else:
            return (execution_id, steps_ids)


def append_execution_to_digital_twin(db, digital_twin_id, execution):
    executions_collection = db[collection_executions]
    execution["digitalTwinRef"] = ObjectId(digital_twin_id)
    execution_id = executions_collection.insert_one(execution).inserted_id
    # Update digital twin with execution reference
    db.digitalTwins.update_one(
        {"_id": ObjectId(digital_twin_id)},
        {"$push": {"executions": ObjectId(execution_id)}},
    )
    return execution_id


def append_step_to_execution(db, execution_id, step):
    steps_collection = db[collection_steps]
    step["executionRef"] = execution_id
    step_id = steps_collection.insert_one(step).inserted_id
    # Update execution with step reference
    db.executions.update_one({"_id": execution_id}, {"$push": {"steps": step_id}})
    return step_id


def delete_collection(collection):
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        db.drop_collection(collection)


def delete_all():
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        # Get a list of all collections in the database
        collections = db.list_collection_names()
        # Drop each collection
        for collection in collections:
            db.drop_collection(collection)


def check_collections(collection):
    collections = get_all_collections()
    if collection not in collections:
        raise mongodb_utils.OdtpDbMongoDBValidationException(
            f"{collection} is not a valid mongo db collection"
        )

def init_collections():
    with MongoClient(ODTP_MONGO_SERVER) as client:
        db = client[ODTP_MONGO_DB]
        collection_names = db.list_collection_names()
        for name in [
            collection_users,
            collection_components,
            collection_digital_twins,
            collection_executions,
            collection_outputs,
            collection_results,
            collection_versions,
            collection_logs,
        ]:
            if name not in collection_names:
                db.create_collection(name)
                log.info(f"Collections has been created or exists: {name}")
