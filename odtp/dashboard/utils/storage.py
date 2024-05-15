import json
import logging

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.parse as parse
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.helpers.git as odtp_git
import odtp.helpers.utils as odtp_utils
import odtp.mongodb.db as db

CURRENT_USER = "user"
CURRENT_DIGITAL_TWIN = "digital_twin"
CURRENT_EXECUTION = "execution"
NEW_EXECUTION = "add_execution"
NEW_COMPONENT = "add_component"
CURRENT_COMPONENT = "component"
CURRENT_LOCAL_SETTINGS = "local_settings"
FORM_STATE_START = "start"
FORM_STATE_STEP = "step"
CURRENT_USER_WORKDIR = "user_workdir"
EXECUTION_RUN = "execution_run"


class ODTPFormValidationException(Exception):
    pass


def reset_storage_delete(keys):
    current_storage_keys = app.storage.user.keys()
    try:
        if not isinstance(keys, list):
            keys = [keys]
        for key in keys:
            if key in current_storage_keys:
                del app.storage.user[key]
    except Exception as e:
        logging.error(
            f"""During reset storage delete with keys {keys} en execption {e} occured. 
                  Current keys in storage {app.storage.user.keys()}"""
        )


def reset_storage_keep(keys):   
    current_storage_keys = app.storage.user.keys()
    try:
        if not isinstance(keys, list):
            keys = [keys]
        keys_in_storage_copy = list(app.storage.user.keys()).copy()
        for key in keys_in_storage_copy:
            if (key not in keys) and (key in current_storage_keys):
                del app.storage.user[key]
    except Exception as e:
        logging.error(
            f"""During reset storage keep with keys {keys} en execption {e} occured. 
                  Current keys in storage {app.storage.user.keys()}"""
        )


def get_active_object_from_storage(object_name):
    try:
        object = app.storage.user.get(object_name)
        if object:
            return json.loads(object)
    except Exception as e:
        logging.error(
            f"'{object_name}' could not be retrieved from storage. Exception occured: {e}"
        )


def get_value_from_storage_for_key(storage_key):
    return app.storage.user.get(storage_key)     


def storage_update_component(component_id):
    try:
        component = db.get_document_by_id(
            document_id=component_id, collection=db.collection_components
        )
        repo_link = component.get("repoLink")
        latest_commit = odtp_git.check_commit_for_repo(repo_link)
        repo_info = odtp_git.get_github_repo_info(repo_link)
        current_component = json.dumps(
            {
                "component_id": component_id,
                "name": component.get("componentName"),
                "repo_link": component.get("repoLink"),
                "type": component.get("type"),
                "latest_commit": latest_commit,
                "repo_info": repo_info,
            }
        )
        app.storage.user[CURRENT_COMPONENT] = current_component
    except Exception as e:
        logging.error(
            f"storage update for {CURRENT_COMPONENT} failed: {e}"
        )


def store_execution_selection(storage_key, execution_id):
    execution = db.get_document_by_id(
        document_id=execution_id, collection=db.collection_executions
    )
    version_tags = odtp_utils.get_version_names_for_execution(
        execution=execution,
        naming_function=helpers.get_execution_step_display_name,
    )
    step_ids = [str(step_id) for step_id in execution["steps"]]
    step_documents = db.get_document_by_ids_in_collection(
        document_ids=step_ids, collection=db.collection_steps
    )
    step_dict = {}
    for step_document in step_documents:
        step_dict[str(step_document["_id"])] = step_document
    ports = []
    parameters = []
    outputs = []
    inputs = []
    for step_id in step_ids:
        parameters.append(step_dict[step_id].get("parameters", {}))
        ports.append(step_dict[step_id].get("ports", []))
        outputs.append(step_dict[step_id].get("output", {}))
        inputs.append(step_dict[step_id].get("input", {}))
    current_execution = {
        "execution_id": execution_id,
        "title": execution.get("title"),
        "timestamp": execution.get("start_timestamp").strftime(
            "%m/%d/%Y, %H:%M:%S"
        ),
        "versions": execution.get("component_versions"),
        "version_tags": version_tags,
        "steps": step_ids,
        "ports": ports,
        "parameters": parameters,
        "outputs": outputs,
        "inputs": inputs,
    }
    current_execution_as_json = json.dumps(current_execution)
    app.storage.user[storage_key] = current_execution_as_json
