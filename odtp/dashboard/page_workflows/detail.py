from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.utils.helpers as helpers


class WorkflowDisplay:
    def __init__(self):
        """init form"""
        self.workflow = None
        self.workflow_id = None
        self.get_workflow_options()
        self.build_form()

    def get_workflow_options(self):
        """get workflow options for selection"""
        workflows = db.get_collection(db.collection_workflows, include_deprecated=False)
        self.workflow_options = {
            str(workflow["_id"]): f"{workflow.get('name')}"
            for workflow in workflows
        }

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_workflow_select()
        self.ui_workflow_diagram()
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
        self.ui_workflow_diagram.refresh()

    @ui.refreshable
    def ui_workflow_info(self):
        """ui element for workflow info"""
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
        ui.label(label)
        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            for dict_item in version.get(dict_list_name):
                for key, value in dict_item.items():
                    ui.label(key).classes('bg-gray-200 border p-1')
                    ui.label(value).classes('border p-1')
