from nicegui import ui
import odtp.mongodb.db as db


from nicegui import ui

class WorkflowDisplay:
    def __init__(self):
        """init form"""
        return
        self.workflow = None
        self.workflow_id = None
        self.get_workflow_options()
        self.build_form()

    def get_component_options(self):
        """get workflow options for selection"""
        workflows = db.get_collection(db.collection_workflows)
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
        self.version = None
        self.version_id = None
        self.version_options = None
        self.ui_version_select.refresh()
        self.show_version_info.refresh()

    @ui.refreshable
    def ui_component_select(self):
        """ui element for workflow select"""
        ui.select(
            self.workflow_options,
            value=self.workflow_id,
            on_change=lambda e: self.set_workflow(str(e.value)),
            label="workflow",
            with_input=True,
        ).classes("w-1/2")

    def set_workflow(self, component_id):
        """called when a new workflow has been selected"""
        return
