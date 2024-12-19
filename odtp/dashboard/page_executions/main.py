import logging

from nicegui import ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db
import odtp.dashboard.page_executions.table as table
import odtp.dashboard.page_executions.detail as detail
import odtp.dashboard.page_executions.add as add
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
            manage = ui.tab("Manage execution")
            select = ui.tab("Execution Details")
            add = ui.tab("Add an execution")
        with ui.tab_panels(tabs, value=manage).classes("w-full") as panels:
            with ui.tab_panel(select):
                ui_execution_select(current_digital_twin)
            with ui.tab_panel(add):
                ui_add_execution(current_digital_twin)
            with ui.tab_panel(manage):
                ui_executions_table(current_digital_twin)
    except Exception as e:
        log.exception(f"Execution Tabs could not be loaded. An Exception occurred: {e}")


def ui_add_execution(current_digital_twin):
    add.ExecutionForm(current_digital_twin["digital_twin_id"])


@ui.refreshable
def ui_execution_select(current_digital_twin) -> None:
    detail.ExecutionDisplay(digital_twin_id=current_digital_twin["digital_twin_id"])


@ui.refreshable
def ui_executions_table(current_digital_twin):
    table.ExecutionTable(digital_twin_id=current_digital_twin["digital_twin_id"])

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
