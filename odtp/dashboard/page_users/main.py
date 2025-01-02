import logging
from nicegui import app, ui
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.page_users.select as select
import odtp.dashboard.page_users.add as add
import odtp.dashboard.page_users.workarea as workarea
import odtp.dashboard.page_users.storage as storage

log = logging.getLogger("__name__")


def content() -> None:
    ui_workarea()
    ui_tabs()


@ui.refreshable
def ui_tabs():
    with ui.tabs() as tabs:
        select = ui.tab("Select User")
        add = ui.tab("Add User")
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(select):
            ui_users_select()
        with ui.tab_panel(add):
            ui_add_user()


@ui.refreshable
def ui_users_select():
    try:
        select.SelectUserForm()
    except Exception as e:
        log.exception(e)


@ui.refreshable
def ui_add_user():
    try:
        add.UserAddForm()
    except Exception as e:
        log.exception(e)


@ui.refreshable
def ui_workarea():
    try:
        workarea.workarea()
    except Exception as e:
        log.exception(e)
