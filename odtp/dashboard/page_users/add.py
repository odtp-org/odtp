import logging
from nicegui import ui, app
import odtp.mongodb.db as db
import odtp.dashboard.page_users.workdir as workdir
import odtp.dashboard.page_users.storage as storage
import odtp.dashboard.page_users.validation as validation


log = logging.getLogger("__name__")

class UserAddForm:
    def __init__(self):
        self.user_name = None
        self.user_id = None
        self.user_path = None
        self.build_form()

    def build_form(self):
        ui.markdown(
            """
            #### Add new user
            if you are not registered yet: create a new user as a first step.
            """
        )
        with ui.row():
            name_input = ui.input(
                label="Name",
                placeholder="name",
                validation={
                    "Username must be unique": lambda value: validation.validate_user_name_unique(
                    value.strip()
                )},
            )
            github_input = ui.input(
                label="Github User",
                placeholder="github username",
                validation={
                    "Not a github username": lambda value: validation.validate_github_user_name(
                    value.strip()
                )},
            )
            email_input = ui.input(
                label="Email",
                placeholder="email",
                validation={
                    "Not a valid email, should contain @ and have at least 6 characters": lambda value: "@"
                    in value
                    and len(value.strip()) >= 6
                },
            )
            ui.button(
                "Add new user",
                on_click=lambda: self.action_db_add_user(
                    name_input=name_input,
                    github_input=github_input,
                    email_input=email_input,
                ),
                icon="add",
            )

    def action_db_add_user(self, name_input, github_input, email_input):
        if (
            not name_input.validate()
            or not github_input.validate()
            or not email_input.validate()
        ):
            ui.notify(
                "Fill in the form correctly before you can add a new user", type="negative"
            )
            return
        self.user_name = name_input.value
        self.make_workdir()
        user_id = db.add_user(
            name=self.user_name,
            github=github_input.value,
            email=email_input.value,
        )
        self.user_id = str(user_id)
        self.storage_set_current_user()
        ui.notify(f"A user with id {self.user_name} with workdir {self.workdir} has been created", type="positive")
        self.refresh_page()

    def make_workdir(self):
        self.workdir = workdir.make_workdir_for_user_name(self.user_name)

    def storage_set_current_user(self):
        storage.storage_set_current_user(user_id=self.user_id, user_name=self.user_name, workdir=self.workdir)

    def refresh_page(self):
        from odtp.dashboard.page_users.main import ui_users_select, ui_add_user, ui_tabs, ui_workarea
        ui_users_select.refresh()
        ui_add_user.refresh()
        ui_workarea.refresh()
        ui_tabs.refresh()
