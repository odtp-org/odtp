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
