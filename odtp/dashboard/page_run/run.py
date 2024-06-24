import asyncio
import logging
import os.path
import shlex
import sys

from nicegui import ui
import odtp.helpers.settings as config
import odtp.dashboard.page_run.helpers as rh
import odtp.dashboard.page_run.folder as folder

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(config.command_log_handler)


def ui_prepare_execution(dialog, result, current_run, folder_status):
    stepper = current_run.get("stepper")
    if stepper and rh.STEPPERS.index(stepper) != rh.STEPPER_PREPARE_EXECUTION:
        return
    with ui.row().classes("w-full"):
        ui.markdown(
            f"""
            ###### Prepare the Execution: 

            - clone github repo
            - build Docker images 
            - create folder structure
            """
        )
    with ui.row().classes("w-full"):
        if folder_status == folder.FOLDER_EMPTY:
            ui.icon("check").classes("text-teal text-lg")
            ui.label("Project folder for the execution run has been selected").classes("text-teal") 
        elif folder_status == folder.FOLDER_NOT_SET:
            ui.icon("clear").classes("text-red text-lg")
            ui.label("Project folder missing: please select one").classes("text-red") 
        elif folder_status == folder.FOLDER_DOES_NOT_MATCH:
            ui.icon("clear").classes("text-red text-lg")
            ui.label("The project folder structure does not match the steps of the execution: choose an empty project folder or create a new project folder").classes("text-red")  
        elif folder_status == folder.FOLDER_PREPARED:
            ui.icon("check").classes("text-teal text-lg")
            ui.label("The execution has been prepared").classes("text-teal")      
        elif folder_status == folder.FOLDER_HAS_OUTPUT:
            ui.icon("check").classes("text-teal text-lg")
            ui.label("The execution has been run").classes("text-teal")   
        folder_matches = folder_status in [
            folder.FOLDER_EMPTY,
            folder.FOLDER_HAS_OUTPUT,
            folder.FOLDER_PREPARED,
        ]
        if folder_matches:
            execution = current_run["execution"]
            project_path = current_run["project_path"]    
            cli_output_command = build_command(
                cmd="output",
                execution_id=execution["execution_id"],
                project_path=project_path,
            ) 
        if folder_status == folder.FOLDER_EMPTY:                                   
            cli_prepare_command = build_command(
                cmd="prepare",
                execution_id=execution["execution_id"],
                project_path=project_path,
            )        
    with ui.grid(columns=1):
        if folder_status == folder.FOLDER_EMPTY:
            with ui.row().classes("w-full"):
                ui.label(cli_prepare_command).classes("font-mono")
            with ui.row().classes("w-full"):    
                ui.button(
                    "Prepare execution",
                    on_click=lambda: run_command(cli_prepare_command, dialog, result),
                    icon="folder",
                ).props("no-caps")
        if folder_matches:        
            with ui.row().classes("w-full"):
                ui.button(
                    "Show project folder",
                    on_click=lambda: run_command(cli_output_command, dialog, result),
                    icon="info",
                ).props("no-caps")
    rh.ui_next_back(current_run)


def build_command(cmd, project_path, execution_id, secret_files=None):
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


def get_docker_command(execution_id):   
    cli_parameters = [
        f"--execution-id {execution_id}",
    ]    
    cli_command = f"odtp execution docker_container {'  '.join(cli_parameters)}"
    return cli_command

def ui_run_execution(dialog, result, current_run, folder_status):
    stepper = current_run.get("stepper")
    if stepper and rh.STEPPERS.index(stepper) != rh.STEPPER_RUN_EXECUTION:
        return
    with ui.row().classes("w-full"):
        ui.markdown(
            f"""
            ###### Run the Execution: 

            - Run docker images as containers
            - write output 
            """
        )  
    msg = ""          
    if folder_status == folder.FOLDER_DOES_NOT_MATCH:
        msg = """The project folder structure does not match the steps of the execution: 
        choose an empty project folder and prepare the execution before you can run it."""
        text_color = "text-red"
    elif folder_status == folder.FOLDER_NOT_SET:
        msg = """The project folder has not been set: 
        Select an empty project folder and prepare the execution before you can run it."""
        text_color = "text-red"   
    elif folder_status == folder.FOLDER_EMPTY:
        msg = """The project folder is empty: 
        Prepare the execution before you can run it."""
        text_color = "text-red"                    
    if msg:             
        ui.label(msg).classes(text_color)
        rh.ui_next_back(current_run, ready_for_next=False)
        return 
    if folder_status == folder.FOLDER_HAS_OUTPUT:
        msg = """The execution has already been run and the project folder has output."""
        text_color = "text-teal"  
    else:         
        msg = """The execution is ready to run."""
        text_color = "text-teal" 
    ui.label(msg).classes(text_color)   
    execution = current_run["execution"]
    project_path = current_run["project_path"]
    secret_files = current_run["secret_files"]
    if folder_status != folder.FOLDER_HAS_OUTPUT:
        cli_run_command = build_command(
            cmd="run",
            secret_files=secret_files,
            execution_id=execution["execution_id"],
            project_path=project_path,
        )
        with ui.row().classes("w-full"):
            ui.label(cli_run_command).classes("font-mono")
        with ui.row().classes("w-full"):
            ui.icon("warning").classes("text-lg text-yellow")
            ui.label(
                """It can take a while until you see output in this step: 
            loading means just that the job is still running."""
            )
        with ui.row().classes("w-full"):
            ui.button(
                "Run execution",
                on_click=lambda: run_command(cli_run_command, dialog, result),
                icon="rocket",
            ).props("no-caps")
    else:    
        cli_output_command = build_command(
            cmd="output",
            execution_id=execution["execution_id"],
            project_path=project_path,
        )
        with ui.row().classes("w-full"):
            ui.button(
                "Show folder with output",
                on_click=lambda: run_command(cli_output_command, dialog, result),
                icon="info",
            ).props("no-caps")
    rh.ui_next_back(current_run, ready_for_next=False)


async def run_command(command: str, dialog, result) -> None:
    """Run a command in the background and display the output in the pre-created dialog.
    This function has been copied from nicegui examples.
    """
    try:
        dialog.open()
        result.content = "... loading"
        # NOTE replace with machine-independent Python path (#1240)
        command = command.replace("python3", sys.executable)
        log.info(command)
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
    except Exception as e:
        log.exception(f"run command failed with Exception {e}")
    else:        
        from odtp.dashboard.page_run.main import ui_workarea, ui_stepper    
        ui_workarea.refresh()
        ui_stepper.refresh()
