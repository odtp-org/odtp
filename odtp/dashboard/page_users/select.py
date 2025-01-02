import json
import logging
from nicegui import ui, app
import odtp.mongodb.db as db
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db
import odtp.dashboard.page_users.workdir as workdir
import odtp.dashboard.page_users.storage as storage

log = logging.getLogger("__name__")


class SelectUserForm():
    def __init__(self):
        self.user_id = ""
        self.user_name = None
        self.workdir = None
        self.user_options = None
        self.get_user_options()
        self.build_form()

    def get_user_options(self):
        self.users = db.get_collection(db.collection_users)
        if not self.users:
            return
        self.user_options = { str(user["_id"]): user["displayName"] for user in self.users }

    def get_current_user_from_storage(self):
        current_user = storage.storage_get_current_user()
        if not current_user:
            return
        self.user_id = current_user["user_id"]
        self.user_name = current_user["user_name"]
        self.workdir = current_user["workdir"]

    def ui_no_users_yet(self):
        if not self.users:
            ui_theme.ui_no_items_yet("users")

    @ui.refreshable
    def build_form(self):
        self.ui_no_users_yet()
        self.get_current_user_from_storage()
        if not self.user_options:
            return
        self.ui_select_form()

    def ui_select_form(self):
        ui.select(
            self.user_options,
            value=self.user_id,
            label="user",
            on_change=lambda e: self.store_selected_user(str(e.value)),
            with_input=True,
        ).props("size=80")

    def storage_set_current_user(self):
        storage.storage_set_current_user(user_id=self.user_id, user_name=self.user_name, workdir=self.workdir)

    def get_user_from_db(self):
        user = db.get_document_by_id(
            document_id=self.user_id, collection=db.collection_users
        )
        self.user_name = user.get("displayName")

    def get_workdir(self):
        self.workdir = workdir.get_workdir_for_user_name(self.user_name)

    def store_selected_user(self, value):
        if not ui_theme.new_value_selected_in_ui_select(value):
            return
        self.user_id = value
        self.get_user_from_db()
        self.get_workdir()
        self.storage_set_current_user()
        self.build_form.refresh()
        from odtp.dashboard.page_users.main import ui_workarea
        ui_workarea.refresh()

