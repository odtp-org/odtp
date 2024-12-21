from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db


class ExecutionTable:
    def __init__(self, digital_twin_id):
        """intialize the form"""
        self.executions = db.get_sub_collection_items(
            collection=db.collection_digital_twins,
            sub_collection=db.collection_executions,
            item_id=digital_twin_id,
            ref_name=db.collection_executions,
        )
        workflows = db.get_collection(db.collection_workflows)
        self.workflow_options = {
            str(workflow["_id"]): f"{workflow.get('name')}"
            for workflow in workflows
            if not workflow.get("deprecated", False)
        }
        if not self.executions:
            ui.label("No components yet").classes("text-red-500")
            return
        self.execution_rows = []
        self.selected_execution_ids = set()
        self.filtered_executions = [
            execution for execution in self.executions
            if not execution.get("deprecated", False)
        ]
        self.workflow_id = None
        self.workflow_name = None
        self.show_deprecated = False
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
        if self.workflow_options:
            with ui.row().classes("w-full"):
                ui.select(
                    self.workflow_options,
                    on_change=lambda e: self.filter_workflows(str(e.value)),
                    label="workflows",
                    with_input=True,
                ).classes("w-1/2")
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
            "Select",
            "Title",
            "Id",
            "Created At",
            "Started at",
            "Ended at",
        ]
        with ui.row().classes("w-full bg-gray-200 p-2 border-b grid grid-cols-10 gap-4"):
            for header in headers:
                ui.label(header).classes("font-bold text-center truncate")

    def get_deprecated_display(self, deprecated):
        if deprecated:
            return "deprecated"
        else:
            return ""

    @ui.refreshable
    def add_rows(self):
        """set the table rows"""
        self.execution_rows.clear()
        for execution in self.filtered_executions:
            if execution.get("deprecated"):
                color = "text-gray-500"
            else:
                color = ""
            with ui.row().classes("w-full p-2 border grid grid-cols-10 gap-4 items-center"):
                ui.checkbox(
                    on_change=lambda e, execution_id=execution["_id"]: self.toggle_selection(e.value, execution_id)
                )
                ui.label(execution['title']).classes(f"text-center truncate {color}")
                ui.label(str(execution['_id'])).classes(f"text-center truncate {color}")
                ui.label(execution['createdAt'].strftime(f'%Y-%m-%d')).classes("text-center truncate {color}")
                if execution.get('start_timestamp'):
                    ui.label(execution['start_timestamp'].strftime(f'%Y-%m-%d')).classes("text-center truncate {color}")
                else:
                    ui.label("not run").classes(f"{color}")
                if execution.get('end_timestamp'):
                    ui.label(execution['end_timestamp'].strftime('%Y-%m-%d')).classes(f"text-center truncate {color}")
                else:
                    ui.label("not ended").classes(f"{color}")

    def toggle_selection(self, selected, execution_id):
        """toggle select for delete of executions"""
        if selected:
            self.selected_execution_ids.add(execution_id)
        else:
            self.selected_execution_ids.remove(execution_id)

    def filter_workflows(self, workflow_id):
        """filter by workflow"""
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

    def rebuild_rows(self):
        """rebuild rows with filters"""
        self.filtered_executions = self.executions
        if self.workflow_id:
            self.filtered_executions = [
                execution for execution in self.executions
                if str(execution["workflow"]) == self.workflow_id
            ]
        if not self.show_deprecated:
            self.filtered_executions = [
                execution for execution in self.filtered_executions
                if not execution.get("deprecated", False)
            ]
        self.add_rows.refresh()

    def deprecate_selected(self):
        """deprecate selected executions"""
        db.deprecate_documents_by_ids_in_collection(self.selected_execution_ids, db.collection_executions)
        ui.notify(
            f"The selected {len(self.selected_execution_ids)} component versions have been deprecated.",
            type="positive"
        )
        from odtp.dashboard.page_executions.main import ui_executions_table
        ui_executions_table.refresh()

    def activate_selected(self):
        """activate selected executions"""
        db.activate_documents_by_ids_in_collection(self.selected_execution_ids, db.collection_executions)
        ui.notify(
            f"The selected {len(self.selected_execution_ids)} component versions have been activated.",
            type="positive"
        )
        from odtp.dashboard.page_executions.main import ui_executions_table
        ui_executions_table.refresh()
