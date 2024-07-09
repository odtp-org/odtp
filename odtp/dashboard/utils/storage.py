import json
import logging

from nicegui import app, ui
import odtp.mongodb.db as db


CURRENT_USER = "user"
AUTH_USER_KEYCLOAK = "auth_user"
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
            f"""During reset storage keep with keys {keys} en exception {e} occurred. 
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


def storage_update_user_keycloak(user_data):
    try:
        sub = user_data.get("sub")
        if sub:
            user_id = db.get_document_id_by_field_value("sub", sub, "users")
            user_component = json.dumps(
            {
                "sub": user_data.get("sub"),
                "display_name": user_data.get("preferred_username"),
                "repo_link": user_data.get("Github_repo"),
                "email": user_data.get("email"),
                "user_id:":user_id 
                }
            )
        app.storage.user[AUTH_USER_KEYCLOAK] = user_component  
    except Exception as e:
        ui.notify(
            f"storage update for {AUTH_USER_KEYCLOAK} failed: {e}", type="negative"
        )  


def reset_all () -> None: 
    app.storage.clear()