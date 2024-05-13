from nicegui import ui, app
import json
import logging

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db
from odtp.dashboard.utils.file_picker import local_file_picker
from odtp.helpers.settings import ODTP_PATH


def content() -> None:  
    ui.markdown(
        """
        # Manage Users 
        """
    )     
    with ui.right_drawer().classes("bg-slate-50").props(
        "bordered width=500"
    ) as right_drawer:
        ui_workarea()
    with ui.tabs().classes("w-full") as tabs:
        select = ui.tab("Select User")
        add = ui.tab("Add User")
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(select):
            ui_users_select()
        with ui.tab_panel(add):
            ui_add_user()


@ui.refreshable
def ui_users_select() -> None:
    ui.markdown(
        """
        #### Select your user
        """
    )
    try:
        users = db.get_collection(db.collection_users)
        if not users:
            ui_theme.ui_no_items_yet("users")
            return
        user_options = {str(user["_id"]): user["displayName"] for user in users}
        current_user = storage.get_active_object_from_storage((storage.CURRENT_USER))
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
    except Exception as e:
        logging.error(
            f"User selection could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_add_user():
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
            validation={"Should be at least 6 characters long": lambda value: len(value.strip()) >= 6},
        )

        github_input = ui.input(
            label="Github User",
            placeholder="github username",
            validation={"Should be at least 6 characters long": lambda value: len(value.strip()) >= 6},
        )

        email_input = ui.input(
            label="Email",
            placeholder="email",
            validation={"Not a valid email, should contain @ and have at least 6 characters": 
                        lambda value: "@" in value and len(value.strip()) >= 6},
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


@ui.refreshable
def ui_workarea():
    ui.markdown(
        """
        ### Work Area
        """
    )
    try:
        user = storage.get_active_object_from_storage(storage.CURRENT_USER)
        workdir = storage.get_value_from_storage_for_key(storage.CURRENT_USER_WORKDIR)
        if not workdir:
            workdir = ODTP_PATH
        if not user:
            ui.markdown(
                f"""
                #### Actions
                - Add a user
                - Select a user
                """
            )
            return            
        ui.markdown(
            f"""
            #### Current Selection
            - **user**: {user.get("display_name")}
            - **work directory**: {workdir}

            ##### Actions

            - add user
            - select user
            """
        )
        ui.button(
            "Manage digital twins",
            on_click=lambda: ui.open(ui_theme.PATH_DIGITAL_TWINS),
            icon="link",
        )
        ui.button(
            "Set Work directory", 
            on_click=pick_workdir, 
            icon="folder"
        )
        ui.button(
            "Set Work directory to default", 
            on_click=set_default_workdir, 
            icon="folder"
        ).props('flat')       
    except Exception as e:
        logging.error(
            f"Workarea could not be retrieved. An Exception occurred: {e}"
        )


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
        logging.error(
            f"Selected user could not be stored. An Exception happened: {e}"
        )
    else:
        storage.reset_storage_keep([storage.CURRENT_USER])
        ui_workarea.refresh()


def add_user(name_input, github_input, email_input):
    if not name_input.validate() or not github_input.validate() or not email_input.validate():
        ui.notify("Fill in the form correctly before you can add a new user", type="negative")
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
    else:
        ui_users_select.refresh()
        ui_add_user.refresh()


async def pick_workdir() -> None:
    try:
        root = ODTP_PATH
        result = await local_file_picker(root, multiple=False)
        if result:
            workdir = result[0]
            app.storage.user[storage.CURRENT_USER_WORKDIR] = workdir
            ui.notify(f"A new user workdir has been set to {workdir}", type="positive")
    except Exception as e:
        logging.error(
            f"Work directory could not be picked: an Exception occurred: {e}"
        )
    else:            
        ui_workarea.refresh()    


def set_default_workdir():
    app.storage.user[storage.CURRENT_USER_WORKDIR] = ODTP_PATH
    ui.notify(f"User workdir has been set to {ODTP_PATH}", type="positive")
    ui_workarea.refresh()
