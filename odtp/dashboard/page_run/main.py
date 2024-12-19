import logging
from nicegui import ui
from pprint import pprint

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
        run.ExecutionRunForm(
            digital_twin_id=current_digital_twin["digital_twin_id"],
            execution_id=current_execution["execution_id"],
            workdir=workdir,
            dialog=dialog,
            result=result,
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
