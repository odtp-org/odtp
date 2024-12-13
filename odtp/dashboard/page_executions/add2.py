from nicegui import ui
from pprint import pprint
import odtp.mongodb.db as db
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.validators as validators
from odtp.dashboard.page_executions.parameters_form import ContainerParameters
from odtp.dashboard.page_executions.ports_form import ContainerPorts
from odtp.dashboard.page_executions.workflow_form import ContainerWorkflow
from odtp.dashboard.utils.file_picker import local_file_picker


class ExecutionForm(object):
    def __init__(self, digital_twin_id):
        self.execution = None
        self.parameters = None
        self.step_count = None
        self.ports = None
        self.digital_twin_id = digital_twin_id
        self.workflow = None
        self.title = None
        self.workflow_id = None
        self.versions_dict = None
        self.get_select_options()
        self.build_form()

    def build_form(self):
        self.ui_execution_title()
        self.ui_workflow_select()
        self.ui_workflow_diagram()
        self.ui_workflow_steps()
        self.ui_add_execution_button()

    def ui_execution_title(self):
        ui.input(
            label="Execution title",
            placeholder="Execution title",
            on_change=lambda e: self.set_title(e.value)
        ).classes("w-1/2")

    def set_title(self, title):
        self.title = title
        self.ui_workflow_select.refresh()

    def get_select_options(self):
        workflows = db.get_collection(
            collection=db.collection_workflows,
        )
        self.workflow_options = {
            str(workflow["_id"]): f"{workflow.get('name')}"
            for workflow in workflows
        }

    @ui.refreshable
    def ui_workflow_select(self):
        if not self.title:
            return
        self.get_select_options()
        ui.select(
            self.workflow_options,
            on_change=lambda e: self.set_workflow(workflow_id=e.value),
            label="workflow",
            with_input=True,
        ).classes("w-1/2")

    def set_workflow(self, workflow_id):
        self.workflow_id = workflow_id
        self.workflow = db.get_document_by_id(
            document_id=workflow_id,
            collection=db.collection_workflows
        )
        self.step_count = len(self.workflow.get("versions", []))
        self.port_mappings = [{} for i in range(self.step_count)]
        self.parameters = [{} for i in range(self.step_count)]
        self.get_versions_dict()
        self.set_workflow_steps()
        self.ui_workflow_steps.refresh()
        self.ui_workflow_diagram.refresh()
        self.ui_add_execution_button.refresh()

    def get_versions_dict(self):
        versions = db.get_document_by_ids_in_collection(
            document_ids=self.workflow.get("versions", []),
            collection=db.collection_versions
        )
        self.versions_dict = {str(version["_id"]): version  for version in versions }
        print(self.versions_dict)

    def set_workflow_steps(self):
        if self.workflow:
            for i, version_id in enumerate(self.workflow.get("versions", [])):
                version = self.versions_dict[version_id]
                self.parameters[i] = self.get_default_parameters(version)
                self.port_mappings[i] = self.get_default_port_mappings(version)
            pprint(self.ports)
            pprint(self.parameters)

    @ui.refreshable
    def ui_workflow_steps(self):
        if not self.workflow_id:
            return
        for i, version_id in enumerate(self.workflow.get("versions", [])):
            version = self.versions_dict[version_id]
            self.display_version(version)
            with ui.grid(columns=2).classes("w-1/2"):
                for key, value in self.parameters[i].items():
                    key = ui.input(label="key", value=key, placeholder="key")
                    value = ui.input(label="value", value=value, placeholder="value")
            with ui.grid(columns=2).classes("w-1/8"):
                for key, value in self.port_mappings[i].items():
                    ui.input(label=f"port mapping for :{value}", value=key)

    def get_default_parameters(self, version):
        if not version.get("parameters"):
            return {}
        default_parameters = {}
        for parameter in version["parameters"]:
            key = parameter.get('name')
            value = parameter.get('default-value')
            if key:
                default_parameters[key] = value
        return default_parameters

    def get_default_port_mappings(self, version):
        if not version.get("ports"):
            return {}
        default_ports = {}
        for port in version["ports"]:
            port_value = port.get('port-value')
            if port_value:
                default_ports[port_value] = port_value
        return default_ports

    def ui_parameters(self, version):
        key, value = self.get_default_parameters(version)
        with ui.row().classes("w-full"):
            with ui.grid(columns=2).classes("w-full"):
                key = ui.input(label="key", value=key, placeholder="key")
                value = ui.input(label="value", value=value, placeholder="value")

    @ui.refreshable
    def ui_workflow_diagram(self, init="graph LR;"):
        if not self.workflow:
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

    def display_version(self, version):
        version_name = self.get_version_display(version)
        ui.mermaid(
            f"""
            {helpers.get_workflow_mermaid([version_name], init='graph LR;')}"""
        ).classes("w-full")
        parameters = version.get("parameters", [])
        if parameters:
            self.display_dict_list(version, "Parameters", "parameters")
        else:
            self.display_not_set("Parameters")
        ports = version.get("ports", [])
        if ports:
            self.display_dict_list(version, "Ports", "ports")
        else:
            self.display_not_set("Ports")
        secrets = version.get("secrets", [])
        if secrets:
            self.display_dict_list(version, "Secrets", "secrets")
        else:
            self.display_not_set("Secrets")


    def display_not_set(self, label):
        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            ui.label(label)
            ui.label("None")

    def display_dict_list(self, version, label, dict_list_name):
        """display a list of dicts"""
        with ui.expansion(label).classes("w-1/2"):
            with ui.grid(columns='1fr 2fr').classes('w-full gap-0'):
                for dict_item in version.get(dict_list_name):
                    for key, value in dict_item.items():
                        ui.label(key).classes('bg-gray-200 border p-1')
                        ui.label(value).classes('border p-1')

    @ui.refreshable
    def ui_add_execution_button(self):
        if not self.workflow:
            return
        ui.button(
            "add execution",
            icon="add",
            on_click=lambda: self.db_add_execution(),
        )

    def db_add_execution(self):
        """add execution"""
        print("-------- before save")
        pprint(self.port_mappings)
        print(self.workflow_id)
        print(self.digital_twin_id)
        print(self.title)
        print(self.workflow.get("versions"))
        execution_id = db.add_execution(
            dt_id=self.digital_twin_id,
            workflow_id=self.workflow_id,
            name=self.title,
            versions=self.workflow.get("versions"),
            parameters=self.parameters,
            ports=self.ports,
        )
        ui.notify(
            f"Execution {execution_id} has been added",
            type="positive",
        )
        from odtp.dashboard.page_executions.main import ui_tabs
        ui_tabs.refresh()
