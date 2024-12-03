import json
import logging

from nicegui import app, ui
import odtp.helpers.environment as odtp_env
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme


log = logging.getLogger(__name__)


STEPPERS = (
    "Display Execution",
    "Select Folder",
    "Add Secret Files",
    "Prepare Execution (Build Images)",
    "Run Execution (Run Containers)",
)

STEPPER_DISPLAY_EXECUTION = 0
STEPPER_SELECT_FOLDER = 1
STEPPER_ADD_SECRETS = 2
STEPPER_PREPARE_EXECUTION = 3
STEPPER_RUN_EXECUTION = 4

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


def execution_run_init(digital_twin, execution):
    step_count = len(execution["steps"])
    current_run = {
        "digital_twin_id": digital_twin["digital_twin_id"],
        "digital_twin_name": digital_twin["name"],
        "stepper": STEPPERS[STEPPER_DISPLAY_EXECUTION],
        "secret_files": ["" for i in range(step_count)],
        "project_path": "",
        "execution": execution,
    }
    current_run_as_json = json.dumps(current_run)
    app.storage.user[storage.EXECUTION_RUN] = current_run_as_json
    return current_run


def ui_execution_details(current_run):
    execution = current_run.get("execution")
    execution_title = execution.get("title")
    version_tags = execution.get("version_tags")
    current_ports = execution.get("ports")
    current_parameters = execution.get("parameters")
    ui_theme.ui_execution_display(
        execution_title=execution_title,
        version_tags=version_tags,
        ports=current_ports,
        parameters=current_parameters,
    )
    ui_next_back(current_run, ready_for_next=True)


def ui_next_back(current_run, ready_for_next=False):
    stepper = current_run.get("stepper")
    with ui.grid(columns=1).classes("w-full"):
        with ui.row().classes("w-full"):
            if ready_for_next:
                ui.button(
                    "Next",
                    on_click=lambda: next_step(
                        current_run=current_run,
                    ),
                )
            if stepper and STEPPERS.index(stepper) != STEPPER_DISPLAY_EXECUTION:
                ui.button(
                    "Back",
                    on_click=lambda: run_form_step_back(
                        current_run=current_run,
                    ),
                ).props("flat")


def run_form_step_back(current_run):
    try:
        current_stepper = current_run["stepper"]
        current_stepper_index = STEPPERS.index(current_stepper)
        next_stepper_index = current_stepper_index - 1
        next_stepper = STEPPERS[next_stepper_index]
        current_run["stepper"] = next_stepper
        app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
    except Exception as e:
        log.exception(
            f"Step back failed. An Exception occurred: {e}",
        )
    else:
        from odtp.dashboard.page_run.main import ui_stepper
        ui_stepper.refresh()


def next_step(current_run):
    try:
        current_stepper = current_run["stepper"]
        current_stepper_index = STEPPERS.index(current_stepper)
        next_stepper_index = current_stepper_index + 1
        next_stepper = STEPPERS[next_stepper_index]
        current_run["stepper"] = next_stepper
        app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
    except Exception as e:
        log.exception(
            f"Step back failed. An Exception occurred: {e}",
        )
    else:
        from odtp.dashboard.page_run.main import ui_stepper
        ui_stepper.refresh()

def get_folder_status(execution_id, project_path):
    if not project_path:
        return FOLDER_NOT_SET
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


def ui_display_folder_status(folder_status):
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
            ui.label("Project folder for the execution run has been selected").classes("text-teal")
            ui.icon("check").classes("text-teal text-lg")
            ui.label("The execution has been prepared").classes("text-teal")
        elif folder_status == FOLDER_HAS_OUTPUT:
            ui.icon("check").classes("text-teal text-lg")
            ui.label("Project folder for the execution run has been selected").classes("text-teal")
            ui.icon("check").classes("text-teal text-lg")
            ui.label("The execution has been prepared").classes("text-teal")
            ui.icon("check").classes("text-teal text-lg")
            ui.label("The execution has been run").classes("text-teal")


def ui_display_secrets(secrets):
    with ui.row():
        if secrets:
            ui.icon("check").classes("text-teal text-lg")
            ui.label("Secrets have been set").classes("text-teal")



def build_cli_command(cmd, project_path, execution_id=None, secret_files=None, step_nr=None):
    cli_parameters = [
        f"--project-path {project_path}",
    ]
    if execution_id:
        cli_parameters.append(
            f"--execution-id {execution_id}",
        )
    if step_nr:
        cli_parameters.append(
            f"--step-nr {step_nr}",
        )
    if secret_files and [secret_file for secret_file in secret_files]:
        secret_files_for_run = ",".join(secret_files)
        if secret_files_for_run:
            cli_parameters.append(
                f"--secrets-files {secret_files_for_run}",
            )
    cli_command = f"odtp execution {cmd} {'  '.join(cli_parameters)}"
    return cli_command
