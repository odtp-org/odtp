import json
import logging

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.helpers.parse as odtp_parse
from odtp.dashboard.utils.file_picker import local_file_picker
import odtp.dashboard.page_run.helpers as rh


log = logging.getLogger(__name__)


def ui_add_secrets_form(current_run, workdir):
    stepper = current_run.get("stepper")
    if stepper and rh.STEPPERS.index(stepper) != rh.STEPPER_ADD_SECRETS:
        return
    version_tags = current_run["execution"]["version_tags"]
    if not version_tags:
        return
    with ui.row():
        ui.icon("check").classes("text-teal text-lg")
        ui.label("Adding Secrets files is an optional step").classes("text-teal")        
    with ui.grid(columns=2).classes("flex items-center w-full"):
        for j, version_tag in enumerate(version_tags):
            secret_file = current_run["secret_files"][j]
            with ui.row().classes("w-full flex items-center"):
                ui.mermaid(
                    f"""
                    {helpers.get_workflow_mermaid([version_tag], init='graph TB;')}"""
                )
                ui.button(
                    f"Pick secrets file",
                    on_click=lambda step_index=j: pick_secrets_file(
                        step_nr=step_index,
                        workdir=workdir,
                        current_run=current_run,
                    ),
                    icon="key",
                ).props("flat")
                if secret_file:
                    ui.markdown(
                        f"""
                    - **file path**: {secret_file}
                    """
                    )
    with ui.row().classes("w-full"):                
        ui.button(
            f"Reset secrets files",
            on_click=lambda: remove_secrets_files(current_run),
            icon="clear",
        ).props("flat")                    
    rh.ui_next_back(current_run)


async def pick_secrets_file(step_nr, workdir, current_run) -> None:
    try:
        root = workdir
        result = await local_file_picker(root, multiple=False)
        if not result:
            return
        file_path = result[0]
        odtp_parse.parse_parameters_for_one_file(file_path)
        current_run["secret_files"][step_nr] = file_path
        ui.notify(
            f"Secrets file has been added for step {step_nr + 1}", type="positive"
        )
        current_run["stepper"] = rh.STEPPERS[rh.STEPPER_ADD_SECRETS]
        app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
    except odtp_parse.OdtpParameterParsingException:
        ui.notify(
            f"Selected file {file_path} could not be parsed. Is it a parameter file?",
            type="negative",
        )
    except Exception as e:
        log.exception(f"An exception {e} occurred when picking a parameter file.")
    else:
        from odtp.dashboard.page_run.main import ui_workarea, ui_stepper
        ui_stepper.refresh()
        ui_workarea.refresh()


def remove_secrets_files(current_run) -> None:
    try:
        step_count = len(current_run["execution"]["steps"])
        current_run["secret_files"] = ["" for i in range(step_count)]
        app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
        ui.notify("The secrets files have been removed", type="positive")
    except Exception as e:
        log.exception(f"removing secret files failed with Exception {e}")        
    else:
        from odtp.dashboard.page_run.main import ui_workarea, ui_stepper      
        ui_stepper.refresh()
        ui_workarea.refresh()
