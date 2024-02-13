import json

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db


def app_storage_is_set(value):
    storage_entry_for_value = app.storage.user.get(value)
    if storage_entry_for_value == "None" or not storage_entry_for_value:
        return False
    return True


def storage_update_digital_twin(digital_twin_id):
    if not digital_twin_id:
        app.storage.user["digital_twin"] = "None"
    try:
        digital_twin = db.get_document_by_id(
            document_id=digital_twin_id, collection=db.collection_digital_twins
        )
        current_digital_twin = json.dumps(
            {"digital_twin_id": digital_twin_id, "name": digital_twin.get("name")}
        )
        app.storage.user["digital_twin"] = current_digital_twin
    except Exception as e:
        ui.notify(f"storage update for digital twin failed: {e}", type="negative")


def storage_update_docker(image_name, instance_name):
    docker_settings = {
        "image_name": image_name,
        "instance_name": instance_name,
    }
    if not docker_settings:
        app.storage.user["docker_settings"] = "None"
    try:
        app.storage.user["docker_settings"] = json.dumps(docker_settings)
    except Exception as e:
        ui.notify(f"storage update for docker failed: {e}", type="negative")


def storage_update_local_settings(project_folder_name=None, env_file_name=None):
    local_settings = get_active_object_from_storage("local_settings")
    helpers.create_project_folder(project_folder_name=project_folder_name)
    if project_folder_name:
        local_settings["project_path"] = helpers.get_workdir_path(project_folder_name)
    if env_file_name:
        local_settings["env_file_path"] = helpers.get_workdir_path(env_file_name)
    try:
        app.storage.user["local_settings"] = json.dumps(local_settings)
    except Exception as e:
        ui.notify(f"storage update for local settings failed: {e}", type="negative")


def storage_update_execution(execution_id):
    if not execution_id:
        app.storage.user["execution"] = "None"
    try:
        execution = db.get_document_by_id(
            document_id=execution_id, collection=db.collection_executions
        )
        workflow = execution["workflowSchema"]["components"]
        workflow_cleaned = []
        for item_dict in workflow:
            step = {}
            for k, v in item_dict.items():
                print(f"k: {k}, v {v}")
                step[k] = str(v)
            workflow_cleaned.append(step)
        current_execution = {
            "execution_id": execution_id,
            "title": execution.get("title"),
            "workflow": workflow_cleaned,
        }
        print(current_execution)
        current_execution_as_json = json.dumps(current_execution)
        app.storage.user["execution"] = current_execution_as_json
    except Exception as e:
        ui.notify(f"storage update for execution failed: {e}", type="negative")


def storage_update_user(user_id):
    try:
        user = db.get_document_by_id(
            document_id=user_id, collection=db.collection_users
        )
        current_user = json.dumps(
            {"user_id": user_id, "display_name": user.get("displayName")}
        )
        app.storage.user["user"] = current_user
    except Exception as e:
        raise


def get_active_object_from_storage(object_name):
    try:
        object = app.storage.user.get(object_name)
        if app_storage_is_set(object_name) and object:
            return json.loads(object)
    except Exception as e:
        ui.notify(
            f"'{object_name}' could not be retrieved from storage. Exception occured: {e}",
            type="negative",
        )


def storage_update_component(component_id):
    if not component_id:
        app.storage.user["component_id"] = "None"
    try:
        component = db.get_document_by_id(
            document_id=component_id, collection=db.collection_components
        )
        current_component = json.dumps(
            {
                "component_id": component_id,
                "name": component.get("componentName"),
                "repo_link": component.get("repoLink"),
            }
        )
        app.storage.user["component"] = current_component
    except Exception as e:
        ui.notify(f"storage update for component failed: {e}", type="negative")


def storage_update_version(version_id, component_id, replace):
    if not component_id:
        ui.notify(f"storage update for version failed: component_id is missing")
        return
    if app_storage_is_set("component") and version_id:
        component = json.loads(app.storage.user.get("component"))
        if not app_storage_is_set("components"):
            components = []
        else:
            components = json.loads(app.storage.user.get("components"))
        try:
            version = db.get_document_by_id(
                document_id=version_id, collection=db.collection_versions
            )
            component["version"] = {
                "version_id": version_id,
                "commit_hash": version.get("commitHash"),
                "component_version": version.get("component_version"),
                "odtp_version": version.get("odtp_version"),
            }
            if replace:
                components = [
                    c
                    for c in components
                    if c["component_id"] != component["component_id"]
                ]
            components.append(component)
            app.storage.user["components"] = json.dumps(components)
        except Exception as e:
            ui.notify(f"storage update for version failed: {e}", type="negative")


def storage_run_selection(repo_url, commit_hash):
    run_selection = {
        "repo_url": repo_url,
        "commit_hash": commit_hash,
    }
    if not run_selection:
        app.storage.user["run_selection"] = "None"
    try:
        app.storage.user["run_selection"] = json.dumps(run_selection)
    except Exception as e:
        ui.notify(f"storage update for run selection failed: {e}", type="negative")


def app_storage_reset(object_name):
    if app_storage_is_set(object_name):
        app.storage.user[object_name] = "None"
