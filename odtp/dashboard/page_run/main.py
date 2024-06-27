import logging
from nicegui import ui

import odtp.dashboard.utils.storage as storage
from odtp.helpers.settings import ODTP_DASHBOARD_JSON_EDITOR
import odtp.dashboard.page_run.helpers as rh
import odtp.dashboard.page_run.secrets as secrets
import odtp.dashboard.page_run.run as run
import odtp.dashboard.page_run.folder as folder
import odtp.dashboard.page_run.workarea as workarea


log = logging.getLogger(__name__)


def content() -> None:
    try:
        current_user = storage.get_active_object_from_storage(storage.CURRENT_USER)
        workdir = storage.get_value_from_storage_for_key(storage.CURRENT_USER_WORKDIR)
        current_digital_twin = storage.get_active_object_from_storage(
            storage.CURRENT_DIGITAL_TWIN
        )
        current_execution = storage.get_active_object_from_storage(
            storage.CURRENT_EXECUTION
        )
        ui.json_editor({'content': {'json': current_execution}})
        if not current_execution:
            return
        current_run = rh.execution_run_init(
            digital_twin=current_digital_twin, execution=current_execution
        )
        with ui.dialog().props("full-width") as dialog, ui.card():
            result = ui.markdown()
            ui.button("Close", on_click=dialog.close)
        ui_workarea(
            current_user=current_user,
            current_digital_twin=current_digital_twin,
            current_execution=current_execution,
            workdir=workdir,
        )
        ui_stepper(
            dialog,
            result,
            current_run=current_run,
            workdir=workdir,
        )
    except Exception as e:
        log.exception(f"Page could not be loaded: an Exception {e} occurred")


@ui.refreshable
def ui_workarea(current_user, current_digital_twin, current_execution, workdir):
    try:
        workarea.ui_workarea_layout(
            current_user=current_user,
            current_digital_twin=current_digital_twin,
            current_execution=current_execution,
            workdir=workdir,        
        )
    except Exception as e:
        log.exception(f"Workarea could not be loaded: an Exception {e} occurred")


@ui.refreshable
def ui_stepper(
    dialog, result, current_run, workdir
):
    try:
        current_run = storage.get_active_object_from_storage(storage.EXECUTION_RUN) 
        stepper = current_run.get("stepper")
        execution = current_run["execution"]
        project_path = current_run.get("project_path")
        if project_path:
            folder_status = folder.get_folder_status(
                execution_id=execution["execution_id"],
                project_path=project_path,
            )
        else:
            folder_status = folder.FOLDER_NOT_SET       
        if ODTP_DASHBOARD_JSON_EDITOR:
            with ui.expansion("Current Execution Run as JSON"):
                ui.json_editor(
                    {
                        "content": {"json": current_run},
                        "readOnly": True,
                    }
                )
        with ui.stepper(value=stepper).props("vertical").classes("w-full") as stepper:
            with ui.step(rh.STEPPERS[rh.STEPPER_DISPLAY_EXECUTION]):
                rh.ui_execution_details(current_run)
            with ui.step(rh.STEPPERS[rh.STEPPER_ADD_SECRETS]):
                with ui.stepper_navigation():
                    with ui.row():
                        secrets.ui_add_secrets_form(
                            current_run=current_run,
                            workdir=workdir,
                        )
            with ui.step(rh.STEPPERS[rh.STEPPER_SELECT_FOLDER]):
                with ui.stepper_navigation():
                    with ui.row():
                        folder.ui_prepare_folder(
                            dialog=dialog,
                            result=result,
                            current_run=current_run,
                            workdir=workdir,
                            folder_status=folder_status,
                        )
            with ui.step(rh.STEPPERS[rh.STEPPER_PREPARE_EXECUTION]):
                with ui.stepper_navigation():
                    run.ui_prepare_execution(
                        dialog=dialog,
                        result=result,
                        current_run=current_run,
                        folder_status=folder_status,
                    )
            with ui.step(rh.STEPPERS[rh.STEPPER_RUN_EXECUTION]):
                run.ui_run_execution(
                    dialog=dialog,
                    result=result,
                    current_run=current_run,
                    folder_status=folder_status,
                )
    except Exception as e:
        log.exception(f"Stepper could not be loaded: an Exception {e} occurred")
