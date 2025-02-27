import os
from nicegui import ui, events
import odtp.mongodb.db as db
from odtp.helpers.settings import ODTP_SECRETS_DIR
import odtp.dashboard.utils.helpers as helpers
import odtp.helpers.validation as validation
import odtp.dashboard.utils.ui_theme as ui_theme


class ExecutionForm(object):
    def __init__(self, current_user, current_digital_twin):
        self.digital_twin_id = current_digital_twin["digital_twin_id"]
        self.user = current_user
        self.get_select_options()
        self.init_form()

    def init_form(self):
        self.execution = None
        self.parameters = None
        self.secret_files = None
        self.step_count = None
        self.port_mappings = None
        self.workflow = None
        self.title = None
        self.workflow_id = None
        self.versions_dict = None
        self.build_form()

    @ui.refreshable
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
            on_change=lambda e: self.set_title(e.value),
            validation={
                "Title should be unique: this execution already exists for digital twin" \
                : lambda value: validation.validate_execution_name_unique(value.strip(), self.digital_twin_id)
            },
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
            if not workflow.get("deprecated", False)
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
        self.secret_files = [None for i in range(self.step_count)]
        self.parameter_containers = []
        for i in range(self.step_count):
            self.parameter_containers.append(ui.row().classes("w-full"))
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

    def set_workflow_steps(self):
        if self.workflow:
            for i, version_id in enumerate(self.workflow.get("versions", [])):
                version = self.versions_dict[version_id]
                self.parameters[i] = self.get_default_parameters(version)
                self.secret_files[i] = self.get_secrets_files(version)
                self.port_mappings[i] = self.get_default_port_mappings(version)

    def ui_parameters_from_file(self, version, i):
        with ui.expansion("overwrite parameters from file").classes("w-2/6"):
            ui.upload(
                on_upload=lambda e: self.handle_upload(e, version, i),
                label=f"replace parameters by uploaded parameters (ports will stay)"
            ).props('accept=.parameters').classes('max-w-full')

    def handle_upload(self, e: events.UploadEventArguments, version, i):
        text = e.content.read().decode('utf-8')
        parameters = self.parse_key_value_pairs(text)
        self.parameters[i] = parameters
        self.ui_workflow_steps.refresh()

    def parse_key_value_pairs(self, text: str) -> dict:
        parameters = {}
        for line in text.splitlines():
            line = line.strip()
            if line and "=" in line:
                key, value = map(str.strip, line.split('=', 1))
                parameters[key] = value
        return parameters

    @ui.refreshable
    def ui_workflow_steps(self):
        if not self.workflow_id:
            return
        for i, version_id in enumerate(self.workflow.get("versions", [])):
            version = self.versions_dict[version_id]
            with ui.row().classes("w-full"):
                self.display_version(version)
                self.ui_parameters_from_file(version, i)
            with ui.card().classes("w-full bg-gray-100"):
                with ui.row().classes("w-full"):
                    ui.label(self.get_version_display(version)).classes("text-lg")
                    with ui.grid(columns=3).classes("w-full"):
                        with ui.column():
                            ui.label("Parameters").classes("text-lg")
                            if self.parameters[i]:
                                    for key, value in self.parameters[i].items():
                                        ui.input(
                                            label=key,
                                            value=value,
                                            placeholder="value",
                                            on_change=lambda e, i=i, key=key: self.update_parameter_value(
                                                e.value, key, i
                                            )
                                        ).classes("w-2/3")
                        with ui.column():
                            ui.label("Ports").classes("text-lg")
                            if self.port_mappings[i].items():
                                    for port_host, port_component in self.port_mappings[i].items():
                                        ui.input(
                                            label=f"port mapping for :{port_component}",
                                            value=port_host,
                                            on_change=lambda e, i=i, port_component=port_component: self.update_port_mapping(
                                                e.value, port_component, i
                                            )
                                        )
                        with ui.column():
                            ui.label("Secrets").classes("text-lg")
                            if self.secret_files[i]:
                                file_options = self.set_secret_file_select_options()
                                if file_options:
                                    ui.select(
                                        label=f"Secrets file",
                                        value=self.secret_files[i],
                                        options=file_options,
                                        on_change=lambda e, i=i: self.update_secrets(
                                            e.value, i
                                        )
                                    ).classes("w-full")
                                else:
                                    ui_theme.ui_add_first(
                                        "secret files",
                                        ui_theme.PATH_USERS,
                                        action="upload"
                                    )

    def update_secrets(self, value, i):
        if value:
            self.secret_files[i] = os.path.join(
                self.user["workdir"],
                ODTP_SECRETS_DIR,
                value,
            )

    def set_secret_file_select_options(self):
        secret_files = helpers.get_secrets_files(self.user.get("workdir"))
        return secret_files

    def update_port_mapping(self, port_host, port_component, i):
        self.port_mappings[i][port_component] = port_host

    def update_parameter_value(self, value, key, i):
        self.parameters[i][key] = value

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

    def get_secrets_files(self, version):
        if version.get("secrets"):
            return True
        return False

    def get_default_port_mappings(self, version):
        if not version.get("ports"):
            return {}
        default_ports = {}
        for port in version["ports"]:
            port_value = port.get('port-value')
            if port_value:
                default_ports[port_value] = port_value
        return default_ports

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
        with ui.expansion("component version info").classes("w-1/2"):
            version_name = self.get_version_display(version)
            ui.link(version_name, f"../components/{str(version['_id'])}", new_tab=True).classes("text-lg")
            ui_theme.ui_version_section_content(version, "Parameters", "parameters")
            ui_theme.ui_version_section_content(version, "Ports", "ports")
            ui_theme.ui_version_section_content(version, "Secrets", "secrets")

    @ui.refreshable
    def ui_add_execution_button(self):
        if not self.workflow:
            return
        ui.button(
            "add execution",
            icon="add",
            on_click=lambda: self.db_add_execution(),
        )
        ui.button(
            "reset execution",
            icon="clear",
            on_click=lambda: self.reset_execution_form(),
        ).props("flat")

    def prepare_port_mappings_for_db(self):
        port_mappings_db = []
        for port_mappings in self.port_mappings:
            if not port_mappings:
                port_mappings_db.append([])
            else:
                port_mappings_db.append([
                    f"{port_host}:{port_component}" for port_component, port_host in port_mappings.items()
                ])
        return port_mappings_db

    def reset_execution_form(self):
        self.init_form()
        self.build_form.refresh()

    def db_add_execution(self):
        """add execution"""
        port_mappings_db = self.prepare_port_mappings_for_db()
        execution_id = db.add_execution(
            dt_id=self.digital_twin_id,
            workflow_id=self.workflow_id,
            name=self.title,
            parameters=self.parameters,
            ports=port_mappings_db,
            secret_files=self.secret_files,
        )
        ui.notify(
            f"Execution {execution_id} has been added",
            type="positive",
        )
        from odtp.dashboard.page_executions.main import ui_tabs
        ui_tabs.refresh()
