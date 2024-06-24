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

FOLDER_NOT_SET = 0
FOLDER_DOES_NOT_MATCH = 1
FOLDER_EMPTY = 2
FOLDER_PREPARED = 3
FOLDER_HAS_OUTPUT = 4

FOLDER_STATUS = {
    "not_set"
    "no_match",
    "empty",
    "prepared",
    "output",
}

log = logging.getLogger(__name__)


def ui_prepare_folder(dialog, result, workdir, current_run, folder_status):
    stepper = current_run.get("stepper")
    if stepper and rh.STEPPERS.index(stepper) != rh.STEPPER_SELECT_FOLDER:
        return
    project_path = current_run.get("project_path")
    execution = current_run.get("execution")    
    if project_path:
        with ui.row().classes("w-full"):
            ui.markdown(
                f"""
                **project path**: {project_path}
                """
            )      
    with ui.row():
        if folder_status == FOLDER_EMPTY:
            ui.icon("check").classes("text-teal text-lg")
            ui.label("Project folder for the execution run has been selected").classes("text-teal") 
        elif folder_status == FOLDER_NOT_SET:
            ui.icon("clear").classes("text-red text-lg")
            ui.label("Project folder missing: please select one").classes("text-red") 
        elif folder_status == FOLDER_DOES_NOT_MATCH:
            ui.icon("clear").classes("text-red text-lg")
            ui.label("The project folder structure does not match the steps of the execution: choose an empty project folder or create a new project folder").classes("text-red")  
        elif folder_status == FOLDER_PREPARED:
            ui.icon("check").classes("text-teal text-lg")
            ui.label("The execution has been prepared").classes("text-teal")      
        elif folder_status == FOLDER_HAS_OUTPUT:
            ui.icon("check").classes("text-teal text-lg")
            ui.label("The execution has been run").classes("text-teal")   
        folder_matches = folder_status in [
            FOLDER_EMPTY,
            FOLDER_HAS_OUTPUT,
            FOLDER_PREPARED,
        ]
        if folder_matches:
            from odtp.dashboard.page_run.run import build_command
            cli_output_command = build_command(
                cmd="output",
                execution_id=execution["execution_id"],
                project_path=project_path,
            )
        else:
            cli_output_command = None                
    with ui.row().classes("w-full flex items-center"):
        project_folder_input = ui.input(
            value=slugify(execution["title"]),
            label="Project folder name",
            placeholder="execution",
            validation={
                f"Please provide a folder name does not yet exist in the working directory": lambda value: validators.validate_folder_does_not_exist(
                    value, workdir
                )
            },
        )
        ui.button(
            "Create new project folder",
            on_click=lambda: create_folder(workdir, project_folder_input, current_run),
            icon="add",
        ).props("flat ")
    with ui.row().classes("w-full"):
        from odtp.dashboard.page_run.run import run_command
        if cli_output_command:
            ui.button(
                "Show project folder",
                on_click=lambda: run_command(cli_output_command, dialog, result),
                icon="info",
            ).props("no-caps")
    rh.ui_next_back(current_run)


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


def get_folder_status(execution_id, project_path):
    folder_empty = odtp_env.project_folder_is_empty(project_folder=project_path)
    folder_matches_execution = odtp_env.directory_folder_matches_execution(
        project_folder=project_path, execution_id=execution_id
    )
    folder_has_output = odtp_env.directory_has_output(
        execution_id=execution_id, project_folder=project_path
    )
    if folder_empty:
        return FOLDER_EMPTY
    elif folder_matches_execution and not folder_has_output:
        return FOLDER_PREPARED
    elif folder_matches_execution and folder_has_output:
        return FOLDER_HAS_OUTPUT
    else:
        return FOLDER_DOES_NOT_MATCH
