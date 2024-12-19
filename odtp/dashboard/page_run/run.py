import json
import os
import sys
import asyncio
from pprint import pprint
import odtp.dashboard.page_run.helpers as rh
import os.path
import shutil
import shlex
from slugify import slugify
from nicegui import ui, app
import odtp.mongodb.db as db
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.page_run.folder as folder
import odtp.dashboard.utils.validators as validators


from nicegui import ui

class ExecutionRunForm:
    def __init__(self, digital_twin_id, execution_id, workdir, dialog, result):
        """init form"""
        self.workdir = workdir
        self.execution_id = execution_id
        self.digital_twin_id = digital_twin_id
        self.execution_path = None
        self.dialog = dialog
        self.result = result
        self.folder_status = None
        self.get_execution()
        self.check_folder_status()
        self.build_form()

    def get_execution(self):
        if not self.execution_id:
            return
        self.execution = helpers.build_execution_with_steps(self.execution_id)
        if self.execution.get("execution_path"):
            self.execution_path = self.execution.get("execution_path")
        self.ui_execution_info.refresh()

    @ui.refreshable
    def ui_add_project_path(self):
        if not self.execution:
            return
        if self.execution_path:
            return
        project_folder_input = ui.input(
            value=self.execution_path,
            label="Project folder name",
            placeholder="execution",
            validation={
                f"Project folder already exists and is not empty": lambda value: validators.validate_folder_does_not_exist(
                    value, self.workdir
                )
            },
        )
        ui.button(
            "Create new project folder",
            on_click=lambda: self.create_folder(project_folder_input),
            icon="add",
        ).props("flat ")

    def check_folder_status(self):
        self.folder_status = rh.get_folder_status(self.execution_id, self.execution_path)

    def create_folder(self, folder_name_input):
        if self.execution_path:
            return
        if (
            not folder_name_input.validate()
        ):
            ui.notify(
                "Project folder already exists and is not empty", type="negative"
            )
            return
        folder_name = folder_name_input.value
        project_path = os.path.join(self.workdir, folder_name)
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        os.makedirs(project_path)
        self.execution_path = project_path
        db.set_execution_path(self.execution_id, execution_path=project_path)
        ui.notify(
            f"project directory {project_path} has been created and set as project directory",
            type="positive",
        )
        self.ui_add_project_path.refresh()

    @ui.refreshable
    def ui_show_project_folder(self):
        if not self.execution_path:
            return
        with ui.row().classes("w-full"):
            cli_tree_command = f"tree {self.execution_path}"
            with ui.grid(columns=1):
                #with ui.row().classes("w-full"):
                #    ui.label(cli_tree_command).classes("font-mono w-full")
                with ui.row().classes("w-full"):
                    ui.button(
                        "Show execution path",
                        on_click=lambda: self.run_command(cli_tree_command),
                        icon="folder",
                    ).props("flat")

    @ui.refreshable
    def ui_execution_info(self):
        if not self.execution_id:
            return
        with ui.expansion("execution info", icon="info"):
            ui.label(f"Run for execution {self.execution_id}")
            ui.label(f"created: {self.execution['createdAt']}")
            ui.label(f"inputs: {self.execution['inputs']}")
            ui.label(f"outputs: {self.execution['outputs']}")
            ui.label(f"ports: {self.execution['ports']}")
            ui.label(f"steps: {self.execution['steps']}")
            ui.label(f"version_tags: {self.execution['version_tags']}")
            ui.label(f"versions: {self.execution['versions']}")
            ui.label(f"path: {self.execution.get('execution_path')}")

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_execution_info()
        self.ui_add_project_path()
        self.ui_display_folder_status()
        self.ui_prepare_execution()
        self.ui_show_project_folder()
        self.ui_run_execution()

    def ui_prepare_execution(self):
        if not self.execution_path:
            return
        if self.folder_status == rh.FOLDER_PREPARED:
            return
        with ui.row().classes("w-full"):
            cli_prepare_command = rh.build_cli_command(
                cmd="prepare",
                execution_id=self.execution_id,
                project_path=self.execution_path,
            )
            with ui.grid(columns=1):
                #with ui.row().classes("w-full"):
                #    ui.label(cli_prepare_command).classes("font-mono w-full")
                with ui.row().classes("w-full"):
                    ui.button(
                        "Prepare execution",
                        on_click=lambda: self.run_command(cli_prepare_command),
                        icon="folder",
                    ).props("no-caps")


    def ui_run_execution(self):
        if not self.execution_path:
            return
        if self.folder_status != rh.FOLDER_PREPARED:
            return
        with ui.row().classes("w-full"):
            cli_run_command = rh.build_cli_command(
                cmd="run",
                execution_id=self.execution_id,
                project_path=self.execution_path,
            )
            with ui.grid(columns=1):
                with ui.row().classes("w-full"):
                    ui.label(cli_run_command).classes("font-mono w-full")
                with ui.row().classes("w-full"):
                    ui.button(
                        "Run execution",
                        on_click=lambda: self.run_command(cli_run_command),
                        icon="folder",
                    ).props("no-caps")

    @ui.refreshable
    def ui_display_folder_status(self):
        if not self.execution_path:
            return
        with ui.grid(columns='1fr 7fr'):
            if self.folder_status == rh.FOLDER_EMPTY:
                ui.icon("check").classes("text-teal text-lg")
                ui.label("Project folder for the execution run has been selected").classes("text-teal")
            elif self.folder_status == rh.FOLDER_NOT_SET:
                ui.icon("clear").classes("text-red text-lg")
                ui.label("Project folder missing: please select one").classes("text-red")
            elif self.folder_status == rh.FOLDER_DOES_NOT_MATCH:
                ui.icon("clear").classes("text-red text-lg")
                ui.label("The project folder structure does not match the steps of the execution: choose an empty project folder or create a new project folder").classes("text-red")
            elif self.folder_status == rh.FOLDER_PREPARED:
                ui.icon("check").classes("text-teal text-lg")
                ui.label("Project folder for the execution run has been selected").classes("text-teal")
                ui.icon("check").classes("text-teal text-lg")
                ui.label("The execution has been prepared").classes("text-teal")
            elif self.folder_status == rh.FOLDER_HAS_OUTPUT:
                ui.icon("check").classes("text-teal text-lg")
                ui.label("Project folder for the execution run has been selected").classes("text-teal")
                ui.icon("check").classes("text-teal text-lg")
                ui.label("The execution has been prepared").classes("text-teal")
                ui.icon("check").classes("text-teal text-lg")
                ui.label("The execution has been run").classes("text-teal")

    async def run_command(self, command: str):
        try:
            self.dialog.open()
            self.result.content = "... loading"
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
                self.result.content = f"```\n{output}\n```"
        except Exception as e:
            print(f"run command failed with Exception {e}")
        else:
            self.check_folder_status()
            self.ui_display_folder_status.refresh()
            self.ui_execution_info.refresh()
            self.build_form.refresh()
