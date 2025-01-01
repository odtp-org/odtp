import logging

from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.page_digital_twins.table as table
import odtp.dashboard.page_digital_twins.select as select
import odtp.dashboard.page_digital_twins.add as add
import odtp.dashboard.page_digital_twins.workarea as workarea
import odtp.mongodb.db as db

TAB_SELECT = "Select a digital twin"
TAB_ADD = "Add a new digital twin"


log = logging.getLogger("__name__")


def content() -> None:
    current_user = storage.get_active_object_from_storage(storage.CURRENT_USER)
    ui_workarea(current_user)
    if current_user:
        ui_tabs(current_user)


@ui.refreshable
def ui_tabs(current_user):
    with ui.tabs() as tabs:
        select = ui.tab(TAB_SELECT)
        add = ui.tab(TAB_ADD)
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(select):
            ui_digital_twin_select(current_user)
            ui_digital_twins_table(current_user)
        with ui.tab_panel(add):
            ui_add_digital_twin(current_user)


@ui.refreshable
def ui_digital_twins_table(current_user):
    try:
        current_digital_twin = storage.get_active_object_from_storage(
            (storage.CURRENT_DIGITAL_TWIN)
        )
        digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=current_user["user_id"],
            ref_name=db.collection_digital_twins,
        )
        table.ui_table_layout(
            digital_twins=digital_twins
        )
    except Exception as e:
        log.exception(
            f"Digital Twin table could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_digital_twin_select(current_user) -> None:
    try:
        current_digital_twin = storage.get_active_object_from_storage(
            (storage.CURRENT_DIGITAL_TWIN)
        )
        user_id = current_user["user_id"]
        digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=user_id,
            ref_name=db.collection_digital_twins,
        )
        select.digital_twin_select_form(
            current_user=current_user,
            current_digital_twin=current_digital_twin,
            digital_twins=digital_twins,
        )
    except Exception as e:
        log.exception(
            f"Digital Twin Selection could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_add_digital_twin(current_user):
    try:
        add.add_digital_twin_form(current_user)
    except Exception as e:
        log.exception(
            f"Digital Twin Selection could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_workarea(current_user):
    try:
        user_workdir = storage.get_value_from_storage_for_key(storage.CURRENT_USER_WORKDIR)
        current_digital_twin = storage.get_active_object_from_storage(
            storage.CURRENT_DIGITAL_TWIN
        )
        workarea.ui_workarea_form(
            current_user=current_user,
            current_digital_twin=current_digital_twin,
            user_workdir=user_workdir
        )
    except Exception as e:
        log.exception(f"Work area could not be loaded. An Exception happened: {e}")
