import asyncio
import os.path
import shlex
import json
import sys
import logging

from nicegui import ui, app

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.validators as validators
import odtp.helpers.environment as odtp_env
from odtp.dashboard.utils.file_picker import local_file_picker


STEPPERS = (
    "Select Execution",
    "Add Secret Files",
    "Select Folder",
    "Prepare Execution (Build Images)", 
    "Run Execution (Run Containers)",
    "Check Output"
)

STEPPER_SELECT_EXECUTION = 0
STEPPER_ADD_SECRETS = 1
STEPPER_SELECT_FOLDER = 2
STEPPER_PREPARE_EXECUTION = 3
STEPPER_RUN_EXECUTION = 4
STEPPER_CHECK_OUTPUT = 5


FOLDER_EMPTY = "empty"
FOLDER_PREPARED = "prepared"
FOLDER_HAS_OUTPUT = "output"
FOLDER_DOES_NOT_MATCH = "no_match"


folder_status_msg = {
   FOLDER_EMPTY: "Empty project folder: ready for Execution prepare",
   FOLDER_PREPARED: "Project folder has been set up for Execution run",
   FOLDER_HAS_OUTPUT: "Project folder has output: Check Output",
   FOLDER_DOES_NOT_MATCH: "Project Folder is not empty and does not match the Execution: Choose another project folder" 
}


def content() -> None:
    ui.markdown(
        """
        ## Prepare and Run Executions
        """
    )
    current_user = storage.get_active_object_from_storage(
        storage.CURRENT_USER
    )
    workdir = storage.get_value_from_storage_for_key(
        storage.CURRENT_USER_WORKDIR
    )    
    if not current_user:
        ui_theme.ui_add_first(
            item_name="user",
            page_link=ui_theme.PATH_USERS
        )     
        return
    if not workdir:
        ui_theme.ui_add_first(
            item_name="workdir",
            page_link=ui_theme.PATH_USERS
        )     
        return        
    current_digital_twin = storage.get_active_object_from_storage(
        storage.CURRENT_DIGITAL_TWIN
    )
    if not current_digital_twin:
        ui_theme.ui_add_first(
            item_name="digital twin",
            page_link=ui_theme.PATH_DIGITAL_TWINS
        )     
        return    
    with ui.dialog().props("full-width") as dialog, ui.card():
        result = ui.markdown()
        ui.button("Close", on_click=dialog.close)
    with ui.right_drawer().classes("bg-slate-50").props(
        "bordered width=500"
    ):
        ui_workarea(
            current_user=current_user,
            current_digital_twin=current_digital_twin,
            workdir=workdir
        )
    #ui_run(dialog, result, current_execution=current_execution, workdir=user_workdir)
    ui_stepper(
        dialog,
        result,
        current_digital_twin=current_digital_twin,
        workdir=workdir
    )


@ui.refreshable
def ui_workarea(current_user, current_digital_twin, workdir):
    ui.markdown(
        """
        ### Work Area
        """
    )
    try:
        project_path = storage.get_value_from_storage_for_key(
            storage.CURRENT_PROJECT_PATH)
        execution = storage.get_active_object_from_storage(
            storage.EXECUTION_FOR_RUN
        )  
        secrets_files = storage.get_active_object_from_storage(
            storage.SECRETS_FILES
        )  
        stepper = storage.get_value_from_storage_for_key(
            storage.RUN_STEP
        )
        with ui.expansion('General Settings'):
            ui.markdown(
                f"""
                #### General Settings
                - **user**: {current_user.get("display_name")}
                - **digital twin**: {current_digital_twin.get("name")}"
                - **working directory**: {workdir}
                """
            )
        ui_check_status(
            execution, 
            project_path,
            secrets_files,
        )
    except Exception as e:
        ui.notify(f"an exception occurred {e}")    


@ui.refreshable 
def ui_stepper(dialog, result, current_digital_twin, workdir):
    project_path = storage.get_value_from_storage_for_key(
        storage.CURRENT_PROJECT_PATH) 
    execution = storage.get_active_object_from_storage(
        storage.EXECUTION_FOR_RUN
    )  
    secrets_files = storage.get_active_object_from_storage(
        storage.SECRETS_FILES
    ) 
    stepper = storage.get_value_from_storage_for_key(
        storage.RUN_STEP
    )
    digital_twin_id = current_digital_twin["digital_twin_id"]           
    with ui.stepper(value=STEPPERS[stepper]).props('vertical').classes('w-full') as stepper:
        with ui.step(STEPPERS[STEPPER_SELECT_EXECUTION]):
            with ui.stepper_navigation():
                ui.button('Next', on_click=stepper.next)             
            ui_execution_select(execution, digital_twin_id, stepper) 
            ui_execution_details()          
        with ui.step(STEPPERS[STEPPER_ADD_SECRETS]):
            with ui.stepper_navigation():
                with ui.row():
                    ui_add_secrets_form(execution, workdir, secrets_files, stepper)
                with ui.row():
                    ui.button('Next', on_click=stepper.next)
                    ui.button('Back', on_click=stepper.previous).props('flat')                 
        with ui.step(STEPPERS[STEPPER_SELECT_FOLDER]):
            with ui.row():
                ui_prepare_folder(workdir, project_path)
            with ui.stepper_navigation():
                ui.button('Next', on_click=stepper.next) 
                ui.button('Back', on_click=stepper.previous).props('flat')                              
        with ui.step(STEPPERS[STEPPER_PREPARE_EXECUTION]):
            with ui.stepper_navigation():
                ui_prepare_execution(
                    dialog=dialog,
                    result=result,
                    project_path=project_path,
                    execution=execution,
                )
            with ui.stepper_navigation():
                ui.button('Next', on_click=stepper.next)
                ui.button('Back', on_click=stepper.previous).props('flat')                
        with ui.step(STEPPERS[STEPPER_RUN_EXECUTION]):
            with ui.stepper_navigation():
                ui_run_execution(
                    dialog=dialog,
                    result=result,
                    project_path=project_path,
                    execution=execution,
                    secrets_files=secrets_files,
                )
            with ui.stepper_navigation():
                ui.button('Next', on_click=stepper.next)
                ui.button('Back', on_click=stepper.previous).props('flat')
        with ui.step(STEPPERS[STEPPER_CHECK_OUTPUT]):
            ui_check_output(
                dialog=dialog,
                result=result,
                project_path=project_path,
                execution=execution,
            )
            with ui.stepper_navigation():
                ui.button('Done', on_click=lambda: ui.notify('Yay!', type='positive'))
                ui.button('Back', on_click=stepper.previous).props('flat')    


def ui_execution_select(current_execution, digital_twin_id, stepper):
    if current_execution:
        selected_value = current_execution["execution_id"]
    else:
        selected_value = None 
    execution_options = helpers.get_execution_select_options(
        digital_twin_id=digital_twin_id)    
    if execution_options:
        ui.select(
            execution_options,
            value=selected_value,
            label="executions",
            on_change=lambda e: store_selected_execution(e.value, stepper),
            with_input=True,
        ).classes("w-full")  
    ui.button(
        "Cancel Execution Selection",
        on_click=lambda: cancel_execution_selection(stepper),
        icon="cancel",
    )


def ui_add_secrets_form(execution, workdir, secrets_files, stepper):
    if not execution: 
        return              
    version_tags = execution.get("version_tags")
    if not version_tags:
        return  
    with ui.column():   
        for j, version_tag in enumerate(version_tags):
            if secrets_files and secrets_files.get("secret_files"):
                secrets_file_display = secrets_files["secret_files"][j]
            else:
                secrets_file_display = ""    
            with ui.row():
                ui.markdown(
                    f"""
                    **{version_tag}**: 
                    """
                )           
                ui.button(
                    f"Pick secrets file for {version_tag}", 
                    on_click=lambda step_nr=j: pick_secrets_file(
                        step_nr,
                        workdir=workdir,
                        execution=execution,
                    ), 
                    icon="key"
                ).props('flat') 
            with ui.row():  
                if secrets_file_display:  
                    ui.icon("key")  
                    ui.label(secrets_file_display)            
    with ui.row().classes("w-full"):                
        ui.button(
            f"Reset secrets files", 
            on_click=lambda: remove_secrets_files(stepper), 
            icon="clear"
        ).props('flat')                 
             

async def pick_secrets_file(step_nr, workdir, execution) -> None:
    root = workdir
    result = await local_file_picker(root, multiple=False)
    if result:
        file_path = result[0]
        current_secrets_files = storage.get_active_object_from_storage(storage.SECRETS_FILES)
        if not current_secrets_files:
            step_count = len(execution.get("steps"))
            current_secrets_files = {
                "execution_id": execution["execution_id"],
                "secret_files": ["" for i in range(step_count) ],
            }
        current_secrets_files["secret_files"][step_nr] = file_path
        app.storage.user[storage.SECRETS_FILES] = json.dumps(current_secrets_files)
    app.storage.user[storage.RUN_STEP] = STEPPER_ADD_SECRETS    
    ui_stepper.refresh()
    ui_workarea.refresh()


def remove_secrets_files(stepper) -> None:
    if stepper != STEPPER_SELECT_EXECUTION:
        #app.storage.user[storage.RUN_STEP] = STEPPER_ADD_SECRETS
        pass
    else:
        app.storage.user[storage.RUN_STEP] = STEPPER_SELECT_EXECUTION 
    storage.reset_storage_delete([storage.SECRETS_FILES])
    ui_stepper.refresh() 
    ui_workarea.refresh()   


@ui.refreshable
def ui_execution_details():
    try:
        current_execution = storage.get_active_object_from_storage(
            storage.EXECUTION_FOR_RUN
        )
        if not current_execution:
            return
        execution_title = current_execution.get('title')
        version_tags = current_execution.get("version_tags")
        current_ports = current_execution.get("ports")
        current_parameters = current_execution.get("parameters")        
        ui_theme.ui_execution_display(
            execution_title=execution_title,
            version_tags=version_tags,
            ports=current_ports,
            parameters=current_parameters,
        )         
    except Exception as e:
        ui.notify(
            f"Execution details could not be loaded. An Exception occurred: {e}",
            type="negative",
        )


def ui_prepare_folder(workdir, project_path):
    if project_path:
        with ui.row().classes("w-full"):
            ui.markdown(
                f"""
                - **project path**: {project_path}
                """
            )       
    with ui.row().classes("w-full"):    
        ui.button(
            "Choose other project folder", 
            on_click=lambda: pick_folder(workdir), 
            icon="folder"
        ).props('flat')  
    with ui.row().classes("w-full"):       
        project_folder_input = ui.input(
            label="Project folder name", 
            placeholder="execution",
            validation={f"Please provide a folder name does not yet exist in the working directory":
                lambda value: validators.validate_folder_does_not_exist(value, workdir)},                
        )      
        ui.button(
            "Create new project folder", 
            on_click=lambda: create_folder(workdir, project_folder_input), 
            icon="add",
        ).props('flat')                    


def cancel_execution_selection(stepper):
    storage.reset_storage_delete([storage.EXECUTION_FOR_RUN])
    ui_stepper.refresh()
    ui_workarea.refresh()


async def pick_folder(workdir) -> None:
    root = workdir
    result = await local_file_picker(root, multiple=False)
    if result:
        project_path = result[0]
        app.storage.user[storage.CURRENT_PROJECT_PATH] = project_path
        ui.notify(f"A new project folder has been set {project_path}", type="positive")
        ui_workarea.refresh()
        ui_stepper.refresh()


def create_folder(workdir, folder_name_input):
    if not folder_name_input.validate():
        return
    try:
        folder_name = folder_name_input.value
        project_path = os.path.join(workdir, folder_name)
        os.mkdir(project_path)
    except Exception as e:
        ui.notify(f"The project directory could not be created: an exception occurred: {e}", type="negative")
    else:        
        app.storage.user[storage.CURRENT_PROJECT_PATH] = project_path
        ui.notify(
            f"project directory {project_path} has been created and set as project directory", type="positive")
        ui_workarea.refresh()
        ui_stepper.refresh()
 

def set_stepper(stepper):
    app.storage.user[storage.RUN_STEP] = stepper 
    ui_workarea.refresh()
    ui_stepper.refresh()


def get_folder_status(project_path, execution):
    execution_id = execution["execution_id"]
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


def ui_check_status(execution, project_path, secrets_files):  
    folder_status = get_folder_status(project_path, execution)   
    if not execution:
        with ui.row():
            ui.icon("east").classes("text-blue-800 text-lg")
            ui.label("NEXT: Select Execution").classes("content-center")  
    with ui.row(): 
        ui.markdown(               
            f"""
            #### Access Steps"""
        )   
    with ui.column():                   
        ui.button(
            "Select Execution", 
            on_click=lambda: set_stepper(STEPPER_SELECT_EXECUTION), 
            icon="east",
        ).props('flat')                          
        ui.button(
            "Add secrets", 
            on_click=lambda: set_stepper(STEPPER_ADD_SECRETS), 
            icon="east",
        ).props('flat') 
        ui.button(
            "Select Folder", 
            on_click=lambda: set_stepper(STEPPER_SELECT_FOLDER), 
            icon="east",
        ).props('flat')  
    if folder_status == FOLDER_EMPTY:
        ui.button(
            "Prepare Execution", 
            on_click=lambda: set_stepper(STEPPER_PREPARE_EXECUTION), 
            icon="east",
        )
    elif folder_status == FOLDER_PREPARED:
        ui.button(
            "Run Execution", 
            on_click=lambda: set_stepper(STEPPER_RUN_EXECUTION), 
            icon="east",
        ) 
    elif folder_status == FOLDER_HAS_OUTPUT:
        ui.button(
            "Check Output", 
            on_click=lambda: set_stepper(STEPPER_CHECK_OUTPUT), 
            icon="east",
        )                                                             
    if execution:
        with ui.row(): 
            ui.markdown(               
                f"""
                #### Run Settings"""
            )
        with ui.row():
            with ui.expansion('Select Execution', icon="check").classes('text-green-800'):
                with ui.row():     
                    with ui.card():                       
                        ui.markdown(
                            f""" 
                            ###### Selected Execution
                            - **Execution**: {execution.get("title")}
                            - **Steps**: {execution.get("version_tags")}
                            """
                        ).classes("w-full")                   
    if secrets_files:
        with ui.row():
            with ui.expansion('Add Secret Files', icon="check").classes('text-green-800'): 
                with ui.row():    
                    with ui.card():                       
                        ui.markdown(
                            f""" 
                            ###### Secret Files 

                            - **secret files** {secrets_files["secret_files"]}
                            """
                        )
    else:
        with ui.row():
            ui.icon("info").classes("text-blue-800 text-lg")
            ui.label("Secrets have not been added")                           
    if project_path:
        folder_status = get_folder_status(project_path, execution) 
        with ui.row():
            with ui.expansion('Select Folder', icon="check").classes('text-green-800'):        
                with ui.row():
                    with ui.card():
                        ui.markdown(
                            f"""
                            ###### Project Folder

                            - **project path**: {project_path}
                            """
                        )  
            ui.markdown(f"""
            - Folder: **{folder_status}**

            {folder_status_msg[folder_status]}
            """
            )                       
    
      
def store_selected_execution(value, stepper):
    execution_id = value
    try:
        storage.store_execution_selection(storage.EXECUTION_FOR_RUN, value)   
    except Exception as e:
        logging.error(
            f"Selected execution could not be stored. An Exception occurred: {e}"
        )
    else:
        app.storage.user[storage.RUN_STEP] = STEPPER_SELECT_EXECUTION
        remove_secrets_files(stepper)
        ui_stepper.refresh()
        ui_workarea.refresh()


def ui_prepare_execution(dialog, result, project_path, execution):
    if not execution:
        return
    if not project_path:
        return  
    cli_parameters = [
        f"--project-path {project_path}",
        f"--execution-id {execution['execution_id']}",
    ]  
    cli_prepare_command = f"odtp execution prepare {'  '.join(cli_parameters)}"   
    logging.info(cli_prepare_command)    
    with ui.row().classes("w-full"):
        ui.markdown(f"""
            ###### Prepare the Execution: 

            - clone github repo
            - build Docker images 
            - create folder structure
            """
        ) 
        ui.label(cli_prepare_command).classes("font-mono")        
    with ui.row().classes("w-full"):         
        ui.button(
            "Prepare execution",
            on_click=lambda: run_command(cli_prepare_command, dialog, result),
            icon="folder",
        ).props("no-caps")   


def ui_run_execution(dialog, result, project_path, execution, secrets_files):
    if not execution:
        return
    if not project_path:
        return  
    cli_parameters = [
        f"--project-path {project_path}",
        f"--execution-id {execution['execution_id']}",
    ] 
    secrets_files_match = (secrets_files and secrets_files.get("secret_files") and (
        secrets_files["execution_id"] == execution['execution_id'])
    )
    if secrets_files_match:
        secrets_files_for_run = ",".join(secrets_files['secret_files'])   
        cli_parameters.append(
            f"--secrets-files {secrets_files_for_run}",
        )     
        logging.info("secrets matched")
    else: 
        logging.info("secrets did not matched")       
    cli_run_command = f"odtp execution run {'  '.join(cli_parameters)}"   
    logging.info(cli_run_command)    
    with ui.row().classes("w-full"):
        ui.markdown(f"""
            ###### Run the Execution: 

            - Run docker images as containers
            - write output 
            """
        )
        ui.label(cli_run_command).classes("font-mono")   
    with ui.row().classes("w-full"):         
        ui.button(
            "Run execution",
            on_click=lambda: run_command(cli_run_command, dialog, result),
            icon="rocket",
        ).props("no-caps") 


def ui_check_output(dialog, result, project_path, execution):
    if not execution:
        return
    if not project_path:
        return  
    cli_parameters = [
        f"--project-path {project_path}",
        f"--execution-id {execution['execution_id']}",
    ]  
    cli_output_command = f"odtp execution output {'  '.join(cli_parameters)}" 
    ui.label(cli_output_command).classes("font-mono")    
    logging.info(cli_output_command)    
    with ui.row().classes("w-full"):
        ui.markdown(f"""
            ###### Check output: 

            - check output of the execution
            """
        )  
    with ui.row().classes("w-full"):              
        ui.button(
            "Check output",
            on_click=lambda: run_command(cli_output_command, dialog, result),
            icon="info",
        ).props("no-caps")              


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
