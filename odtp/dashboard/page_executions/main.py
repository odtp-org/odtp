import logging
from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.page_executions.table as table
import odtp.dashboard.page_executions.detail as detail
import odtp.dashboard.page_executions.add as add
import odtp.dashboard.page_executions.workarea as workarea
import odtp.dashboard.page_executions.storage as storage

log = logging.getLogger("__name__")


def content() -> None:
    try:
        current_user = storage.get_current_user_from_storage()
        current_digital_twin = storage.storage_get_current_digital_twin()
        components = db.get_collection(collection=db.collection_components)
        ui_workarea(
            current_digital_twin=current_digital_twin,
            current_user=current_user,
            components=components,
        )
        if not current_digital_twin or not current_user:
            return
        ui_tabs(current_digital_twin, current_user)
    except Exception as e:
        log.exception(f"Execution Tabs could not be loaded. An Exception occurred: {e}")


@ui.refreshable
def ui_tabs(current_digital_twin, current_user):
    try:
        with ui.tabs() as tabs:
            manage = ui.tab("Manage execution")
            select = ui.tab("Execution Run")
            add = ui.tab("Add an execution")
        with ui.tab_panels(tabs, value=select).classes("w-full") as panels:
            with ui.tab_panel(select):
                ui_execution_select(current_user, current_digital_twin)
            with ui.tab_panel(add):
                ui_add_execution(current_digital_twin)
            with ui.tab_panel(manage):
                ui_executions_table(current_digital_twin)
    except Exception as e:
        log.exception(f"Execution Tabs could not be loaded. An Exception occurred: {e}")


def ui_add_execution(current_digital_twin):
    try:
        add.ExecutionForm(current_digital_twin["digital_twin_id"])
    except Exception as e:
        log.exception(f"Execution Add form could not be loaded. An Exception occurred: {e}")


@ui.refreshable
def ui_execution_select(current_user, current_digital_twin):
    try:
        with ui.dialog().props("full-width") as dialog, ui.card():
            result = ui.markdown()
            ui.button("Close", on_click=dialog.close)
        detail.ExecutionDisplay(current_user, current_digital_twin, dialog, result)
    except Exception as e:
        log.exception(f"Execution Select form could not be loaded. An Exception occurred: {e}")


@ui.refreshable
def ui_executions_table(current_digital_twin):
    try:
        table.ExecutionTable(digital_twin_id=current_digital_twin["digital_twin_id"])
    except Exception as e:
        log.exception(f"Execution table could not be loaded. An Exception occurred: {e}")


@ui.refreshable
def ui_workarea(current_digital_twin, current_user, components):
    try:
        workarea.ui_workarea_form(
            current_digital_twin=current_digital_twin,
            current_user=current_user,
            components=components,
        )
    except Exception as e:
        log.exception(
            f"Workarea could not be loaded. An Exception occurred: {e}"
        )
