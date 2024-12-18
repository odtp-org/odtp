import logging

from nicegui import ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db
import odtp.dashboard.page_executions.table as table
import odtp.dashboard.page_executions.select as select
import odtp.dashboard.page_executions.add as add
import odtp.dashboard.page_executions.add2 as add2
import odtp.dashboard.page_executions.workarea as workarea

log = logging.getLogger("__name__")


def content() -> None:
    try:
        current_user = storage.get_active_object_from_storage(storage.CURRENT_USER)
        workdir = storage.get_value_from_storage_for_key(storage.CURRENT_USER_WORKDIR)
        current_digital_twin = storage.get_active_object_from_storage(
            storage.CURRENT_DIGITAL_TWIN
        )
        components = db.get_collection(collection=db.collection_components)
        ui_workarea(
            current_digital_twin=current_digital_twin,
            current_user=current_user,
            workdir=workdir,
            components=components,
        )
        if not current_digital_twin or not current_user or not workdir or not components:
            return
        ui_tabs(current_digital_twin=current_digital_twin, workdir=workdir)
    except Exception as e:
        log.exception(f"Execution Tabs could not be loaded. An Exception occurred: {e}")


def parse_key_value_pairs(text: str) -> dict:
    parameters = {}
    for line in text.splitlines():
        line = line.strip()  # Remove whitespace around the line
        if line and "=" in line:  # Check if the line is non-empty and contains '='
            key, value = map(str.strip, line.split('=', 1))  # Split and strip key-value
            parameters[key] = value
    return parameters

@ui.refreshable
def ui_tabs(current_digital_twin, workdir):
    try:
        with ui.tabs() as tabs:
            select = ui.tab("Select an execution")
            add = ui.tab("Add an execution")
            table = ui.tab("Execution table")
        with ui.tab_panels(tabs, value=select).classes("w-full") as panels:
            with ui.tab_panel(select):
                ui_execution_select(current_digital_twin)
                ui_execution_details()
            with ui.tab_panel(add):
                #ui_add_execution(current_digital_twin, workdir)
                ui_add_execution2(current_digital_twin)
            with ui.tab_panel(table):
                ui_executions_table(current_digital_twin)
    except Exception as e:
        log.exception(f"Execution Tabs could not be loaded. An Exception occurred: {e}")


@ui.refreshable
def ui_add_execution(current_digital_twin, workdir):
    try:
        current_execution_to_add = storage.get_active_object_from_storage(
            storage.NEW_EXECUTION
        )
        add.ui_execution_add_form(current_digital_twin, workdir, current_execution_to_add)
    except Exception as e:
        log.exception(f"Execution add form could not be loaded. An Exception occurred: {e}")


def ui_add_execution2(current_digital_twin):
    add2.ExecutionForm(current_digital_twin["digital_twin_id"])


@ui.refreshable
def ui_execution_select(current_digital_twin) -> None:
    try:
        digital_twin_id = current_digital_twin["digital_twin_id"]
        execution_options = helpers.get_execution_select_options(
            digital_twin_id=digital_twin_id
        )
        current_execution = storage.get_active_object_from_storage(
            storage.CURRENT_EXECUTION
        )
        select.ui_select_form(
            execution_options=execution_options,
            current_execution=current_execution,
        )
    except Exception as e:
        log.exception(
            f"Execution selection could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_executions_table(current_digital_twin):
    try:
        executions = db.get_sub_collection_items(
            collection=db.collection_digital_twins,
            sub_collection=db.collection_executions,
            item_id=current_digital_twin["digital_twin_id"],
            ref_name=db.collection_executions,
        )
        table.ui_table_layout(executions)
    except Exception as e:
        log.exception(f"Execution table could not be loaded. An Exception occurred: {e}")


@ui.refreshable
def ui_execution_details():
    try:
        current_execution = storage.get_active_object_from_storage(
            storage.CURRENT_EXECUTION
        )
        if not current_execution:
            return
        execution_title = current_execution.get("title")
        version_tags = current_execution.get("version_tags")
        current_ports = current_execution.get("ports")
        current_parameters = current_execution.get("parameters")
        ui_theme.ui_execution_display(
            execution_title=execution_title,
            version_tags=version_tags,
            ports=current_ports,
            parameters=current_parameters,
        )
    except Exception as e:
        log.exception(
            f"Execution details could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_workarea(current_digital_twin, current_user, workdir, components):
    try:
        current_execution = storage.get_active_object_from_storage(
            storage.CURRENT_EXECUTION
        )
        workarea.ui_workarea_form(
            current_digital_twin=current_digital_twin,
            current_user=current_user,
            workdir=workdir,
            components=components,
            current_execution=current_execution
        )
    except Exception as e:
        log.exception(
            f"Workarea could not be loaded. An Exception occurred: {e}"
        )
