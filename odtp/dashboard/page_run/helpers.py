import json
import logging

from nicegui import app, ui
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme


log = logging.getLogger(__name__)


STEPPERS = (
    "Display Execution",
    "Add Secret Files",
    "Select Folder",
    "Prepare Execution (Build Images)",
    "Run Execution (Run Containers)",
)

STEPPER_DISPLAY_EXECUTION = 0
STEPPER_ADD_SECRETS = 1
STEPPER_SELECT_FOLDER = 2
STEPPER_PREPARE_EXECUTION = 3
STEPPER_RUN_EXECUTION = 4


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
    with ui.row():
        ui.icon("check").classes("text-teal text-lg")
        ui.label("Execution to run is selected").classes("text-teal")
    ui_theme.ui_execution_display(
        execution_title=execution_title,
        version_tags=version_tags,
        ports=current_ports,
        parameters=current_parameters,
    )
    ui_next_back(current_run)    


def ui_next_back(current_run, ready_for_next=True):
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
