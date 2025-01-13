import asyncio
import os.path
import shlex
import sys
import re
import os
from nicegui import ui
import odtp.mongodb.db as db
import odtp.helpers.utils as odtp_utils
from odtp.helpers.settings import ODTP_SECRETS_DIR
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.page_executions.projectdir as projectdir
import odtp.dashboard.page_executions.run as run
from odtp.helpers.settings import ODTP_SECRETS_DIR, ODTP_LOG_PATH


from nicegui import ui

class ExecutionDisplay:
    def __init__(self, current_user, current_digital_twin, dialog, result):
        """init form"""
        self.dialog = dialog
        self.result = result
        self.execution = None
        self.versions_dict = None
        self.steps = None
        self.workflow = None
        self.execution_id = None
        self.execution_path = None
        self.user = current_user
        self.digital_twin = current_digital_twin
        self.execution_options = None
        self.folder_status = None
        self.run = None
        self.get_execution_options()
        self.build_form()

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.db_get_execution()
        self.ui_execution_select()
        self.ui_execution_run_info()
        self.ui_workflow_diagram()
        self.ui_execution_info()
        self.ui_project_directory()
        self.ui_prepare_execution()
        self.ui_run_execution()

    def ui_execution_info(self):
        if not self.execution:
            return
        for index, step in enumerate(self.steps):
            self._display_step(step, index)

    def ui_execution_run_info(self):
        if not self.execution:
            return
        with ui.row().classes('w-full gap-10'):
            ui.icon("schedule").classes("text-xl")
            ui.label(f"created {self.execution['createdAt'].strftime(f'%Y-%m-%d %H:%M:%S')}")
            if self.execution.get('start_timestamp'):
                ui.label(f"started {self.execution['start_timestamp'].strftime(f'%Y-%m-%d %H:%M:%S')}")
            if self.execution.get('end_timestamp'):
                ui.label(f"ended {self.execution['end_timestamp'].strftime(f'%Y-%m-%d %H:%M:%S')}")

    def get_execution_options(self):
        """get execution options"""
        executions = db.get_sub_collection_items(
            collection=db.collection_digital_twins,
            sub_collection=db.collection_executions,
            item_id=self.digital_twin["digital_twin_id"],
            ref_name=db.collection_executions,
            sort_by=[("createdAt", db.DESCENDING)],
            include_deprecated=False,
        )
        self.execution_options = {}
        if not executions:
            return
        for execution in executions:
            self.execution_options[str(execution["_id"])] = (
                f"{execution['createdAt'].strftime('%d/%m/%y')} {execution.get('title')}"
            )

    @ui.refreshable
    def ui_prepare_execution(self):
        if not self.execution_path:
            return
        if self.folder_status >= run.FOLDER_PREPARED:
            with ui.row():
                ui.icon("check").classes("text-teal text-lg")
                ui.label("The execution has been prepared").classes("text-teal")
        if self.folder_status != run.FOLDER_EMPTY:
            return
        command = run.build_cli_command(
            cmd="prepare",
            execution_id=self.execution_id,
            project_path=self.execution_path,
        )
        ui.label(command).classes("font-mono w-full")
        ui.button(
            "Prepare Execution",
            on_click=lambda: self.action_run_command(command, self.dialog, self.result),
            icon="folder",
        )

    @ui.refreshable
    def ui_run_execution(self):
        if not self.execution_path:
            return
        if not self.folder_status >= run.FOLDER_PREPARED:
            return
        if self.execution.get("start_timestamp"):
            with ui.row():
                ui.icon("check").classes("text-teal text-lg")
                ui.label("The execution has run").classes("text-teal")
        if not True in self.run:
            return
        command = run.build_cli_command(
            cmd="run",
            execution_id=self.execution_id,
            project_path=self.execution_path,
        )
        ui.label(command).classes("font-mono w-full")
        ui.button(
            "Run Execution",
            on_click=lambda: self.action_run_command(command, self.dialog, self.result),
            icon="rocket",
        )

    @ui.refreshable
    def ui_open_logs(self, version_name):
        log_file_path = f"{self.execution_path}/{version_name}/{ODTP_LOG_PATH}"
        if not os.path.exists(log_file_path):
            return
        command = f"cat {log_file_path}"
        ui.button(
            "Show logs",
            on_click=lambda: self.action_run_command(command, self.dialog, self.result),
            icon="receipt_long",
        )

    @ui.refreshable
    def ui_project_directory(self):
        if not self.execution:
            return
        if self.execution_path and self.folder_status >= run.FOLDER_EMPTY:
            with ui.row():
                ui.icon("check").classes("text-teal text-lg")
                ui.label("Project folder for the execution run has been created").classes("text-teal")
                ui.label(self.execution_path)
            return
        if self.folder_status < run.FOLDER_EMPTY:
            ui.button(
                "Create execution directory",
                on_click=lambda: self.action_create_folder(),
                icon="add",
            )

    def action_create_folder(self):
        execution_path = projectdir.make_project_dir_for_execution(
            self.user["workdir"],
            self.digital_twin["digital_twin_name"],
            self.execution["title"]
        )
        db.set_execution_path(self.execution_id, execution_path=execution_path)
        ui.notify(
            f"project directory {execution_path} has been created and set as project directory",
            type="positive",
        )
        self.execution_path = execution_path
        self.build_form.refresh()

    @ui.refreshable
    def ui_execution_select(self):
        """ui element for component select"""
        with ui.row().classes("w-full items-center"):
            ui.select(
                self.execution_options,
                value=self.execution_id,
                on_change=lambda e: self.action_set_execution(str(e.value)),
                label="execution",
                with_input=True,
            ).classes("w-2/3")
            if not self.execution_id:
                return
            ui.button(
                "Reload execution",
                on_click=lambda: self.build_form.refresh(),
                icon="refresh",
            )

    def action_set_execution(self, execution_id):
        """called when a new component has been selected"""
        self.execution_id = execution_id
        self.build_form.refresh()

    def db_get_execution(self):
        if not self.execution_id:
            return
        self.execution = db.get_document_by_id(
            document_id=self.execution_id, collection=db.collection_executions
        )
        self.execution["_id"] = str(self.execution["_id"])
        self.execution["digitalTwinRef"] = str(self.execution["digitalTwinRef"])
        self.workflow = db.get_document_by_id(
            document_id=self.execution["workflow_id"], collection=db.collection_workflows
        )
        self.workflow["_id"] = str(self.workflow["_id"])
        self.versions = db.get_document_by_ids_in_collection(
            document_ids=self.workflow.get("versions", []),
            collection=db.collection_versions
        )
        self.versions_dict = { str(version["_id"]): version  for version in self.versions }
        step_ids = [str(step_id) for step_id in self.execution["steps"]]
        self.steps = db.get_document_by_ids_in_collection(
            document_ids=step_ids, collection=db.collection_steps
        )
        self.run = []
        for step in self.steps:
            step["_id"] = str(step["_id"])
            if step.get("run_step"):
                self.run.append(True)
            else:
                self.run.append(False)
            if step.get("output"):
                step["output"] = db.get_document_by_id(str(step["output"]), db.collection_outputs)
        self.execution_path = self.execution.get("execution_path")
        self.folder_status = run.get_folder_status(self.execution_id, self.execution_path)

    @ui.refreshable
    def ui_workflow_diagram(self, init="graph LR;"):
        if not self.execution:
           return
        version_names = []
        for index, version_id in enumerate(self.workflow.get("versions", [])):
            version = self.versions_dict[version_id]
            version_names.append(self._get_version_display(version, index))
        return ui.mermaid(
            f"""
            {helpers.get_workflow_mermaid(version_names, init='graph LR;')}"""
        ).classes("w-full")

    def _get_version_display(self, version, index):
        return odtp_utils.get_execution_step_name(
            version['component']['componentName'],
            version['component_version'],
            index
        )

    def action_update_step(self, value, step, index):
        db.update_step(step["_id"], {"run_step":value})
        if value == True:
            self.run[index] = True
        else:
            self.run[index] = False
        self.ui_run_execution.refresh()

    def _display_step(self, step, index):
        """Display information for a single step."""
        version = self.versions_dict.get(step["component_version"])
        version_name = self._get_version_display(version, index)
        with ui.card().classes("w-full bg-gray-100"):
            with ui.grid(columns=3).classes("flex items-center"):
                ui.label(version_name).classes("text-lg")
            with ui.grid(columns=3).classes("flex items-center"):
                ui.icon("schedule").classes("text-xl")
                if self.execution.get('start_timestamp'):
                    ui.label(f"started {self.execution['start_timestamp'].strftime(f'%Y-%m-%d %H:%M:%S')}")
                if self.execution.get('end_timestamp'):
                    ui.label(f"ended {self.execution['end_timestamp'].strftime(f'%Y-%m-%d %H:%M:%S')}")
                self.ui_open_logs(version_name)
                if self.execution["start_timestamp"]:
                    ui.switch(
                        'Re run step',
                        value=step.get("run_step"),
                        on_change=lambda e, step=step, index=index: self.action_update_step(e.value, step, index),
                    )
            if step.get("output"):
                with ui.grid(columns=3).classes("flex items-center"):
                    ui.icon("output").classes("text-teal text-lg")
                    ui.label(f"output: {step['output'].get('file_name')} ({step['output'].get('file_size')})")
                    ui.label(f"S3: {step['output'].get('s3_bucket')} ({step['output'].get('s3_key')})")
            with ui.grid(columns=3).classes("flex items-center"):
                if step.get("secrets"):
                    ui.icon("check").classes("text-teal text-lg")
                    ui.label(f"Secrets uploaded: {step.get('secrets')}")
            with ui.grid(columns=3).classes("flex items-center"):
                if step.get("error"):
                    ui.icon("clear").classes("text-red text-lg")
                    ui.label(f"ERROR: {step.get('msg')}").classes("text-red")
                else:
                    container_running = run.check_container_running(version_name)
                    if container_running and step.get("type") == "ephemeral":
                        ui.icon("check").classes("text-teal text-lg")
                        ui.label(f"container {version_name} running")
            if step.get("parameters"):
                self._display_parameters(step, step.get("parameters"))
            if step.get("ports"):
                port_mappings = {}
                for pm in step.get("ports"):
                    ports_split = pm.split(":")
                    port_mappings[ports_split[1]] = ports_split[0]
                self._display_port_mappings(step, port_mappings)
            if step.get("secrets"):
                self._display_secrets(step, step.get("secrets"))

    def _display_parameters(self, step, parameters):
        ui.label("Parameters")
        with ui.grid(columns=1).classes('w-1/2 gap-0'):
            for key, value in parameters.items():
                ui.input(
                    label=key,
                    value=str(value),
                    on_change=lambda e, key=key, step=step: self.action_update_step_parameter(
                        step, key, e.value
                    ),
                )

    def _display_port_mappings(self, step, port_mappings):
        ui.label("Port Mappings")
        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            for key, value in port_mappings.items():
                ui.input(
                    label=key,
                    value=str(value),
                    on_change=lambda e, step=step: self.action_update_step_port(
                        step, key, e.value
                    ),
                )

    def _display_secrets(self, step, secrets):
        ui.label("Secrets file")
        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            if secrets:
                ui.select(
                    label=f"Secrets file",
                    value=step["secrets"].split("/")[-1],
                    options=self.set_secret_file_select_options(),
                    on_change=lambda e, step=step: self.action_update_step_secrets(
                        step, e.value
                    )
                ).classes("w-full")

    def set_secret_file_select_options(self):
        secret_files = helpers.get_secrets_files_for_user(self.user.get("workdir"))
        return secret_files

    def action_update_step_parameter(self, step, key, value):
        parameters = step.get("parameters")
        parameters[key] = value
        db.update_step(step["_id"], {"parameters": parameters})

    def action_update_step_secrets(self, step, value):
        if value:
            secrets_path = os.path.join(
                self.user["workdir"],
                ODTP_SECRETS_DIR,
                value,
            )
        else:
            secrets_path = False
        db.update_step(step["_id"], {"secrets": secrets_path})

    def action_update_step_port(self, step, key, value):
        port_mappings = step.get("ports")
        pattern = re.compile(rf"(\d{{2,4}}):{key}")
        updated_port_mappings = [pattern.sub(f"{value}:{key}", entry) for entry in port_mappings]
        db.update_step(step["_id"], {"ports": updated_port_mappings})


    async def action_run_command(self, command, dialog, result):
        dialog.open()
        result.content = "... loading"
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
            result.content = f'```\n{output}\n```'
        self.build_form.refresh()
