import json
import logging
import os

from nicegui import app, ui, events

import odtp.dashboard.utils.storage as storage
import odtp.mongodb.db as db
from odtp.helpers.settings import ODTP_PATH
import odtp.dashboard.page_users.select as select
import odtp.dashboard.page_users.add as add
import odtp.dashboard.page_users.workarea as workarea


log = logging.getLogger("__name__")

TAB_SELECT = "Select User"
TAB_ADD = "Add User"

def content() -> None:
    ui_workarea()
    ui_tabs()


@ui.refreshable
def ui_tabs():
    with ui.tabs() as tabs:
        select = ui.tab(TAB_SELECT)
        add = ui.tab(TAB_ADD)
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(select):
            ui_users_select()
        with ui.tab_panel(add):
            ui_add_user()


@ui.refreshable
def ui_users_select() -> None:
    try:
        users = db.get_collection(db.collection_users)
        if not users:
            return
        if users:
            user_options = {str(user["_id"]): user["displayName"] for user in users}
        current_user = storage.get_active_object_from_storage((storage.CURRENT_USER))
        select.ui_users_select_form(
            users=users,
            user_options=user_options,
            current_user=current_user,
        )
    except Exception as e:
        log.exception(f"User selection could not be loaded. An Exception occurred: {e}")


@ui.refreshable
def ui_add_user():
    try:
        add.ui_user_add_form()
    except Exception as e:
        log.exception(f"User add form could not be loaded. An Exception occurred: {e}")


@ui.refreshable
def ui_workarea():
    try:
        user = storage.get_active_object_from_storage(storage.CURRENT_USER)
        workdir = storage.get_value_from_storage_for_key(storage.CURRENT_USER_WORKDIR)
        if not workdir:
            workdir = ODTP_PATH
            app.storage.user[storage.CURRENT_USER_WORKDIR] = workdir
        workarea.ui_workarea_form(user=user, workdir=workdir)
    except Exception as e:
        log.exception(f"User workarea not be loaded. An Exception occurred: {e}")