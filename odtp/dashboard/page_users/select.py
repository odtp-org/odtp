from nicegui import ui, app
import json
import logging


import odtp.mongodb.db as db
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.storage as storage
from odtp.helpers.settings import ODTP_PATH


log = logging.getLogger("__name__")

def ui_users_select_form(users=None, user_options=None, current_user=None):
    ui.markdown(
        """
        #### Select your user
        """
    )
    if not users:
        ui_theme.ui_no_items_yet("users")
        return
    if current_user:
        value = str(current_user["user_id"])
    else:
        value = ""
    ui.select(
        user_options,
        value=value,
        label="user",
        on_change=lambda e: store_selected_user(str(e.value)),
        with_input=True,
    ).props("size=80")


def store_selected_user(value):
    if not ui_theme.new_value_selected_in_ui_select(value):
        return
    user_id = value
    try:
        user = db.get_document_by_id(
            document_id=user_id, collection=db.collection_users
        )
        current_user = json.dumps(
            {"user_id": user_id, "display_name": user.get("displayName")}
        )
        app.storage.user[storage.CURRENT_USER] = current_user
    except Exception as e:
        log.exception(f"Selected user could not be stored. An Exception happened: {e}")
    else:
        storage.reset_storage_keep([storage.CURRENT_USER])
        app.storage.user[storage.CURRENT_USER_WORKDIR] = ODTP_PATH
        from odtp.dashboard.page_users.main import ui_users_select, ui_workarea
        ui_users_select.refresh()
        ui_workarea.refresh()

