from nicegui import ui
import odtp.mongodb.db as db
from pprint import pprint

class WorkflowDisplay:
    def __init__(self):
        """init form"""
        self.workflow = None
        self.workflow_id = None
        self.get_workflow_options()
        self.build_form()

    def get_workflow_options(self):
        """get workflow options for selection"""
        workflows = db.get_collection(db.collection_workflows)
        print(workflows)
        self.workflow_options = {
            str(workflow["_id"]): f"{workflow.get('name')}"
            for workflow in workflows
        }

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_workflow_select()
        self.ui_workflow_info()

    def reset_workflow_form(self):
        """reset workflow form"""
        self.workflow_id = None
        self.wor.refresh()
        self.show_version_info.refresh()

    @ui.refreshable
    def ui_workflow_select(self):
        """ui element for workflow select"""
        ui.select(
            self.workflow_options,
            value=self.workflow_id,
            on_change=lambda e: self.set_workflow(str(e.value)),
            label="workflow",
            with_input=True,
        ).classes("w-1/2")

    def set_workflow(self, workflow_id):
        """called when a new workflow has been selected"""
        self.workflow_id = workflow_id
        self.workflow = db.get_document_by_id(
            document_id=workflow_id, collection=db.collection_workflows
        )
        versions = db.get_document_by_ids_in_collection(
            document_ids=self.workflow.get("versions", []),
            collection=db.collection_versions
        )
        self.versions_dict = {str(version["_id"]): version  for version in versions }
        self.ui_workflow_info.refresh()

    @ui.refreshable
    def ui_workflow_info(self):
        """ui element for workflow info"""
        if not self.workflow:
            return
        for version_id in self.workflow.get("versions", []):
            version = self.versions_dict[version_id]
            pprint(version)
            self.display_version(version)


    def display_version(self, version):
        ui.label(f"{version["component"]["componentName"]} {version["component_version"]}")
        parameters = version.get("parameters", [])
        if parameters:
            self.display_dict_list(version, "Parameters", "parameters")
        ports = version.get("ports", [])
        if ports:
            self.display_dict_list(version, "Ports", "ports")
        secrets = version.get("secrets", [])
        if secrets:
            self.display_dict_list(version, "Secrets", "secrets")

    def display_dict_list(self, version, label, dict_list_name):
        """display a list of dicts"""
        ui.label(label)
        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            for dict_item in version.get(dict_list_name):
                for key, value in dict_item.items():
                    ui.label(key).classes('bg-gray-200 border p-1')
                    ui.label(value).classes('border p-1')
