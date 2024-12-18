import pandas as pd
from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db

from pprint import pprint


class ExecutionTable:
    def __init__(self, digital_twin_id):
        """intialize the form"""
        self.executions = db.get_sub_collection_items(
            collection=db.collection_digital_twins,
            sub_collection=db.collection_executions,
            item_id=digital_twin_id,
            ref_name=db.collection_executions,
        )
        pprint(self.executions)
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
        workflows = db.get_collection(db.collection_workflows)
        workflow_options = {
            str(workflow["_id"]): f"{workflow.get('name')}"
            for workflow in workflows
        }
        if workflows:
            with ui.row().classes("w-full"):
                ui.select(
                    workflow_options,
                    on_change=lambda e: self.filter_components(str(e.value)),
                    label="workflows",
                    with_input=True,
                ).classes("w-1/2")
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
                    "delete_selected",
                    on_click=lambda: self.delete_selected(),
                    icon="clear",
                ).props("flat").classes("w-1/8")

    def add_header(self):
        headers = [
            "Select",
            "Id",
            "Created At",
            "Executed at",
            "deprecated",
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
            with ui.row().classes("w-full p-2 border grid grid-cols-10 gap-4 items-center"):
                ui.checkbox(
                    on_change=lambda e, execution_id=execution["_id"]: self.toggle_selection(e.value, execution_id)
                )
                #ui.label(execution['component']['componentName']).classes("truncate")
                #ui.label(execution['component_version']).classes("truncate")
                #ui.link(execution['component']['repoLink'], execution['component']['repoLink']).classes("truncate")
                #ui.label(execution['commitHash'][:8]).classes("text-center truncate")
                #ui.label(execution['component'].get("type") or execution.get("type")).classes("text-center truncate")
                ui.label(str(execution['_id'])).classes("text-center truncate")
                ui.label(execution['createdAt'].strftime('%Y-%m-%d')).classes("text-center truncate")
                ui.label(self.get_deprecated_display(execution["deprecated"])).classes("truncate")

    def toggle_selection(self, selected, execution_id):
        """toggle select for delete of executions"""
        print(f"Toggle called: {selected} for execution_id: {execution_id}")
        if selected:
            self.selected_execution_ids.add(execution_id)
        else:
            self.selected_execution_ids.remove(execution_id)

    def filter_workflows(self, workflow_id):
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

    def rebuild_rows(self):
        """rebuild rows with filters"""
        self.filtered_executions = self.executions
        if self.workflow_id:
            self.filtered_executions = [
                execution for execution in self.executions
                if str(execution["workflow_id"]) == self.execution_id
            ]
        if not self.show_deprecated:
            self.filtered_executions = [
                execution for execution in self.filtered_executions
                if not execution.get("deprecated", False)
            ]
        self.add_rows.refresh()

    def delete_selected(self):
        """delete selected executions"""
        pass
