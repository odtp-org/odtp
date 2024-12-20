from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.validators as validators


class WorkflowForm(object):
    def __init__(self):
        self.workflow = []
        self.name = None
        self.select_options = None
        self.versions = None
        self.version_tags = None
        self.count_step_forms = 1
        self.get_select_options()
        self.build_form()

    @ui.refreshable
    def build_form(self):
        self.ui_workflow_name()
        self.ui_steps()
        self.ui_buttons()
        self.ui_add_workflow_button()

    def ui_workflow_name(self):
        ui.input(
            label="Workflow title",
            placeholder="Workflow title",
            on_change=lambda e: self.set_name(e.value)
        ).classes("w-1/2")

    def set_name(self, name):
        self.name = name

    def get_select_options(self):
        component_versions = db.get_collection_sorted(
            collection=db.collection_versions,
            sort_tuples=[
                ("component.componentName", db.ASCENDING),
                ("component_version", db.DESCENDING),
            ],
        )
        select_options = {}
        for version in component_versions:
            if not version.get("deprecated", False):
                version_display_name = helpers.get_execution_step_display_name(
                    component_name=version["component"]["componentName"],
                    component_version=version["component_version"],
                )
                select_options[(str(version["_id"]), version_display_name)] = (
                    f"{version_display_name}"
                )
        self.select_options = select_options

    @ui.refreshable
    def ui_steps(self):
        with ui.row().classes("w-full"):
            for i in range(self.count_step_forms):
                ui.select(
                    self.select_options,
                    on_change=lambda e, step_index=i: self.update_workflow(step_index, e.value),
                    label="component versions",
                    value=self.get_workflow_value(i),
                ).classes("w-1/2")


    def get_workflow_value(self, i):
        if i < len(self.workflow):
            return self.workflow[i]
        else:
            return None

    def update_workflow(self, step_index, version_tuple):
        if step_index < len(self.workflow):
            self.workflow[step_index] = version_tuple
        else:
            self.workflow.append(version_tuple)
        self.ui_add_workflow_button.refresh()

    def add_step(self):
        self.count_step_forms += 1
        self.ui_steps.refresh()

    def remove_step(self):
        if self.count_step_forms > 1:
            self.count_step_forms -= 1
            self.workflow = self.workflow[:self.count_step_forms]
            self.ui_steps.refresh()

    def ui_buttons(self):
        with ui.grid(columns=2):
            ui.button(
                "Add workflow step",
                on_click=self.add_step,
                icon="add",
            ).props(
                "flat"
            ).classes("w-full")
            ui.button(
                "Remove workflow step",
                on_click=self.remove_step,
                icon="remove",
            ).props("flat").classes("w-full")

    def get_steps(self):
        steps = []
        for item in self.container:
            if item and item.tag == "nicegui-select":
                steps.append(item)
        return steps

    @ui.refreshable
    def ui_add_workflow_button(self):
        if not self.workflow:
            return
        ui.button(
            "add workflow",
            icon="add",
            on_click=lambda: self.db_add_workflow(),
        )

    def db_add_workflow(self):
        """add component version"""
        db_workflow = [
            version_tuple[0] for version_tuple in self.workflow
        ]
        workflow_id = db.add_workflow(
            name=self.name,
            workflow=db_workflow,
        )
        ui.notify(
            f"Workflow {workflow_id} has been added",
            type="positive",
        )
        from odtp.dashboard.page_workflows.main import ui_tabs
        ui_tabs.refresh()
