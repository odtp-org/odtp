import json
import asyncio
import os.path
import shlex
import sys
from nicegui import ui, app
import odtp.mongodb.db as db
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.page_executions.projectdir as projectdir
import odtp.dashboard.page_executions.run as run


from nicegui import ui

class ExecutionDisplay:
    def __init__(self, current_user, current_digital_twin, dialog, result):
        """init form"""
        self.dialog = dialog
        self.result = result
        self.execution = None
        self.steps = None
        self.workflow = None
        self.execution_id = None
        self.execution_path = None
        self.user = current_user
        self.digital_twin = current_digital_twin
        self.execution_options = None
        self.folder_status = None
        self.get_execution_options()
        self.build_form()

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_execution_select()
        self.ui_workflow_diagram()
        with ui.expansion("Execution Details: Parameters and Ports").classes("w-1/2 bg-gray-100"):
            self.ui_steps()
        self.ui_execution_run_info()
        self.ui_project_directory()
        self.ui_prepare_execution()
        self.ui_run_execution()

    def ui_execution_run_info(self):
        if not self.execution:
            return
        with ui.grid(columns=2):
            ui.label("created")
            ui.label(self.execution['createdAt'].strftime(f'%Y-%m-%d'))
            if not self.execution:
                return
            ui.label("started")
            if self.execution.get('start_timestamp'):
                ui.label(self.execution['start_timestamp'].strftime(f'%Y-%m-%d %H:%M:%S'))
            else:
                ui.label("not yet")
            ui.label("ended")
            if self.execution.get('end_timestamp'):
                ui.label(self.execution['end_timestamp'].strftime('%Y-%m-%d %H:%M:%S'))
            else:
                ui.label("not yet")

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
        self.folder_status = run.get_folder_status(self.execution_id, self.execution_path)
        if self.folder_status == run.FOLDER_PREPARED:
            with ui.row():
                ui.icon("check").classes("text-teal text-lg")
                ui.label("The execution has been prepared").classes("text-teal")
            return
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
        ).props("flat")

    @ui.refreshable
    def ui_run_execution(self):
        if not self.execution_path:
            return
        self.folder_status = run.get_folder_status(self.execution_id, self.execution_path)
        if not self.folder_status == run.FOLDER_PREPARED:
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
        ).props("flat")

    @ui.refreshable
    def ui_project_directory(self):
        if not self.execution:
            return
        if self.execution_path:
            with ui.row():
                ui.icon("check").classes("text-teal text-lg")
                ui.label("Project folder for the execution run has been created").classes("text-teal")
                ui.label(self.execution_path)
            return
        ui.button(
            "Create execution directory",
            on_click=lambda: self.action_create_folder(),
            icon="add",
        ).props("flat")

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
        ui.select(
            self.execution_options,
            value=self.execution_id,
            on_change=lambda e: self.action_set_execution(str(e.value)),
            label="execution",
            with_input=True,
        ).classes("w-1/2")

    def action_set_execution(self, execution_id):
        """called when a new component has been selected"""
        self.execution_id = execution_id
        self.execution = db.get_document_by_id(
            document_id=execution_id, collection=db.collection_executions
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
        for step in self.steps:
            step["_id"] = str(step["_id"])
            step["executionRef"] = str(step["executionRef"])
        self.execution_path = self.execution.get("execution_path")
        self.build_form.refresh()

    @ui.refreshable
    def ui_workflow_diagram(self, init="graph LR;"):
        if not self.execution:
           return
        version_names = []
        for version_id in self.workflow.get("versions", []):
            version = self.versions_dict[version_id]
            version_names.append(self._get_version_display(version))
        return ui.mermaid(
            f"""
            {helpers.get_workflow_mermaid(version_names, init='graph LR;')}"""
        ).classes("w-full")

    @ui.refreshable
    def ui_steps(self):
        if not self.steps:
            return
        for step in self.steps:
            self._display_step(step)

    def _get_version_display(self, version):
        return f"{version['component']['componentName']}_{version['component_version']}"

    def _display_step(self, step):
        """Display information for a single step."""
        version = self.versions_dict.get(step["component_version"])
        version_name = self._get_version_display(version)
        ui.label(version_name).classes("text-lg")
        if  step.get("parameters"):
            self._display_dict_list(step.get("parameters"), "Parameters")
        else:
            self._display_not_set("Parameters")
        if step.get("ports"):
            port_mappings = {}
            for pm in step.get("ports"):
                ports_split = pm.split(":")
                port_mappings[ports_split[0]] = ports_split[1]
            self._display_dict_list(port_mappings, "Port Mappings")
        else:
            self._display_not_set("Port Mappings")

        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            for key in ["start_timestamp", "end_timestamp"]:
                if step.get(key) is not None:
                    ui.label(key.replace("_", " ").capitalize()).classes('bg-gray-200 border p-1')
                    ui.label(str(step[key])).classes('border p-1')

    def _display_not_set(self, label):
        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            ui.label(label)
            ui.label("None")

    def _display_dict_list(self, data, label):
        """Display a list of dictionaries or key-value pairs."""
        ui.label(label)
        if isinstance(data, dict) and data != {}:
            with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
                for key, value in data.items():
                    ui.label(key).classes('bg-gray-200 border p-1')
                    ui.label(str(value)).classes('border p-1')

        elif isinstance(data, list) and data:
            with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
                for index, item in enumerate(data):
                    ui.label(f"{label} {index + 1}").classes('bg-gray-200 border p-1')
                    ui.label(str(item)).classes('border p-1')

    async def action_run_command(self, command, dialog, result) -> None:
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
