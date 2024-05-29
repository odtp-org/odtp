import asyncio
import os.path
import shlex
import json
import sys
import logging
from pprint import pprint

from nicegui import ui, app

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.validators as validators
import odtp.helpers.parse as odtp_parse
import odtp.helpers.environment as odtp_env
from odtp.dashboard.utils.file_picker import local_file_picker
from odtp.helpers.settings import ODTP_DASHBOARD_JSON_EDITOR
import odtp.mongodb.db as db


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


FOLDER_EMPTY = "empty"
FOLDER_PREPARED = "prepared"
FOLDER_HAS_OUTPUT = "output"
FOLDER_DOES_NOT_MATCH = "no_match"
FOLDER_NOT_SET = "not_set"


folder_status_msg = {
   FOLDER_NOT_SET: "Project folder has not been selected",
   FOLDER_EMPTY: "Project folder ready for Prepare Execution",
   FOLDER_PREPARED: "Project folder ready for Run Execution",
   FOLDER_HAS_OUTPUT: "Project folder has output: Check Output",
   FOLDER_DOES_NOT_MATCH: """Project Folder is not empty and has not been prepared by the execution: 
Choose an empty project folder or create a new one.""" 
}


def content() -> None:
    current_user = storage.get_active_object_from_storage(
        storage.CURRENT_USER
    )
    workdir = storage.get_value_from_storage_for_key(
        storage.CURRENT_USER_WORKDIR
    )       
    current_digital_twin = storage.get_active_object_from_storage(
        storage.CURRENT_DIGITAL_TWIN
    )
    current_execution = storage.get_active_object_from_storage(
        storage.CURRENT_EXECUTION
    )      
    current_run = storage.get_active_object_from_storage(
       storage.EXECUTION_RUN
    )
    if not current_execution:
        return    
    if not run_belongs_to_current_execution(current_execution, current_run):    
        current_run = execution_run_init(
            digital_twin=current_digital_twin, 
            execution=current_execution
        )  
        ui_workarea.refresh()
        ui_stepper.refresh()                       
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
        current_digital_twin=current_digital_twin,
        current_execution=current_execution,
        current_run=current_run,
        workdir=workdir,
    )


def run_belongs_to_current_execution(current_execution, current_run):
    if not current_run: 
        return False
    if current_run["execution"]["execution_id"] != current_execution["execution_id"]:
        return False
    return True          


@ui.refreshable
def ui_workarea(current_user, current_digital_twin, current_execution, workdir):
    ui.markdown(
        """
        ## Prepare and Run Executions
        """
    )    
    if not current_user:
        ui_theme.ui_add_first(
            item_name="user",
            page_link=ui_theme.PATH_USERS,
            action="select",
        )     
        return
    if not workdir:
        ui_theme.ui_add_first(
            item_name="working directory",
            page_link=ui_theme.PATH_USERS,
            action="select",
        )     
        return          
    if not current_digital_twin:
        ui_theme.ui_add_first(
            item_name="a digital twin",
            page_link=ui_theme.PATH_DIGITAL_TWINS,
            action="select",
        )     
        return   
    if not current_execution:
        ui_theme.ui_add_first(
            item_name="an executions",
            page_link=ui_theme.PATH_EXECUTIONS,
            action="select",
        )     
        return        
    current_run = storage.get_active_object_from_storage(
       storage.EXECUTION_RUN
    )    
    secret_files = current_run.get("secret_files")
    project_path = current_run.get("project_path")
    if not [file for file in secret_files if file]:
        secret_files = "" 
    else: 
        ",".join(secret_files)    
    if not project_path:     
        project_path = ui_theme.MISSING_VALUE     
    with ui.grid(columns=2):  
        with ui.column():             
            ui.markdown(
                f"""
                #### Current Selection
                - **user**: {current_user.get("display_name")}
                - **digital twin**: {current_digital_twin.get("name")}
                - **current execution**: {current_execution.get("title")}
                - **secret files**: {secret_files}
                - **work directory**: {workdir}
                - **project directory**: {project_path}
                """
            ) 
        with ui.column():                             
            if current_execution:
                ui.markdown(
                    f"""
                    #### Actions
                    """
                )
                ui.button(
                    "Manage Executions",
                    on_click=lambda: ui.open(ui_theme.PATH_EXECUTIONS),
                    icon="link",
                )


@ui.refreshable 
def ui_stepper(dialog, result, current_digital_twin, current_execution, current_run, workdir):
    current_run = storage.get_active_object_from_storage(
       storage.EXECUTION_RUN
    )
    stepper = current_run.get("stepper")
    if ODTP_DASHBOARD_JSON_EDITOR:
        with ui.expansion("Current Execution Run as JSON"):
            ui.json_editor(
                {'content': {'json': current_run },
                'readOnly': True,
                }
            )
    with ui.stepper(value=stepper).props('vertical').classes('w-full') as stepper:
        with ui.step(STEPPERS[STEPPER_DISPLAY_EXECUTION]):           
            ui_execution_details(current_run)
        with ui.step(STEPPERS[STEPPER_ADD_SECRETS]):
            with ui.stepper_navigation():
                with ui.row():
                    ui_add_secrets_form(
                        current_run=current_run,
                        workdir=workdir,
                    )
        with ui.step(STEPPERS[STEPPER_SELECT_FOLDER]):
            with ui.stepper_navigation():
                with ui.row():
                    ui_prepare_folder(
                        dialog=dialog,
                        result=result,
                        current_run=current_run,
                        workdir=workdir,
                    )
        with ui.step(STEPPERS[STEPPER_PREPARE_EXECUTION]):
            with ui.stepper_navigation():
                ui_prepare_execution(
                    dialog=dialog,
                    result=result,
                    current_run=current_run,
                )
        with ui.step(STEPPERS[STEPPER_RUN_EXECUTION]):
            ui_run_execution(
                dialog=dialog,
                result=result,
                current_run=current_run,
            )



def ui_run_status(current_run):
    execution = current_run.get("execution")
    project_path = current_run.get("project_path")
    secret_files = current_run.get("secret_files")
    with ui.grid(columns=2).classes("flex items-start"):
        with ui.row().classes("flex items-center w-full"):
            if not execution:
                ui.icon("clear").classes("text-red-500")
                ui.label("Execution selected").classes("text-red-500")
                return
            ui.icon("check").classes("text-teal-500 text-lg")
            ui.label("Execution selected")
            ui.markdown(
                f"""
                - **execution**: {execution["title"]}
                """
            )
        with ui.row().classes("flex items-center w-full"):
            if secret_files:
                ui.icon("check").classes("text-teal-500 text-lg")
                ui.label("Secret files added")
                ui.markdown(
                    f"""
                    - **secret files**: {secret_files}
                    """
                )
            else:
                ui.icon("info").classes("text-lg")
                ui.label("No secret files")
        with ui.row().classes("flex items-center w-full"):
            if not project_path:
                ui.icon("clear").classes("text-red-500")
                ui.label("Project folder selected").classes("text-red-500")
                return
            ui.icon("check").classes("text-teal-500 text-lg")
            ui.label("Project folder selected")
            folder_status = get_folder_status(
                execution_id=execution["execution_id"],
                project_path=project_path,
            )
            msg = folder_status_msg.get(folder_status)
            if folder_status == FOLDER_DOES_NOT_MATCH:
                ui.icon("clear").classes("text-red-500")
                ui.label(msg).classes("text-red-500")
                return
            ui.markdown(
                f"""
                - **project path**: {project_path}
                - **status**: {folder_status}
                - **message**: {msg}
                """
            )


def ui_next_back(current_run):
    stepper = current_run.get("stepper")
    with ui.grid(columns=1).classes('w-full'):
        with ui.row().classes('w-full'):
            if stepper and STEPPERS.index(stepper) != STEPPER_RUN_EXECUTION:
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
                ).props('flat')


def execution_run_init(digital_twin, execution):
    step_count = len(execution["steps"])
    print("======================")
    print(step_count)
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


def ui_add_secrets_form(current_run, workdir):
    logging.info("ui form secrets")
    stepper = current_run.get("stepper")
    if stepper and STEPPERS.index(stepper) != STEPPER_ADD_SECRETS:
        return
    version_tags = current_run["execution"]["version_tags"]
    if not version_tags:
        return
    with ui.grid(columns=2).classes("flex items-center w-full"):
        for j, version_tag in enumerate(version_tags):
            secret_file = current_run["secret_files"][j]
            with ui.row().classes("w-full flex items-center"):
                ui.mermaid(f"""
                    {helpers.get_workflow_mermaid([version_tag], init='graph TB;')}"""
                )
                ui.button(
                    f"Pick secrets file",
                    on_click=lambda step_index=j: pick_secrets_file(
                        step_nr=step_index,
                        workdir=workdir,
                        current_run=current_run,
                    ), 
                    icon="key"
                ).props('flat')
                if secret_file:
                    ui.markdown(f"""
                    - **file path**: {secret_file}
                    """)
    with ui.grid(columns=1).classes("flex items-left"):
        ui.button(
            f"Reset secrets files", 
            on_click=lambda: remove_secrets_files(current_run),
            icon="clear"
        ).props('flat')
    ui_next_back(current_run)


def run_form_step_back(current_run):
    logging.info("run_form_step_back")
    current_stepper = current_run["stepper"]
    current_stepper_index = STEPPERS.index(current_stepper)
    next_stepper_index = current_stepper_index - 1
    next_stepper = STEPPERS[next_stepper_index]
    current_run["stepper"] = next_stepper
    app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
    ui_stepper.refresh()


def next_step(current_run):
    logging.info("next_step")
    logging.info(current_run["stepper"])
    current_stepper = current_run["stepper"]
    current_stepper_index = STEPPERS.index(current_stepper)
    next_stepper_index = current_stepper_index + 1
    next_stepper = STEPPERS[next_stepper_index]
    current_run["stepper"] = next_stepper
    app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
    logging.info(current_run["stepper"])
    ui_stepper.refresh()


async def pick_secrets_file(step_nr, workdir, current_run) -> None:
    try:
        root = workdir
        result = await local_file_picker(root, multiple=False)
        if not result:
            return
        file_path = result[0]
        odtp_parse.parse_parameters_for_one_file(file_path)
        current_run["secret_files"][step_nr] = file_path
        ui.notify(f"Secrets file has been added for step {step_nr + 1}", type="positive")
        current_run["stepper"] = STEPPERS[STEPPER_ADD_SECRETS]
        app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
    except odtp_parse.OdtpParameterParsingException:
        ui.notify(f"Selected file {file_path} could not be parsed. Is it a parameter file?", type="negative")
    except Exception as e:
        logging.error(f"An exception {e} occurred when picking a parameter file.")
    else:
        ui_stepper.refresh()
        ui_workarea.refresh()


def remove_secrets_files(current_run) -> None:
    step_count = len(current_run["execution"]["steps"])
    current_run["secret_files"] = ["" for i in range(step_count)]
    app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
    ui.notify("The secrets files have been removed", type="positive")
    ui_stepper.refresh()
    ui_workarea.refresh()


def remove_project_folder(current_run) -> None:
    current_run["project_path"] = ""
    app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
    ui.notify("The project path been reset", type="positive")
    ui_stepper.refresh()
    ui_workarea.refresh()


def ui_execution_details(current_run):
    execution = current_run.get("execution")
    try:
        execution_title = execution.get('title')
        version_tags = execution.get("version_tags")
        current_ports = execution.get("ports")
        current_parameters = execution.get("parameters")
        ui_theme.ui_execution_display(
            execution_title=execution_title,
            version_tags=version_tags,
            ports=current_ports,
            parameters=current_parameters,
        )         
    except Exception as e:
        logging.error(
            f"Execution details could not be loaded. An Exception occurred: {e}",
        )
    ui_next_back(current_run)    

def ui_prepare_folder(dialog, result, workdir, current_run):
    stepper = current_run.get("stepper")
    project_path = current_run.get("project_path")
    execution = current_run.get("execution")
    folder_matches = False
    if stepper and STEPPERS.index(stepper) != STEPPER_SELECT_FOLDER:
        return
    if project_path:
        with ui.row().classes("w-full"):
            ui.markdown(
                f"""
                - **project path**: {project_path}
                """
            )

        folder_status = get_folder_status(
            execution_id=execution["execution_id"],
            project_path=project_path,
        )
        if folder_status in [FOLDER_EMPTY, FOLDER_HAS_OUTPUT, FOLDER_PREPARED]:
            ui.label(folder_status_msg.get(folder_status)).classes("text-teal")
        else:
            ui.label(folder_status_msg.get(folder_status)).classes("text-read")     
        folder_matches = folder_status in [FOLDER_EMPTY, FOLDER_HAS_OUTPUT, FOLDER_PREPARED]
        if folder_matches:
            cli_output_command = build_command(
                cmd="output",
                execution_id=execution['execution_id'],
                project_path=project_path,
            )

    with ui.row().classes("w-full"):    
        ui.button(
            "Choose other project folder", 
            on_click=lambda: pick_folder(workdir, current_run),
            icon="folder"
        ).props('flat')  
    with ui.row().classes("w-full flex items-center"):       
        project_folder_input = ui.input(
            label="Project folder name", 
            placeholder="execution",
            validation={f"Please provide a folder name does not yet exist in the working directory":
                lambda value: validators.validate_folder_does_not_exist(value, workdir)},                
        )      
        ui.button(
            "Create new project folder", 
            on_click=lambda: create_folder(workdir, project_folder_input, current_run),
            icon="add",
        ).props('flat')
    with ui.grid(columns=1).classes("flex items-left"):
        ui.button(
            f"Reset project folder",
            on_click=lambda: remove_project_folder(current_run),
            icon="clear"
        ).props('flat')
    with ui.row().classes("w-full"):
        if folder_matches:
            ui.button(
                "Show project folder",
                on_click=lambda: run_command(cli_output_command, dialog, result),
                icon="info",
            ).props("no-caps")
    ui_next_back(current_run)


async def pick_folder(workdir, current_run) -> None:
    try:
        root = workdir
        result = await local_file_picker(root, multiple=False)
        if not result:
            return
        if result:
            project_path = result[0]
            current_run["project_path"] = project_path
            current_run["stepper"] = STEPPERS[STEPPER_SELECT_FOLDER]
            app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
            ui.notify(f"A new project folder has been set {project_path}", type="positive")
    except Exception as e:
        logging.error(f"An exception {e} occurred when picking a parameter file.")
    else:
        ui_workarea.refresh()
        ui_stepper.refresh()


def create_folder(workdir, folder_name_input, current_run):
    try:
        folder_name = folder_name_input.value
        project_path = os.path.join(workdir, folder_name)
        os.mkdir(project_path)
        current_run["project_path"] = project_path
        current_run["stepper"] = STEPPERS[STEPPER_SELECT_FOLDER]
        app.storage.user[storage.EXECUTION_RUN] = json.dumps(current_run)
    except Exception as e:
        ui.notify(f"The project directory could not be created: {workdir} {folder_name} an exception occurred: {e}", type="negative")
    else:
        ui.notify(
            f"project directory {project_path} has been created and set as project directory", type="positive")
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


def ui_prepare_execution(dialog, result, current_run):
    stepper = current_run.get("stepper")
    if stepper and STEPPERS.index(stepper) != STEPPER_PREPARE_EXECUTION:
        return        
    execution = current_run["execution"]
    project_path = current_run["project_path"]
    with ui.row().classes("w-full"):
        ui.markdown(f"""
            ###### Prepare the Execution: 

            - clone github repo
            - build Docker images 
            - create folder structure
            """
        )      
    if not project_path: 
        ui.label("Before you can prepare the execution, you need to first select a project path").classes("text-red")
        ui_next_back(current_run)
        return
    folder_status = get_folder_status(
        execution_id=execution["execution_id"],
        project_path=project_path,
    )
    msg = folder_status_msg.get(folder_status)  
    if folder_status in [FOLDER_HAS_OUTPUT]:   
        ui.label(msg).classes("text-teal")      
    elif not folder_status in [FOLDER_EMPTY, FOLDER_PREPARED]:
        ui.label(msg).classes("text-red") 
    if folder_status == FOLDER_EMPTY:
        cli_prepare_command = build_command(
            cmd="prepare",
            execution_id=execution['execution_id'],
            project_path=project_path,
        )         
        with ui.grid(columns=1): 
            with ui.column().classes("w-full"):
                ui.label(cli_prepare_command).classes("font-mono")         
                ui.button(
                    "Prepare execution",
                    on_click=lambda: run_command(cli_prepare_command, dialog, result),
                    icon="folder",
                ).props("no-caps")  
    if project_path:                  
        cli_output_command = build_command(
            cmd="output",
            execution_id=execution['execution_id'],
            project_path=project_path,
        )
        with ui.row().classes("w-full"):
            ui.button(
                "Show project folder",
                on_click=lambda: run_command(cli_output_command, dialog, result),
                icon="info",
            ).props("no-caps")
    ui_next_back(current_run)


def build_command(
    cmd,
    project_path,
    execution_id,
    secret_files=None
):
    cli_parameters = [
        f"--project-path {project_path}",
        f"--execution-id {execution_id}",
    ] 
    if secret_files and [secret_file for secret_file in secret_files]:
        secret_files_for_run = ",".join(secret_files)
        if secret_files_for_run:
            cli_parameters.append(
                f"--secrets-files {secret_files_for_run}",
            )
    cli_command = f"odtp execution {cmd} {'  '.join(cli_parameters)}"
    return cli_command


def ui_run_execution(dialog, result, current_run):
    stepper = current_run.get("stepper")
    if stepper and STEPPERS.index(stepper) != STEPPER_RUN_EXECUTION:
        return
    execution = current_run["execution"]
    project_path = current_run["project_path"]
    secret_files = current_run["secret_files"]
    cli_run_command = build_command(
        cmd="run",
        secret_files=secret_files,
        execution_id=execution['execution_id'],
        project_path=project_path,
    )
    cli_output_command = build_command(
        cmd="output",
        execution_id=execution['execution_id'],
        project_path=project_path,
    )
    with ui.row().classes("w-full"):
        ui.markdown(f"""
            ###### Run the Execution: 

            - Run docker images as containers
            - write output 
            """
        )
    with ui.row().classes("w-full"):    
        ui.label(cli_run_command).classes("font-mono")   
    with ui.row().classes("w-full"):  
        ui.icon("warning").classes("text-lg text-yellow")
        ui.label("""It can take a while until you see output in this step: 
        loading means just that the job is still running.""") 
    with ui.row().classes("w-full"):           
        ui.button(
            "Run execution",
            on_click=lambda: run_command(cli_run_command, dialog, result),
            icon="rocket",
        ).props("no-caps")
    with ui.row().classes("w-full"):              
        ui.button(
            "Show folder with output",
            on_click=lambda: run_command(cli_output_command, dialog, result),
            icon="info",
        ).props("no-caps")
    ui_next_back(current_run)


async def run_command(command: str, dialog, result) -> None:
    """Run a command in the background and display the output in the pre-created dialog.
    This function has been copied from nicegui examples.
    """
    logging.info(command)
    dialog.open()
    result.content = "... loading"
    # NOTE replace with machine-independent Python path (#1240)
    command = command.replace("python3", sys.executable)
    process = await asyncio.create_subprocess_exec(
        *shlex.split(command, posix="win" not in sys.platform.lower()),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    # NOTE we need to read the output in chunks, otherwise the process will block
    output = ""
    while True:
        new = await process.stdout.read(4096)
        if not new:
            break
        output += new.decode()
        # NOTE the content of the markdown element is replaced every time we have new output
        result.content = f"```\n{output}\n```"
    ui_workarea.refresh()
    ui_stepper.refresh()
