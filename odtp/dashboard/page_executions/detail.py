import json
from nicegui import ui, app
import odtp.mongodb.db as db
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.storage as storage
from pprint import pprint


from nicegui import ui

class ExecutionDisplay:
    def __init__(self, digital_twin_id):
        """init form"""
        self.execution = None
        self.steps = None
        self.workflow = None
        self.execution_id = None
        self.digital_twin_id = digital_twin_id
        self.execution_options = None
        self.get_execution_options()
        self.build_form()

    def get_execution_options(self):
        """get execution options"""
        self.execution_options = helpers.get_execution_select_options(
            digital_twin_id=self.digital_twin_id
        )

    @ui.refreshable
    def ui_run_execution(self):
        if not self.execution_id:
            return
        ui.button(
            "Prepare and Run Executions",
            on_click=lambda: ui.open(ui_theme.PATH_RUN),
            icon="link",
        )

    @ui.refreshable
    def ui_reset_execution(self):
        if not self.execution_id:
            return
        ui.button(
            "Reset execution selection",
            on_click=lambda e: self.reset_execution(),
            icon="link",
        ).props("flat")

    def reset_execution(self):
        storage.reset_storage_delete([storage.CURRENT_EXECUTION])
        self.execution_id = None
        self.execution = None
        self.steps = None
        self.workflow = None
        self.build_form.refresh()

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_execution_select()
        self.ui_run_execution()
        self.ui_reset_execution()
        self.ui_workflow_diagram()
        self.ui_steps()

    @ui.refreshable
    def ui_execution_select(self):
        """ui element for component select"""
        ui.select(
            self.execution_options,
            value=self.execution_id,
            on_change=lambda e: self.set_execution(str(e.value)),
            label="execution",
            with_input=True,
        ).classes("w-1/2")

    def set_execution(self, execution_id):
        """called when a new component has been selected"""
        self.execution_id = execution_id
        self.execution = db.get_document_by_id(
            document_id=execution_id, collection=db.collection_executions
        )
        self.workflow = db.get_document_by_id(
            document_id=self.execution["workflow_id"], collection=db.collection_workflows
        )
        self.versions = db.get_document_by_ids_in_collection(
            document_ids=self.workflow.get("versions", []),
            collection=db.collection_versions
        )
        self.versions_dict = { str(version["_id"]): version  for version in self.versions }
        step_ids = [str(step_id) for step_id in self.execution["steps"]]
        self.steps = db.get_document_by_ids_in_collection(
            document_ids=step_ids, collection=db.collection_steps
        )
        pprint("SET=======")
        pprint(self.steps)
        self.ui_workflow_diagram.refresh()
        self.ui_run_execution.refresh()
        self.ui_execution_run_info.refresh()
        self.ui_steps.refresh()

    @ui.refreshable
    def ui_workflow_diagram(self, init="graph LR;"):
        if not self.execution:
           return
        version_names = []
        for version_id in self.workflow.get("versions", []):
            version = self.versions_dict[version_id]
            version_names.append(self.get_version_display(version))
        return ui.mermaid(
            f"""
            {helpers.get_workflow_mermaid(version_names, init='graph LR;')}"""
        ).classes("w-full")

    def get_version_display(self, version):
        return f"{version['component']['componentName']}_{version['component_version']}"

    @ui.refreshable
    def ui_execution_run_info(self):
        if not self.execution:
            return
        print("--------- ui execution")
        pprint(self.execution)

    @ui.refreshable
    def ui_steps(self):
        if not self.steps:
            return
        for step in self.steps:
            self.display_step(step)

    def get_version_display(self, version):
        return f"{version['component']['componentName']}_{version['component_version']}"

    def display_step(self, step):
        """Display information for a single step."""
        version = self.versions_dict.get(step["component_version"])
        version_name = self.get_version_display(version)
        ui.mermaid(
            f"""
            {helpers.get_workflow_mermaid([version_name], init='graph LR;')}"""
        ).classes("w-full")
        if  step.get("parameters"):
            self.display_dict_list(step.get("parameters"), "Parameters")
        else:
            self.display_not_set("Parameters")
        if step.get("ports"):
            print(step.get("ports"))
            port_mappings = {}
            for pm in step.get("ports"):
                ports_split = pm.split(":")
                print(ports_split)
                port_mappings[ports_split[0]] = ports_split[1]
            self.display_dict_list(port_mappings, "Port Mappings")
        else:
            self.display_not_set("Port Mappings")

        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            for key in ["start_timestamp", "end_timestamp"]:
                if step.get(key) is not None:
                    ui.label(key.replace("_", " ").capitalize()).classes('bg-gray-200 border p-1')
                    ui.label(str(step[key])).classes('border p-1')

    def display_not_set(self, label):
        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            ui.label(label)
            ui.label("None")

    def display_dict_list(self, data, label):
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
