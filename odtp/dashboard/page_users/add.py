import logging
from nicegui import ui
import odtp.mongodb.db as db


log = logging.getLogger("__name__")


def ui_user_add_form():
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
                "Should be at least 6 characters long": lambda value: len(value.strip())
                >= 6
            },
        )
        github_input = ui.input(
            label="Github User",
            placeholder="github username",
            validation={
                "Should be at least 6 characters long": lambda value: len(value.strip())
                >= 6
            },
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
            on_click=lambda: add_user(
                name_input=name_input,
                github_input=github_input,
                email_input=email_input,
            ),
            icon="add",
        )


def add_user(name_input, github_input, email_input):
    if (
        not name_input.validate()
        or not github_input.validate()
        or not email_input.validate()
    ):
        ui.notify(
            "Fill in the form correctly before you can add a new user", type="negative"
        )
        return
    try:
        user_id = db.add_user(
            name=name_input.value,
            github=github_input.value,
            email=email_input.value,
        )
        ui.notify(f"A user with id {user_id} has been created", type="positive")
    except Exception as e:
        ui.notify(
            f"The user could not be added in the database. An Exception occurred: {e}",
            type="negative",
        )
        log.exception("The user could not be added in the database. An Exception occurred: {e}")
    else:
        user_id = str(user_id)
        from odtp.dashboard.page_users.select import store_selected_user
        store_selected_user(user_id)
        from odtp.dashboard.page_users.main import ui_users_select, ui_add_user, ui_tabs
        ui_users_select.refresh()
        ui_add_user.refresh()
        ui_tabs.refresh()

