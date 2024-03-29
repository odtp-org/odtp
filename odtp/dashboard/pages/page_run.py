import asyncio
import os.path
import shlex
import sys

from nicegui import ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.helpers.environment as odtp_env
from odtp.dashboard.utils.file_picker import local_file_picker


HOME_DIRECTORY_USER = "~"


def content() -> None:
    ui.markdown(
        """
        ## Prepare and Run Executions
        """
    )
    current_user = storage.get_active_object_from_storage(
        storage.CURRENT_USER
    )
    if not current_user:
        ui_theme.ui_add_first(
            item_name="user",
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
    current_execution = storage.get_active_object_from_storage(
        storage.CURRENT_EXECUTION
    )
    if not current_execution:
        ui_theme.ui_add_first(
            item_name="execution",
            page_link=ui_theme.PATH_EXECUTIONS
        )     
        return    
    with ui.dialog().props("full-width") as dialog, ui.card():
        result = ui.markdown()
        ui.button("Close", on_click=dialog.close)
    with ui.right_drawer().style("background-color: #ebf1fa").props(
        "bordered width=500"
    ):
        ui_workarea(
            current_user=current_user,
            current_digital_twin=current_digital_twin,
            current_execution=current_execution,
        )
    ui_run(dialog, result, current_execution=current_execution)


@ui.refreshable
def ui_workarea(current_user, current_digital_twin, current_execution):
    ui.markdown(
        """
        ### Work Area
        """
    )
    try:
        current_local_settings = storage.get_active_object_from_storage(
            storage.CURRENT_LOCAL_SETTINGS
        )
        if current_local_settings:
            project_path = current_local_settings.get("project_path")
        else:    
            project_path = ""
        step_names = current_execution.get("step_names")
        ui.markdown(
            f"""
            #### Current Selection
            - **user**: {current_user.get("display_name")}
            - **digital twin**: {current_digital_twin.get("name")}"
            - **execution** {current_execution.get("title")}
            - **project path**: {project_path}
            """
        )
        ui.mermaid(
            f"""
            graph TD;
                {helpers.get_workflow_mairmaid(step_names)};
            """
        )
        ui.markdown(
            f"""
            ##### Actions

            - set project folder
            - prepare execution
            - run execution 
            """
        )
    except Exception as e:
        ui.notify(f"Workarea could not be loaded: an exception occured: {e}")


async def pick_file() -> None:
    root = HOME_DIRECTORY_USER
    result = await local_file_picker(root, multiple=False)
    if result:
        project_path = result[0]
        update_local_setup(project_path=project_path)
        ui.notify(f"A new project folder has been set {project_path}", type="positive")


@ui.refreshable
def ui_run(dialog, result, current_execution):
    try:
        current_local_settings = storage.get_active_object_from_storage(
            storage.CURRENT_LOCAL_SETTINGS
        )
        execution_id = current_execution.get("execution_id")        
        with ui.row().classes("w-full no-wrap"):
            with ui.column().classes("w-1/2"):
                ui.markdown(
                    f"""
                    ##### Current project folder
                    """
                )
                if current_local_settings:
                    project_path = current_local_settings.get("project_path")
                    ui_run_form(
                        dialog=dialog,
                        result=result,
                        project_path=project_path,
                        execution_id=execution_id,
                    )
                else:
                    with ui.row():
                        ui.icon("east").classes("text-blue-800 text-lg")
                        ui.label("start with an empty folder").classes("content-center")
            with ui.column().classes("w-1/2"):
                ui.markdown(
                    f"""
                    ##### Choose project folder
                    """
                )
                ui.button("Choose folder", on_click=pick_file, icon="folder")
    except Exception as e:
        ui.notify(f"page could not be loaded: an exception occured: {e}")


def ui_run_form(execution_id, project_path, dialog, result):
    folder_empty = odtp_env.project_folder_is_empty(project_folder=project_path)
    folder_matches_execution = odtp_env.directory_folder_matches_execution(
        project_folder=project_path, execution_id=execution_id
    )
    folder_has_output = odtp_env.directory_has_output(
        execution_id=execution_id, project_folder=project_path
    )
    cli_parameters = [
        f"--project-path {project_path}",
        f"--execution-id {execution_id}",
    ]
    cli_prepare_command = f"odtp execution prepare {'  '.join(cli_parameters)}"
    cli_run_command = f"odtp execution run {'  '.join(cli_parameters)}"
    cli_output_command = f"odtp execution output {'  '.join(cli_parameters)}"
    ui.markdown(
        f"""
    ```
    {project_path}         
    ```
    """
    )
    if folder_empty:
        with ui.row():
            ui.icon("check").classes("text-green-600 text-lg")
            ui.label("start with an empty folder").classes("content-center")
        with ui.row():
            ui.icon("east").classes("text-blue-800 text-lg")
            ui.label("folder ready for prepare").classes("content-center")
        with ui.row():
            ui.button(
                "Prepare project folder",
                on_click=lambda: run_command(cli_prepare_command, dialog, result),
                icon="folder",
            ).props("no-caps")
    elif folder_matches_execution and not folder_has_output:
        with ui.row():
            ui.icon("check").classes("text-green-600 text-lg")
            ui.label("start with an empty folder").classes("content-center")
        with ui.row():
            ui.icon("check").classes("text-green-800 text-lg")
            ui.label("folder has been prepared").classes("content-center")
        with ui.row():
            ui.icon("east").classes("text-blue-800 text-lg")
            ui.label("ready for run").classes("content-center")
        with ui.row():
            ui.button(
                "Run execution",
                on_click=lambda: run_command(cli_run_command, dialog, result),
                icon="rocket",
            ).props("no-caps")
    elif folder_matches_execution and folder_has_output:
        with ui.row():
            ui.icon("check").classes("text-green-600 text-lg")
            ui.label("start with an empty folder").classes("content-center")
        with ui.row():
            ui.icon("check").classes("text-green-800 text-lg")
            ui.label("folder has been prepared").classes("content-center")
        with ui.row():
            ui.icon("check").classes("text-blue-800 text-lg")
            ui.label("execution has run").classes("content-center")
        with ui.row():
            ui.icon("east").classes("textgreen-600 text-lg")
            ui.label("check output").classes("content-center")
    else:
        with ui.row():
            ui.icon("warning").classes("text-red-800 text-lg")
            ui.label("folder is not empty").classes("content-center")
        with ui.row():
            ui.icon("warning").classes("text-red-800 text-lg")
            ui.label("folder does not match execution steps").classes("content-center")
    ui.button(
        "Check project folder",
        on_click=lambda: run_command(cli_output_command, dialog, result),
        icon="info",
    ).props("no-caps")


def update_local_setup(project_path):
    storage.storage_update_local_settings(project_path=project_path)
    ui_workarea.refresh()
    ui_run.refresh()


async def run_command(command: str, dialog, result) -> None:
    """Run a command in the background and display the output in the pre-created dialog.
    This function has been copied from nicegui examples.
    """
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
    ui_run.refresh()
