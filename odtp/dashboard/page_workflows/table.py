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
        print(workflows)
        if not workflows:
            ui.label("No workflows yet").classes("text-red-500")
            return
        self.workflows = workflows
        self.workflow_rows = []
        self.selected_version_ids = set()
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

    def build_table(self):
        """build the table"""
        with ui.column().classes("w-full"):
            self.table_selectors()
            self.add_header()
            self.add_rows()

    @ui.refreshable
    def table_selectors(self):
        """set the table selectors"""
        with ui.row().classes("w-full"):
            ui.checkbox(
                "Show deprecated",
                on_change=lambda e: self.filter_deprecated(e.value)
            ).classes("w-1/8")
            ui.button(
                "delete_selected",
                on_click=lambda: self.delete_selected(),
                icon="clear",
            ).props("flat").classes("w-1/8")

    def add_header(self):
        headers = [
            {"text": "Select", "col_span": 1},
            {"text": "Workflow", "col_span": 1},
            {"text": "Versions", "col_span": 5},
            {"text": "Created At", "col_span": 1},
            {"text": "Updated At", "col_span": 1},
            {"text": "Deprecated", "col_span": 1},
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
            with ui.row().classes("w-full p-2 border-b grid grid-cols-10 gap-4 items-left"):
                ui.checkbox(
                    on_change=lambda e, workflow_id=workflow["_id"]: self.toggle_selection(e.value, workflow_id)
                ).classes("items-center col-span-1")
                ui.label(workflow['name']).classes("truncate col-span-1")
                ui.label(self.get_workflow_display(workflow)).classes("truncate col-span-5")
                ui.label(self.display_date(workflow['created_at'])).classes("truncate col-span-1")
                ui.label(self.display_date(workflow['updated_at'])).classes("truncate col-span-1")
                ui.label(self.get_deprecated_display(workflow['deprecated'])).classes("truncate col-span-1")

    def toggle_selection(self, selected, workflow_id):
        """toggle select for delete of versions"""
        if selected:
            self.selected_version_ids.add(workflow_id)
        else:
            self.selected_version_ids.remove(workflow_id)

    def filter_components(self, workflow_id):
        """filter by component"""
        self.workflow_id = workflow_id
        self.rebuild_rows()

    def filter_reset(self):
        """rebuild rows in original state"""
        self.workflow_id = None
        self.workflow_name = None
        self.show_deprecated = False
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
        if not self.show_deprecated:
            self.filtered_workflows = [
                workflow for workflow in self.filtered_workflows
                if not workflow.get("deprecated", False)
            ]
        self.add_rows.refresh()

    def delete_selected(self):
        """delete selected versions"""
        pass
