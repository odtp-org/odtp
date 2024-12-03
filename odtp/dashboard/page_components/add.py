import json
import logging

from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.validators as validators


import odtp.helpers.git as odtp_git
import odtp.mongodb.db as db
import odtp.mongodb.utils as db_utils


log = logging.getLogger(__name__)


def ui_form_component_add_step1():
    ui.markdown(
        """
        #### Add new Component
        """
    )
    repo_link_input = (
        ui.input(
            label="Enter Repository URL",
            placeholder="repo url",
            validation=lambda value: validators.validate_github_repo(value),
        )
        .without_auto_validation()
        .classes("w-1/2")
    )
    ui.button(
        "Proceed to next step",
        on_click=lambda: store_new_component(
            repo_link_input=repo_link_input,
        ),
    )


def ui_form_component_add_step2(new_component_to_add):
    with ui.row():
        from odtp.dashboard.page_components.info import ui_git_info_show
        ui_git_info_show(component=new_component_to_add)
        with ui.column().classes("w-full"):
            repo_info = new_component_to_add.get("repo_info")
            ui.button(
                "Cancel Component Entry",
                on_click=lambda: cancel_component_entry(),
            )
            version_selector = {
                (item["name"], item["commit"]): item["name"]
                for item in new_component_to_add.get("repo_info").get("tagged_versions")
            }
            component_type_selector = {
                db_utils.COMPONENT_TYPE_EPHERMAL: f"{db_utils.COMPONENT_TYPE_EPHERMAL}: components exits after run",
                db_utils.COMPONENT_TYPE_PERSISTENT: f"{db_utils.COMPONENT_TYPE_PERSISTENT}: component keeps running",
            }
            component_name_input = ui.input(
                value=repo_info.get("name"),
                label="Component name",
                placeholder="component name",
                validation={
                    f"A component name is required": lambda value: validators.validate_required_input(
                        value
                    )
                },
            ).classes("w-2/3")
            component_type_input = ui.select(
                label="component type",
                options=component_type_selector,
                validation={
                    f"A component type nust be selected": lambda value: validators.validate_required_input(
                        value
                    )
                },
            ).classes("w-2/3")
            component_version_input = ui.select(
                label="component version",
                options=version_selector,
                validation={
                    f"A version selection is required": lambda value: validators.validate_required_input(
                        value
                    )
                },
            ).classes("w-1/3")
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
            ui.button(
                "Register component",
                on_click=lambda: register_new_component(
                    component_name_input=component_name_input,
                    component_version_input=component_version_input,
                    component_type_input=component_type_input,
                    ports_inputs=ports_inputs,
                    new_component=new_component_to_add,
                ),
            )


def cancel_component_entry():
    try:
        storage.reset_storage_delete([storage.NEW_COMPONENT])
    except Exception as e:
        log.exception(f"Cancel of component entry failed {e}")
    else:
        from odtp.dashboard.page_components.main import ui_component_add
        ui_component_add.refresh()


def store_new_component(repo_link_input):
    if not repo_link_input.validate():
        return
    repo_link = repo_link_input.value
    try:
        latest_commit = odtp_git.check_commit_for_repo(repo_link)
        repo_info = odtp_git.get_github_repo_info(repo_link)
        add_component = {
            "repo_link": repo_info.get("html_url"),
            "latest_commit": latest_commit,
            "repo_info": repo_info,
        }
        app.storage.user[storage.NEW_COMPONENT] = json.dumps(add_component)
    except Exception as e:
        log.exception(f"storage update for new component failed: {e}")
    else:
        from odtp.dashboard.page_components.main import ui_component_add
        ui_component_add.refresh()


def register_new_component(
    component_name_input,
    component_version_input,
    component_type_input,
    ports_inputs,
    new_component,
):
    if (
        not component_name_input.validate()
        or not component_version_input.validate()
        or not component_type_input.validate()
    ):
        ui.notify(
            "Fill in the form correctly before you can add a new component",
            type="negative",
        )
        return
    try:
        ports = ports = [
            port_input.value for port_input in ports_inputs if port_input.value
        ]
        component_id, version_id = db.add_component_version(
            component_name=component_name_input.value,
            repo_info=new_component.get("repo_info"),
            component_version=component_version_input.value[0],
            type=component_type_input.value,
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
        log.exception(
            f"The component and version {component_name_input} {component_version_input} could not be added. An Exception occurred: {e}"
        )
    else:
        storage.reset_storage_delete([storage.NEW_COMPONENT])
        from odtp.dashboard.page_components.main import (
            ui_component_add, ui_component_select, ui_component_show, ui_version_add, ui_components_list, ui_tabs
        )
        from odtp.dashboard.page_components.options import store_selected_component
        store_selected_component(str(component_id))
        ui_component_add.refresh()
        ui_component_select.refresh()
        ui_component_show.refresh()
        ui_version_add.refresh()
        ui_components_list.refresh()
        ui_tabs.refresh()
