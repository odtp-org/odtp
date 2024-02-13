from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db


def content() -> None:
    with ui.right_drawer().style("background-color: #ebf1fa").props(
        "bordered width=500"
    ) as right_drawer:
        ui_workarea()
    ui.markdown(
        """
        # Manage Users 
        """
    )
    content = {"Select User": ui_users_select(), "Add User": ui_add_user()}
    with ui.tabs() as tabs:
        for title in content:
            ui.tab(title)
    with ui.tab_panels(tabs).classes("w-full") as panels:
        for title, text in content.items():
            with ui.tab_panel(title):
                ui.label(text)


@ui.refreshable
def ui_users_select() -> None:
    ui.markdown(
        """
        #### Select your user
        """
    )
    try:
        users = db.get_collection(db.collection_users)
        user_options = {str(user["_id"]): user["displayName"] for user in users}
        ui.select(
            user_options,
            label="user",
            on_change=lambda e: store_selected_user(str(e.value)),
            with_input=True,
        ).props("size=80")
    except Exception as e:
        ui.notify(
            f"User selection could not be loaded. An Exception occured: {e}",
            type="negative",
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
            validation={"Can not be empty": lambda value: len(value.strip()) != 0},
        )

        github_input = ui.input(
            label="Github User",
            placeholder="github username",
            validation={"Can not be empty": lambda value: len(value.strip()) != 0},
        )

        email_input = ui.input(
            label="Email",
            placeholder="email",
            validation={
                "Not a valid email, should contain @": lambda value: "@" in value
            },
        )
        ui.button(
            "Add new user",
            on_click=lambda: add_user(
                name=name_input.value,
                github=github_input.value,
                email=email_input.value,
            ),
        )


@ui.refreshable
def ui_workarea():
    ui.markdown(
        """
        ### Work Area
        """
    )
    try:
        user = storage.get_active_object_from_storage("user")
        if user:
            ui.markdown(
                f"""
                #### User
                - user: {user.get("display_name")}

                #### Actions
                - [manage digital twins](/digital-twins)
                """
            )
            ui.button(
                "Reset work area", color="grey", on_click=lambda: app_storage_reset()
            )
        else:
            ui.markdown(
                f"""
                #### Actions
                - Add a user
                - Select a user
                """
            )
    except Exception as e:
        ui.notify(
            f"Workarea could not be retrieved. An Exception occured: {e}",
            type="negative",
        )


def store_selected_user(value):
    try:
        storage.storage_update_user(user_id=value)
        storage.app_storage_reset("digital_twin")
        print(app.storage.user.keys())
    except Exception as e:
        ui.notify(
            f"Selected user could not be stored. An Exception occured: {e}",
            type="negative",
        )
    finally:
        ui_workarea.refresh()


def add_user(name, github, email):
    if name and github and email:
        try:
            user_id = db.add_user(name=name, github=github, email=email)
            ui.notify(f"A user with id {user_id} has been created", type="positive")
        except Exception as e:
            ui.notify(
                f"The user could not be added in the database. An Exception occured: {e}",
                type="negative",
            )
        finally:
            ui_users_select.refresh()
            ui_add_user.refresh()
    else:
        ui.notify(f"A user can only be added once the form is filled", type="negative")


def app_storage_reset():
    try:
        storage.app_storage_reset("user")
    except Exception as e:
        ui.notify(
            f"Work area could not be reset. An Exception occured: {e}", type="negative"
        )
    finally:
        ui_workarea.refresh()
