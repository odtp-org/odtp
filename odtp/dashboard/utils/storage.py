import json
import os
import re
from datetime import datetime

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
        ui.notify(
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
        ui.notify(
            f"""During reset storage keep with keys {keys} en execption {e} occured. 
                  Current keys in storage {app.storage.user.keys()}"""
        )


def storage_update_digital_twin(digital_twin_id):
    try:
        digital_twin = db.get_document_by_id(
            document_id=digital_twin_id, collection=db.collection_digital_twins
        )
        current_digital_twin = json.dumps(
            {"digital_twin_id": digital_twin_id, "name": digital_twin.get("name")}
        )
        app.storage.user[CURRENT_DIGITAL_TWIN] = current_digital_twin
    except Exception as e:
        ui.notify(
            f"storage update for {CURRENT_DIGITAL_TWIN} failed: {e}", type="negative"
        )


def storage_update_local_settings(project_path):
    try:
        if CURRENT_LOCAL_SETTINGS in app.storage.user.keys():
            local_settings = get_active_object_from_storage(CURRENT_LOCAL_SETTINGS)
        else:
            local_settings = {}
        if project_path:
            local_settings["project_path"] = project_path
            app.storage.user[CURRENT_LOCAL_SETTINGS] = json.dumps(local_settings)
    except Exception as e:
        ui.notify(f"storage update for local settings failed: {e}", type="negative")


def storage_update_execution(execution_id):
    try:
        execution = db.get_document_by_id(
            document_id=execution_id, collection=db.collection_executions
        )
        version_names = odtp_utils.get_version_names_for_execution(execution)
        current_execution = {
            "execution_id": execution_id,
            "title": execution.get("title"),
            "timestamp": execution.get("start_timestamp").strftime(
                "%m/%d/%Y, %H:%M:%S"
            ),
            "versions": execution.get("component_versions"),
            "step_names": version_names,
            "steps": [str(step_id) for step_id in execution.get("steps")],
        }
        current_execution_as_json = json.dumps(current_execution)
        app.storage.user[CURRENT_EXECUTION] = current_execution_as_json
    except Exception as e:
        ui.notify(f"storage update for execution failed: {e}", type="negative")


def storage_update_add_execution_init(
    name, version_tuples, digital_twin_id, form_state, parameter_count
):
    if form_state == FORM_STATE_START:
        version_ids = [version_tuple[0] for version_tuple in version_tuples]
        step_names = [version_tuple[2] for version_tuple in version_tuples]
        add_execution = {
            "name": name,
            "versions": version_ids,
            "step_names": step_names,
            "digital_twin_id": digital_twin_id,
            "step_count": len(version_ids),
            "parameter_count": str(parameter_count),
            "current_step_nr": "0",
            "parameters": [],
            "ports": [],
        }
        app.storage.user[NEW_EXECUTION] = json.dumps(add_execution)


def storage_update_add_execution_step(
    parameter_keys,
    parameter_values,
    ports_mapping_inputs,
):

    new_execution = get_active_object_from_storage(NEW_EXECUTION)
    if not len(parameter_keys) == len(parameter_values):
        raise ODTPFormValidationException("paramter key and value count must be equal")
    parameters_step = {}
    ports_step = []
    for key, value in zip(parameter_keys, parameter_values):
        parameters_step[key] = value
    ports_step = parse.parse_ports(ports_mapping_inputs)
    new_execution["parameters"].append(parameters_step)
    new_execution["ports"].append(ports_step)
    current_step_nr = int(new_execution["current_step_nr"])
    current_step_nr += 1
    new_execution["current_step_nr"] = str(current_step_nr)
    app.storage.user[NEW_EXECUTION] = json.dumps(new_execution)


def storage_update_add_component(repo_link):
    latest_commit = odtp_git.check_commit_for_repo(repo_link)
    repo_info = odtp_git.get_github_repo_info(repo_link)
    add_component = {
        "repo_link": repo_link,
        "latest_commit": latest_commit,
        "repo_info": repo_info,
    }
    try:
        app.storage.user[NEW_COMPONENT] = json.dumps(add_component)
    except Exception as e:
        ui.notify(f"storage update for new component failed: {e}", type="negative")


def storage_update_user(user_id):
    try:
        user = db.get_document_by_id(
            document_id=user_id, collection=db.collection_users
        )
        current_user = json.dumps(
            {"user_id": user_id, "display_name": user.get("displayName")}
        )
        app.storage.user[CURRENT_USER] = current_user
    except Exception as e:
        ui.notify(f"{CURRENT_USER} could not be set. Exception {e} occured")


def get_active_object_from_storage(object_name):
    try:
        object = app.storage.user.get(object_name)
        if object:
            return json.loads(object)
    except Exception as e:
        ui.notify(
            f"'{object_name}' could not be retrieved from storage. Exception occured: {e}",
            type="negative",
        )


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
        ui.notify(
            f"storage update for {CURRENT_COMPONENT} failed: {e}", type="negative"
        )


def storage_run_selection(execution_id, repo_url, commit_hash):
    run_selection = {
        "execution_id": execution_id,
        "repo_url": repo_url,
        "commit_hash": commit_hash,
    }
    if not run_selection:
        app.storage.user["run_selection"] = "None"
    try:
        app.storage.user["run_selection"] = json.dumps(run_selection)
    except Exception as e:
        ui.notify(f"storage update for run selection failed: {e}", type="negative")
