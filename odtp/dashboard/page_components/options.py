import json
import logging

from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.validators as validators
import odtp.helpers.git as odtp_git
import odtp.mongodb.db as db

log = logging.getLogger(__name__)


def ui_select_form(current_component, components):
   with ui.column().classes("w-full"):
        if not components:
            ui_theme.ui_no_items_yet("Components")
            return
        ui.markdown(
            """
            #### Component Options
            - compare github and ODTP
            - add versions from github
            """
        )
        if current_component:
            value = current_component["component_id"]
        else:
            value = ""
        components_options = {
            str(component["_id"]): f"{component.get('componentName')}"
            for component in components
        }
        if components:
            ui.select(
                components_options,
                value=value,
                on_change=lambda e: store_selected_component(str(e.value)),
                label="component",
                with_input=True,
            ).classes("w-1/2")


def ui_form_version_add(current_component):   
    repo_info = current_component["repo_info"]
    versions_in_db = db.get_sub_collection_items(
        collection=db.collection_components,
        sub_collection=db.collection_versions,
        item_id=current_component["component_id"],
        ref_name=db.collection_versions,
    )
    component_versions_in_db = [
        item.get("component_version") for item in versions_in_db
    ]
    version_selector = {
        (item["name"], item["commit"]): item["name"]
        for item in repo_info.get("tagged_versions")
        if item["name"] not in component_versions_in_db
    }
    ui.markdown(
        """
        ##### Add Version
        add any tagged version from github that is not on ODTP yet
        """
    )     
    if not version_selector:
        ui.markdown(
            """
            All available versions on github have been already submitted to ODTP.
            """
        ).classes("text-lg")
        return
    component_version_input = ui.select(
        options=version_selector,
        validation={
            f"A version selection is required": lambda value: validators.validate_required_input(
                value
            )
        },
    ).classes("w-1/4")
    with ui.row():
        ports_inputs = []
        for i in range(3):
            port_input = ui.input(
                label="Port",
                placeholder="8052",
                validation={
                    f"This is not a valid port": lambda value: validators.validate_port_input(
                        value
                    )
                },
            ).classes("w-1/4")
            ports_inputs.append(port_input)
    with ui.row():
        ui.button(
            "Register version",
            on_click=lambda: register_new_version(
                component_version_input=component_version_input,
                ports_inputs=ports_inputs,
                current_component=current_component,
            ),
        )


def store_selected_component(value):
    try:
        if not ui_theme.new_value_selected_in_ui_select(value):
            return
        component_id = value
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
        app.storage.user[storage.CURRENT_COMPONENT] = current_component
    except Exception as e:
        log.exception(
            f"Selected component could not be stored. An Exception occurred: {e}"
        )
    else:
        from odtp.dashboard.page_components.main import (ui_workarea, ui_component_show, ui_version_add)
        ui_workarea.refresh()
        ui_component_show.refresh()
        ui_version_add.refresh()


def register_new_version(
    component_version_input,
    ports_inputs,
    current_component,
):
    if not component_version_input.validate():
        ui.notify(
            "Fill in the form correctly before you can add a new version",
            type="negative",
        )
        return
    try:
        ports = [port_input.value for port_input in ports_inputs if port_input.value]
        component_id, version_id = db.add_component_version(
            component_name=current_component.get("name"),
            repo_info=current_component.get("repo_info"),
            component_version=component_version_input.value[0],
            type=current_component.get("type"),
            ports=ports,
        )
        ui.notify(
            f"Component version {component_id} / {version_id} has been added",
            type="positive",
        )
    except Exception as e:
        ui.notify(
            f"The component and version could not be added. An Exception occurred: {e}",
            type="negative",
        )
        log.exception(f"The component and version could not be added. An Exception occurred: {e}")
    else:
        from odtp.dashboard.page_components.main import (
            ui_component_add, ui_component_select, ui_component_show, ui_version_add, ui_components_list
        )
        ui_components_list.refresh()
        ui_component_show.refresh()
        ui_component_select.refresh()
        ui_component_add.refresh()
        ui_version_add.refresh()
