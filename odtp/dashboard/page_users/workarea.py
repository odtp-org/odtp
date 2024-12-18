import logging
import os
from nicegui import ui, app
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.validators as validators
import odtp.dashboard.utils.storage as storage
from odtp.dashboard.utils.file_picker import local_file_picker
from odtp.helpers.settings import ODTP_PATH


log = logging.getLogger("__name__")


def ui_workarea_form(user, workdir):
    try:
        if user:
            user_name = user.get("display_name")
        else:
            user_name = ui_theme.MISSING_VALUE
        with ui.row().classes("w-full"):
            ui.markdown(
                """
                # Manage Users 
                """
            )
        if not user:
            return
        with ui.grid(columns=2):
            with ui.column():
                ui.markdown(
                    f"""
                    #### Current Selection
                    - **user**: {user_name}
                    - **work directory**: {workdir}              
                    """
                )
            with ui.column():
                ui.markdown(
                    f"""
                    #### Actions
                    """
                )
                ui.button(
                    "Manage digital twins",
                    on_click=lambda: ui.open(ui_theme.PATH_DIGITAL_TWINS),
                    icon="link",
                )
                ui.button("Set Work directory", on_click=pick_workdir, icon="folder").props("flat")
                ui.button(
                    "Set Work directory to default",
                    on_click=set_default_workdir,
                    icon="folder",
                ).props("flat")
                with ui.row().classes("flex items-center"):
                    folder_name_input = ui.input(
                        label="Project folder name",
                        placeholder="execution",
                        validation={
                            f"Please provide a folder name does not yet exist in the working directory": lambda value: validators.validate_folder_does_not_exist(
                                value, ODTP_PATH
                            )
                        },
                    )
                    ui.button(
                        "Create new work directory",
                        on_click=lambda: create_workdir(folder_name_input),
                        icon="add",
                    ).props("flat")
    except Exception as e:
        log.exception(f"Workarea could not be loaded: an Exception occurred: {e}")


def create_workdir(folder_name_input):
    try:
        folder_name = folder_name_input.value
        workdir = os.path.join(ODTP_PATH, folder_name)
        os.mkdir(workdir)
        app.storage.user[storage.CURRENT_USER_WORKDIR] = workdir
    except Exception as e:
        ui.notify(
            f"The directory could not be created: {workdir} an exception occurred: {e}",
            type="negative",
        )
        log.exception("The directory could not be created: {workdir} an exception occurred: {e}")
    else:
        ui.notify(
            f"the directory {workdir} has been created and set as working directory",
            type="positive",
        )
        from odtp.dashboard.page_users.main import ui_workarea
        ui_workarea.refresh()


async def pick_workdir() -> None:
    try:
        root = ODTP_PATH
        result = await local_file_picker(root, multiple=False)
        if result:
            workdir = result[0]
            app.storage.user[storage.CURRENT_USER_WORKDIR] = workdir
            ui.notify(f"A new user workdir has been set to {workdir}", type="positive")
    except Exception as e:
        log.exception(f"Work directory could not be picked: an Exception occurred: {e}")
    else:
        from odtp.dashboard.page_users.main import ui_workarea
        ui_workarea.refresh()


def set_default_workdir():
    try:
        app.storage.user[storage.CURRENT_USER_WORKDIR] = ODTP_PATH
    except Exception as e:
        log.exception(f"Default work directory could not be set: an Exception occurred: {e}")
    else:
        ui.notify(f"User workdir has been set to {ODTP_PATH}", type="positive")
        from odtp.dashboard.page_users.main import ui_workarea
        ui_workarea.refresh()
