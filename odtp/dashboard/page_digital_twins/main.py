import logging
from nicegui import ui
import odtp.dashboard.page_digital_twins.table as table
import odtp.dashboard.page_digital_twins.select as select
import odtp.dashboard.page_digital_twins.add as add
import odtp.dashboard.page_digital_twins.storage as storage
import odtp.dashboard.page_digital_twins.workarea as workarea

log = logging.getLogger("__name__")


def content() -> None:
    current_user = storage.get_current_user_from_storage()
    ui_workarea(current_user)
    ui_tabs(current_user)


@ui.refreshable
def ui_tabs(current_user):
    with ui.tabs() as tabs:
        manage = ui.tab("Manage digital twins")
        select = ui.tab("Select digital twin")
        add = ui.tab("Add digital twin")
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(manage):
            ui_digital_twins_manage(current_user)
        with ui.tab_panel(select):
            ui_digital_twin_select(current_user)
        with ui.tab_panel(add):
            ui_add_digital_twin(current_user)


@ui.refreshable
def ui_digital_twins_manage(current_user):
    try:
        table.DigitalTwinTable(current_user)
    except Exception as e:
        log.exception(
            f"Digital Twin table could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_digital_twin_select(current_user) -> None:
    try:
        select.SelectDigitalTwinForm(current_user)
    except Exception as e:
        log.exception(
            f"Digital Twin Selection could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_add_digital_twin(current_user):
    try:
        add.DigitalTwinAddForm(current_user)
    except Exception as e:
        log.exception(
            f"Digital Twin Add Form could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_workarea(current_user):
    try:
        workarea.ui_workarea_form(current_user=current_user)
    except Exception as e:
        log.exception(f"Work area could not be loaded. An Exception happened: {e}")
