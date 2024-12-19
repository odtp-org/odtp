import json
import logging
import os.path
import os
import shutil
from slugify import slugify

from nicegui import app, ui
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.validators as validators
import odtp.helpers.environment as odtp_env
import odtp.dashboard.page_run.helpers as rh
from odtp.dashboard.utils.file_picker import local_file_picker

log = logging.getLogger(__name__)


def ui_prepare_folder(workdir, current_run, folder_status, project_path):
    stepper = current_run.get("stepper")
    if stepper and rh.STEPPERS.index(stepper) != rh.STEPPER_SELECT_FOLDER:
        return
    if project_path:
        ui.label(project_path)
        rh.ui_display_folder_status(folder_status)
    if not project_path:
        execution = current_run.get("execution")
        preset_value = slugify(execution["title"])
        if not project_path:
            with ui.row().classes("w-full flex items-center"):
                project_folder_input = ui.input(
                    value=preset_value,
                    label="Project folder name",
                    placeholder="execution",
                    validation={
                        f"Project folder already exists and is not empty": lambda value: validators.validate_folder_does_not_exist(
                            value, workdir
                        )
                    },
                )
                ui.button(
                    "Create new project folder",
                    on_click=lambda: create_folder(workdir, project_folder_input, current_run),
                    icon="add",
                ).props("flat ")
    if folder_status >= rh.FOLDER_EMPTY:
        ready_for_next = True
    else:
        ready_for_next = False
    rh.ui_next_back(current_run, ready_for_next)


async def pick_folder(workdir, current_run) -> None:
    try:
        root = workdir
        result = await local_file_picker(root, multiple=False)
        if not result:
            return
        if result:
            project_path = result[0]
            current_run["project_path"] = project_path
            current_run["stepper"] = rh.STEPPERS[rh.STEPPER_SELECT_FOLDER]
            app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
            ui.notify(
                f"A new project folder has been set {project_path}", type="positive"
            )
    except Exception as e:
        log.exception(f"An exception {e} occurred when picking a parameter file.")
    else:
        from odtp.dashboard.page_run.main import ui_workarea, ui_stepper
        ui_workarea.refresh()
        ui_stepper.refresh()


def create_folder(workdir, folder_name_input, current_run):
    if (
        not folder_name_input.validate()
    ):
        ui.notify(
            "Project folder already exists and is not empty", type="negative"
        )
        return
    try:
        folder_name = folder_name_input.value
        project_path = os.path.join(workdir, folder_name)
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        os.makedirs(project_path)
        current_run["project_path"] = project_path
        current_run["stepper"] = rh.STEPPERS[rh.STEPPER_SELECT_FOLDER]
        app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
        ui.notify(
            f"project directory {project_path} has been created and set as project directory",
            type="positive",
        )
    except Exception as e:
        ui.notify(
            f"The project directory could not be created: {workdir} {folder_name} an exception occurred: {e}",
            type="negative",
        )
        log.exception(f"The project directory could not be created: {workdir} {folder_name} an exception occurred: {e}")
    else:
        from odtp.dashboard.page_run.main import ui_workarea, ui_stepper
        ui_workarea.refresh()
        ui_stepper.refresh()
