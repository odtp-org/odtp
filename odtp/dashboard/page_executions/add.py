import json
import logging

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.validators as validators
import odtp.helpers.parse as odtp_parse
import odtp.mongodb.db as db
from odtp.dashboard.page_executions.parameters_form import ContainerParameters
from odtp.dashboard.page_executions.ports_form import ContainerPorts
from odtp.dashboard.page_executions.workflow_form import ContainerWorkflow
from odtp.dashboard.utils.file_picker import local_file_picker
from odtp.helpers.settings import ODTP_DASHBOARD_JSON_EDITOR

STEPPERS = (
    "Start",
    "Workflow",
    "Parameters from File",
    "Parameters Overwrite",
    "Ports mapping",
    "Save",
)

STEPPER_START_INDEX = 0
STEPPER_WORKFLOW_INDEX = 1
STEPPER_CONFIRM_INDEX = 2
STEPPER_CONFIGURATION_PARAMETERS_INDEX = 3
STEPPER_CONFIGURATION_PORTS_INDEX = 4
STEPPER_SAVE_INDEX = 5

log = logging.getLogger("__name__")


def ui_execution_add_form(current_digital_twin, workdir, current_execution_to_add):
    ui.button(
        "Cancel Execution Entry",
        on_click=lambda: cancel_execution_entry(),
        icon="cancel",
    )
    ui.markdown(
        """
        #### Add Execution
        """
    )
    if current_execution_to_add:
        if ODTP_DASHBOARD_JSON_EDITOR:
            with ui.expansion("Current Execution as JSON"):
                ui.json_editor(
                    {"content": {"json": current_execution_to_add}, "readOnly": True}
                )
    if current_execution_to_add:
        ui.label(
            f"Digital Twin: {current_execution_to_add.get('digital_twin_name')}"
        ).classes("text-lg w-full")
        stepper = current_execution_to_add.get("stepper")
    else:
        stepper = STEPPERS[STEPPER_START_INDEX]
    with ui.stepper(value=stepper).props("vertical").classes("w-full") as stepper:
        with ui.step(STEPPERS[STEPPER_START_INDEX]):
            with ui.stepper_navigation().classes("w-full"):
                ui_new_execution_start_form(
                    current_digital_twin, current_execution_to_add
                )
        with ui.step(STEPPERS[STEPPER_WORKFLOW_INDEX]):
            with ui.stepper_navigation():
                ui_execution_workflow_template_form(current_execution_to_add)
        with ui.step(STEPPERS[STEPPER_CONFIRM_INDEX]):
            with ui.stepper_navigation():
                ui_execution_workflow_confirmation_form(
                    current_execution_to_add, workdir
                )
        with ui.step(STEPPERS[STEPPER_CONFIGURATION_PARAMETERS_INDEX]):
            with ui.stepper_navigation():
                ui_execution_configuration_parameters_form(current_execution_to_add)
        with ui.step(STEPPERS[STEPPER_CONFIGURATION_PORTS_INDEX]):
            with ui.stepper_navigation():
                ui_execution_configuration_ports_form(current_execution_to_add)
        with ui.step(STEPPERS[STEPPER_SAVE_INDEX]):
            with ui.stepper_navigation():
                ui_execution_save_form(current_execution_to_add)


def ui_new_execution_start_form(current_digital_twin, current_execution_to_add):
    if current_execution_to_add:
        presets = {
            "name": current_execution_to_add.get("name", ""),
        }
    else:
        presets = {
            "name": "",
        }
    name_input = ui.input(
        label="Execution title",
        placeholder="Execution title",
        validation={
            f"Please provide an execution title": lambda value: validators.validate_required_input(
                value
            )
        },
        value=presets["name"],
    ).classes("w-1/2")
    ui.button(
        "Next",
        on_click=lambda: store_new_execution_init(
            name_input=name_input,
            digital_twin=current_digital_twin,
            current_execution_to_add=current_execution_to_add,
        ),
    )


def ui_execution_workflow_template_form(current_execution_to_add):
    if not current_execution_to_add:
        return
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_WORKFLOW_INDEX:
        return
    current_version_tags = current_execution_to_add.get("version_tags", [])
    current_versions = current_execution_to_add.get("versions", [])
    workflow_form = ContainerWorkflow(
        versions=current_versions,
        version_tags=current_version_tags,
    )
    with ui.row().classes("w-full"):
        ui.button(
            "Next",
            on_click=lambda: store_new_execution_workflow(
                current_execution_to_add=current_execution_to_add,
                workflow=workflow_form.get_steps(),
            ),
        )
        ui.button(
            "Back",
            on_click=lambda: execution_form_step_back(
                current_execution_to_add=current_execution_to_add,
            ),
        ).props("flat")


def ui_execution_workflow_confirmation_form(current_execution_to_add, workdir):
    if not current_execution_to_add:
        return
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_CONFIRM_INDEX:
        return
    version_tags = current_execution_to_add.get("version_tags")
    if not version_tags:
        return
    with ui.grid(columns=2).classes("flex items-center"):
        for j, version_tag in enumerate(version_tags):
            with ui.row().classes("w-full flex items-center"):
                ui.mermaid(
                    f"""
                    {helpers.get_workflow_mermaid([version_tag], init='graph TB;')}"""
                )
                ui.button(
                    f"Pick parameters from file",
                    on_click=lambda step_index=j: pick_parameter_file(
                        step_index,
                        workdir=workdir,
                        current_execution_to_add=current_execution_to_add,
                    ),
                    icon="folder",
                ).props("flat")
                if current_execution_to_add["parameter_files"][j]:
                    ui.icon("check").classes("text-lg text-teal-500")
    with ui.grid(columns=1).classes("w-full"):
        with ui.row().classes("w-full"):
            ui.button(
                "Next",
                on_click=lambda: confirm_new_execution_workflow(
                    current_execution_to_add=current_execution_to_add,
                ),
            )
            ui.button(
                "Back",
                on_click=lambda: execution_form_step_back(
                    current_execution_to_add=current_execution_to_add,
                ),
            ).props("flat")


def ui_execution_configuration_parameters_form(current_execution_to_add):
    if not current_execution_to_add:
        return
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_CONFIGURATION_PARAMETERS_INDEX:
        return
    version_tags = current_execution_to_add.get("version_tags")
    if not version_tags:
        return
    current_parameters = current_execution_to_add.get("parameters")
    parameters_form = ContainerParameters(
        version_tags=version_tags, parameters=current_parameters
    )
    with ui.row().classes("w-full"):
        ui.button(
            "Next",
            on_click=lambda: add_parameters_configuration_to_workflow(
                current_execution_to_add=current_execution_to_add,
                parameters=parameters_form.get_parameters(),
            ),
        )
        ui.button(
            "Back",
            on_click=lambda: execution_form_step_back(
                current_execution_to_add=current_execution_to_add,
            ),
        ).props("flat")


def ui_execution_configuration_ports_form(current_execution_to_add):
    if not current_execution_to_add:
        return
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_CONFIGURATION_PORTS_INDEX:
        return
    version_tags = current_execution_to_add.get("version_tags")
    if not version_tags:
        return
    current_ports = current_execution_to_add.get("ports")
    ports_form = ContainerPorts(version_tags, current_ports)
    with ui.row().classes("w-full"):
        ui.button(
            "Next",
            on_click=lambda: add_ports_configuration_to_workflow(
                current_execution_to_add=current_execution_to_add,
                all_ports_inputs=ports_form.get_ports(),
            ),
        )
        ui.button(
            "Back",
            on_click=lambda: execution_form_step_back(
                current_execution_to_add=current_execution_to_add,
            ),
        ).props("flat")


def ui_execution_save_form(current_execution_to_add):
    if not current_execution_to_add:
        return
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_SAVE_INDEX:
        return
    execution_title = current_execution_to_add.get("name")
    version_tags = current_execution_to_add.get("version_tags")
    current_ports = current_execution_to_add.get("ports")
    current_parameters = current_execution_to_add.get("parameters")
    ui_theme.ui_execution_display(
        execution_title=execution_title,
        version_tags=version_tags,
        ports=current_ports,
        parameters=current_parameters,
    )
    with ui.row().classes("w-full"):
        ui.button(
            "Save",
            on_click=lambda: save_new_execution(
                current_execution_to_add=current_execution_to_add,
            ),
        )
        ui.button(
            "Back",
            on_click=lambda: execution_form_step_back(
                current_execution_to_add=current_execution_to_add,
            ),
        ).props("flat")


def store_new_execution_init(name_input, digital_twin, current_execution_to_add):
    try:
        if not name_input.validate():
            ui.notify("Please fill in the form as required", type="negative")
            return
        if not current_execution_to_add:
            current_execution_to_add = {
                "digital_twin_id": digital_twin["digital_twin_id"],
                "digital_twin_name": digital_twin["name"],
                "step_count": 0,
                "form_step_count": 1,
                "parameters": [],
                "ports": [],
            }
        current_execution_to_add["name"] = name_input.value
        current_execution_to_add["stepper"] = STEPPERS[STEPPER_WORKFLOW_INDEX]
        app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    except Exception as e:
        log.exception(f"Execution could not be initialized. An Exception occurred: {e}")   
    else:    
        from odtp.dashboard.page_executions.main import ui_add_execution
        ui_add_execution.refresh()


def store_new_execution_workflow(current_execution_to_add, workflow):
    try:
        if not workflow or False in [item.validate() for item in workflow]:
            ui.notify(
                "Please choose at least one workflow step. Remove steps that are not needed."
            )
            return
        workflow = [item.value for item in workflow if item.value]
        current_execution_to_add["versions"] = [item[0] for item in workflow]
        current_execution_to_add["version_tags"] = [item[1] for item in workflow]
        step_count = len(workflow)
        current_execution_to_add["parameters"] = [[] for i in range(step_count)]
        current_execution_to_add["parameter_files"] = [[] for i in range(step_count)]
        current_execution_to_add["ports"] = [{} for i in range(step_count)]
        current_execution_to_add["stepper"] = STEPPERS[STEPPER_CONFIRM_INDEX]
        app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    except Exception as e:
        log.exception(f"Execution workflow could not be added. An Exception occurred: {e}")    
    else:           
        from odtp.dashboard.page_executions.main import ui_add_execution
        ui_add_execution.refresh()


def cancel_execution_entry():
    try:
        storage.reset_storage_delete([storage.NEW_EXECUTION])
        ui.notify("The execution entry was canceled")
    except Exception as e:
        log.exception(f"Execution entry could not be canceled. An Exception occurred: {e}")    
    else:          
        from odtp.dashboard.page_executions.main import ui_add_execution
        ui_add_execution.refresh()


def execution_form_step_back(current_execution_to_add):
    try:
        current_stepper = current_execution_to_add["stepper"]
        current_stepper_index = STEPPERS.index(current_stepper)
        next_stepper_index = current_stepper_index - 1
        next_stepper = STEPPERS[next_stepper_index]
        current_execution_to_add["stepper"] = next_stepper
        app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    except Exception as e:
        log.exception(f"Execution form step back failed. An Exception occurred: {e}")    
    else:        
        from odtp.dashboard.page_executions.main import ui_add_execution
        ui_add_execution.refresh()


def confirm_new_execution_workflow(current_execution_to_add):
    try:
        current_execution_to_add["stepper"] = STEPPERS[
            STEPPER_CONFIGURATION_PARAMETERS_INDEX
        ]
        app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    except Exception as e:
        log.exception(f"Execution workflow confirmation failed. An Exception occurred: {e}")     
    else:         
        from odtp.dashboard.page_executions.main import ui_add_execution
        ui_add_execution.refresh()


def add_parameters_configuration_to_workflow(current_execution_to_add, parameters):
    try:
        current_execution_to_add["parameters"] = parameters
        current_execution_to_add["stepper"] = STEPPERS[STEPPER_CONFIGURATION_PORTS_INDEX]
        app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    except Exception as e:
        log.exception(f"Execution parameters could not be added. An Exception occurred: {e}")     
    else:        
        from odtp.dashboard.page_executions.main import ui_add_execution
        ui_add_execution.refresh()


def add_ports_configuration_to_workflow(current_execution_to_add, all_ports_inputs):
    try:
        ports = []
        for row in all_ports_inputs:
            if False in [port_input.validate() for port_input in row]:
                return
            ports.append([port_input.value for port_input in row if port_input.value])
        current_execution_to_add["ports"] = ports
        current_execution_to_add["stepper"] = STEPPERS[STEPPER_SAVE_INDEX]
        app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    except Exception as e:
        log.exception(f"Execution ports could not be added. An Exception occurred: {e}")    
    else:           
        from odtp.dashboard.page_executions.main import ui_add_execution
        ui_add_execution.refresh()


async def pick_parameter_file(step_index, workdir, current_execution_to_add) -> None:
    try:
        root = workdir
        result = await local_file_picker(root, multiple=False)
        if not result:
            ui.notify("No new parameter file was selected.", type="negative")
            return
        if result:
            file_path = result[0]
            parameters = dict(odtp_parse.parse_parameters_for_one_file(file_path))
            current_execution_to_add["parameters"][step_index] = parameters
            current_execution_to_add["parameter_files"][step_index] = file_path
            app.storage.user[storage.NEW_EXECUTION] = json.dumps(
                current_execution_to_add
            )
    except odtp_parse.OdtpParameterParsingException:
        ui.notify(
            f"Selected file {file_path} could not be parsed. Is it a parameter file?",
            type="negative",
        )
    except Exception as e:
        logging.error(f"An exception {e} occurred when picking a parameter file.")
    else:
        ui.notify(
            f"parameters have been loaded for step {step_index + 1}", type="positive"
        )
        from odtp.dashboard.page_executions.main import ui_add_execution
        ui_add_execution.refresh()


def save_new_execution(current_execution_to_add):
    try:
        execution_id, step_ids = db.add_execution(
            dt_id=current_execution_to_add["digital_twin_id"],
            name=current_execution_to_add["name"],
            versions=current_execution_to_add["versions"],
            parameters=current_execution_to_add["parameters"],
            ports=current_execution_to_add["ports"],
        )
        execution_id_display = str(execution_id)
        step_ids_display = ",".join([str(step_id) for step_id in step_ids])
        ui.notify(
            f"An execution with id {execution_id_display} and steps: {step_ids_display} has been created",
            type="positive",
        )
    except Exception as e:
        ui.notify(
            f"Execution could not be added. An exception happened: {e}", type="negative"
        )
    else:
        storage.reset_storage_delete([storage.NEW_EXECUTION])
        execution_id = str(execution_id)
        from odtp.dashboard.page_executions.select import store_selected_execution
        store_selected_execution(execution_id)
        from odtp.dashboard.page_executions.main import (
            ui_executions_table, ui_add_execution, ui_tabs, ui_execution_details, ui_execution_select
        )
        ui_add_execution.refresh()
        ui_executions_table.refresh()
        ui_execution_select.refresh()
        ui_execution_details.refresh()
        ui_tabs.refresh()
