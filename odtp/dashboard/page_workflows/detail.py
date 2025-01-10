from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.utils.helpers as helpers


class WorkflowDisplay:
    def __init__(self, workflow_id=None):
        self.workflow = None
        if workflow_id:
            self.workflow_id = workflow_id
            self.set_workflow()
        else:
            self.workflow_id = None
        self.get_version_dict()
        self.get_workflow_options()
        self.build_form()

    def get_workflow_options(self):
        workflows = db.get_collection(db.collection_workflows, include_deprecated=False)
        self.workflow_options = {
            str(workflow["_id"]): f"{workflow.get('name')}"
            for workflow in workflows
        }

    def get_version_dict(self):
        versions = db.get_collection(
            collection=db.collection_versions
        )
        self.versions_dict = {str(version["_id"]): version  for version in versions }

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_workflow_select()
        self.ui_workflow_diagram()
        self.ui_workflow_info()

    @ui.refreshable
    def ui_workflow_select(self):
        """ui element for workflow select"""
        ui.select(
            self.workflow_options,
            value=self.workflow_id,
            on_change=lambda e: self.form_set_workflow_id(str(e.value)),
            label="workflow",
            with_input=True,
        ).classes("w-1/2")

    def form_set_workflow_id(self, workflow_id):
        if workflow_id == self.workflow_id:
            return
        self.workflow_id = workflow_id
        self.set_workflow()
        self.build_form.refresh()


    def set_workflow(self):
        if not self.workflow_id:
            return
        self.workflow = db.get_document_by_id(
            document_id=self.workflow_id, collection=db.collection_workflows
        )

    @ui.refreshable
    def ui_workflow_info(self):
        if not self.workflow:
            return
        for version_id in self.workflow.get("versions", []):
            version = self.versions_dict[version_id]
            self.display_version(version)

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
        with ui.card().classes("bg-gray-100 w-1/2"):
            version_name = self.get_version_display(version)
            ui.link(version_name, f"../components/{str(version['_id'])}", new_tab=True).classes("text-lg")
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
        with ui.grid(columns='1fr 2fr').classes('w-full gap-0'):
            ui.label(label)
            ui.label("does not apply")

    def display_dict_list(self, version, label, dict_list_name):
        """display a list of dicts"""
        ui.label(label)
        with ui.grid(columns='1fr 2fr').classes('w-full gap-0'):
            for dict_item in version.get(dict_list_name):
                for key, value in dict_item.items():
                    ui.label(key).classes('bg-gray-200 border p-1')
                    ui.label(str(value)).classes('border p-1')
