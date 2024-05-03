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
CURRENT_USER_WORKDIR = "user_workdir"
CURRENT_PROJECT_PATH = "project_path"


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
