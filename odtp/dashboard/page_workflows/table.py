from datetime import datetime
from nicegui import ui
import odtp.mongodb.db as db


from nicegui import ui

class WorkflowTable:
    def __init__(self):
        """intialize the form"""
        workflows = db.get_collection(
            collection=db.collection_workflows,
        )
        if not workflows:
            ui.label("No workflows yet").classes("text-red-500")
            return
        self.workflows = workflows
        self.workflow_rows = []
        self.selected_workflow_ids = set()
        self.filtered_workflows = [
            workflow for workflow in self.workflows
            if not workflow.get("deprecated", False)
        ]
        self.show_deprecated = False
        versions = db.get_collection(
            collection=db.collection_versions
        )
        self.versions_dict = {str(version["_id"]): version  for version in versions }
        self.build_table()

    @ui.refreshable
    def build_table(self):
        """build the table"""
        with ui.column().classes("w-full"):
            self.table_selectors()
            self.add_header()
            self.add_rows()
            self.ui_selected_workflow_ids()

    @ui.refreshable
    def ui_selected_workflow_ids(self):
        for wf in self.selected_workflow_ids:
            ui.label(wf)

    @ui.refreshable
    def table_selectors(self):
        """set the table selectors"""
        with ui.row().classes("w-full"):
            ui.checkbox(
                "Show deprecated",
                on_change=lambda e: self.filter_deprecated(e.value)
            ).classes("w-1/8")
            ui.button(
                "Reset selection",
                on_click=lambda e: self.filter_reset(),
                icon="clear",
            ).props("flat").classes("w-1/8")
            ui.button(
                "Deprecate selected",
                on_click=lambda: self.deprecate_selected(),
                icon="clear",
            ).props("flat").classes("w-1/8")
            ui.button(
                "Activate selected",
                on_click=lambda: self.activate_selected(),
                icon="add",
            ).props("flat").classes("w-1/8")

    def add_header(self):
        headers = [
            {"text": "Select", "col_span": 1},
            {"text": "Workflow", "col_span": 1},
            {"text": "Versions", "col_span": 6},
            {"text": "Created At", "col_span": 1},
            {"text": "Updated At", "col_span": 1},
        ]
        with ui.row().classes("w-full bg-gray-200 p-2 border-b grid grid-cols-10 gap-4 items-left"):
            for header in headers:
                ui.label(header["text"]).classes(
                    f"font-bold text-center truncate col-span-{header['col_span']}"
                )

    def display_date(self, datetime_field):
        return datetime_field.strftime("%Y-%m-%d")

    @ui.refreshable
    def add_rows(self):
        """set the table rows"""
        self.workflow_rows.clear()
        for workflow in self.filtered_workflows:
            if workflow.get("deprecated"):
                color = "text-gray-500"
            else:
                color = ""
            with ui.row().classes("w-full p-2 border-b grid grid-cols-10 gap-4 items-left"):
                ui.checkbox(
                    on_change=lambda e, workflow_id=workflow["_id"]: self.toggle_selection(e.value, workflow_id)
                ).classes(f"items-center col-span-1 {color}")
                ui.label(workflow['name']).classes(f"truncate col-span-1 {color}")
                ui.label(self.get_workflow_display(workflow)).classes(f"truncate col-span-6 {color}")
                ui.label(self.display_date(workflow['created_at'])).classes(f"truncate col-span-1 {color}")
                ui.label(self.display_date(workflow['updated_at'])).classes(f"truncate col-span-1 {color}")

    def toggle_selection(self, selected, workflow_id):
        """toggle select for delete of versions"""
        if selected:
            self.selected_workflow_ids.add(workflow_id)
        else:
            self.selected_workflow_ids.remove(workflow_id)

    def filter_components(self, workflow_id):
        """filter by component"""
        self.workflow_id = workflow_id
        self.rebuild_rows()

    def filter_reset(self):
        """rebuild rows in original state"""
        self.show_deprecated = True
        self.rebuild_rows()
        self.table_selectors.refresh()

    def filter_deprecated(self, show_deprecated):
        """filter out deprecated"""
        self.show_deprecated = show_deprecated
        self.rebuild_rows()

    def get_workflow_display(self, workflow):
        workflow_list = []
        for version_id in workflow.get("versions", []):
            workflow_list.append(
                self.get_version_display(self.versions_dict[version_id])
            )
        return " -> ".join(workflow_list)

    def get_version_display(self, version):
        return f"{version['component']['componentName']}_{version['component_version']}"

    def get_deprecated_display(self, deprecated):
        if deprecated:
            return "deprecated"
        else:
            return ""

    def get_version_dict(self, workflow):
        workflow = db.get_document_by_id(
            document_id=workflow["_id"], collection=db.collection_workflows
        )

    def rebuild_rows(self):
        """rebuild rows with filters"""
        self.filtered_workflows = self.workflows
        if not self.show_deprecated:
            self.filtered_workflows = [
                workflow for workflow in self.filtered_workflows
                if not workflow.get("deprecated", False)
            ]
        self.add_rows.refresh()

    def deprecate_selected(self):
        """deprecate selected workflows"""
        db.deprecate_documents_by_ids_in_collection(self.selected_workflow_ids, db.collection_workflows)
        ui.notify(
            f"The selected {len(self.selected_workflow_ids)} workflows have been deprecated.",
            type="positive"
        )
        from odtp.dashboard.page_workflows.main import ui_workflow_list
        ui_workflow_list.refresh()

    def activate_selected(self):
        """activate selected workflows"""
        db.activate_documents_by_ids_in_collection(self.selected_workflow_ids, db.collection_workflows)
        ui.notify(
            f"The selected {len(self.selected_workflow_ids)} workflows have been activated.",
            type="positive"
        )
        from odtp.dashboard.page_workflows.main import ui_workflow_list
        ui_workflow_list.refresh()
