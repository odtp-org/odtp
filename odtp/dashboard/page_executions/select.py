import json
import logging

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme


log = logging.getLogger("__name__")


def ui_select_form(execution_options, current_execution):
    if not execution_options:
        ui_theme.ui_no_items_yet("Executions")
        return
    current_execution = storage.get_active_object_from_storage(
        storage.CURRENT_EXECUTION
    )
    if current_execution:
        selected_value = current_execution["execution_id"]
    else:
        selected_value = None
    ui.markdown(
        """
        #### Select Execution
        """
    )
    ui.select(
        execution_options,
        value=selected_value,
        label="executions",
        on_change=lambda e: store_selected_execution(e.value),
        with_input=True,
    ).classes("w-full")
    ui.button(
        "Unselect Execution",
        on_click=lambda: cancel_execution_selection(),
        icon="cancel",
    )
    

def store_selected_execution(value):
    if not ui_theme.new_value_selected_in_ui_select(value):
        return
    try:
        execution_id = value
        execution = helpers.build_execution_with_steps(execution_id)
        current_execution_as_json = json.dumps(execution)
        app.storage.user[storage.CURRENT_EXECUTION] = current_execution_as_json
    except Exception as e:
        log.exception(
            f"Selected execution could not be stored. An Exception occurred: {e}"
        )
    else:
        from odtp.dashboard.page_executions.main import ui_execution_details, ui_workarea, ui_execution_select
        ui_execution_details.refresh()
        ui_workarea.refresh()
        ui_execution_select.refresh()


def cancel_execution_selection():
    try:
        storage.reset_storage_delete([storage.CURRENT_EXECUTION])
    except Exception as e:
        log.exception(
            f"Execution selection could not be canceled. An Exception occurred: {e}"
        ) 
    else:       
        ui.notify("The execution selection was canceled")
        from odtp.dashboard.page_executions.main import ui_execution_details, ui_workarea, ui_execution_select    
        ui_execution_details.refresh()
        ui_workarea.refresh()
        ui_execution_select.refresh()
