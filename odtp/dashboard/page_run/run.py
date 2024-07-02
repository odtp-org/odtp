import asyncio
import logging
import os.path
import shlex
import sys

from nicegui import ui
import odtp.dashboard.page_run.helpers as rh
import odtp.dashboard.page_run.folder as folder

log = logging.getLogger(__name__)


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
        if folder_status == rh.FOLDER_PREPARED:
            with ui.row().classes("w-full"):
                rh.ui_display_folder_status(folder_status)
        if folder_status == rh.FOLDER_EMPTY:
            execution = current_run["execution"]
            project_path = current_run["project_path"]
            cli_prepare_command = rh.build_cli_command(
                cmd="prepare",
                execution_id=execution["execution_id"],
                project_path=project_path,
            )        
            with ui.grid(columns=1):
                with ui.row().classes("w-full"):
                    ui.label(cli_prepare_command).classes("font-mono")
                with ui.row().classes("w-full"):
                    ui.button(
                        "Prepare execution",
                        on_click=lambda: run_command(cli_prepare_command, dialog, result),
                        icon="folder",
                    ).props("no-caps")
    rh.ui_next_back(current_run, ready_for_next=True)


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
    execution = current_run["execution"]
    project_path = current_run["project_path"]
    secret_files = current_run["secret_files"]
    if folder_status >= rh.FOLDER_PREPARED:
        cli_run_command = rh.build_cli_command(
            cmd="run",
            secret_files=secret_files,
            execution_id=execution["execution_id"],
            project_path=project_path,
        )
        cli_log_commands = []
        for i, _ in enumerate(execution["versions"]):
            cli_log_commands. append(rh.build_cli_command(
                cmd="logs",
                project_path=project_path,
                step_nr=str(i)
            ))
        with ui.row().classes("w-full"):
            ui.label(cli_run_command).classes("font-mono")
        with ui.row().classes("w-full"):
            ui.button(
                "Run execution",
                on_click=lambda: submit_command(cli_run_command),
                icon="rocket",
            ).props("no-caps")
        with ui.row().classes("w-full"):
            ui.icon("warning").classes("text-lg text-yellow")
            ui.label(
                """The logs for a step only become available once it is running.
                So if they are not available right away, they may be so when you 
                click the button again.
                """
            )            
        for i, cli_log_command in enumerate(cli_log_commands):    
            with ui.row().classes("w-full"):
                ui.button(
                    f"show logs for step {i}",
                    on_click=lambda cli_log_command=cli_log_command: run_command(cli_log_command, dialog, result),
                    icon="info",
                ).props("no-caps")
    rh.ui_next_back(current_run, ready_for_next=False)


async def submit_command(command):
    try:
        log.info(command)
        log.info(shlex.split(command, posix="win" not in sys.platform.lower()))
        process = await asyncio.create_subprocess_exec(
            *shlex.split(command, posix="win" not in sys.platform.lower()),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        ui.notify(f"{command} has been submitted as {process}. Click on 'Show logs to view the progress", type="positive")
    except Exception as e:
        log.exception(f"run command failed with Exception {e}")


async def run_command(command: str, dialog, result) -> None:
    """Run a command in the background and display the output in the pre-created dialog.
    This function has been copied from nicegui examples.
    """
    try:
        dialog.open()
        result.content = "... loading"
        log.info(command)
        log.info(shlex.split(command, posix="win" not in sys.platform.lower()))
        process = await asyncio.create_subprocess_exec(
            *shlex.split(command, posix="win" not in sys.platform.lower()),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        # NOTE we need to read the output in chunks, otherwise the process will block
        output = ""
        while True:
            new = await process.stdout.read(100000)
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
