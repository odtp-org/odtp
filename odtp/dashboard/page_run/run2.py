import json
from pprint import pprint
from nicegui import ui, app
import odtp.mongodb.db as db
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.storage as storage


from nicegui import ui

class ExecutionRunForm:
    def __init__(self, digital_twin_id, execution_id):
        """init form"""
        self.execution_id = execution_id
        self.digital_twin_id = digital_twin_id
        self.get_execution()
        self.build_form()

    def get_execution(self):
        self.execution = helpers.build_execution_with_steps(self.execution_id)
        pprint(self.execution)
        self.ui_execution_info.refresh()

    @ui.refreshable
    def ui_add_project_path(self):
        if not self.execution:
            return
        ui.button(
            "Prepare and Run Executions",
            on_click=lambda: ui.open(ui_theme.PATH_RUN),
            icon="link",
        )

    def db_save_project_path(self):
        db.update_execution()

    @ui.refreshable
    def ui_prepare_execution(self):
        if not self.execution:
            return
        ui.button(
            "Prepare and Run Executions",
            on_click=lambda: ui.open(ui_theme.PATH_RUN),
            icon="link",
        )

    @ui.refreshable
    def ui_run_execution(self):
        if not self.execution:
            return
        ui.button(
            "Prepare and Run Executions",
            on_click=lambda: ui.open(ui_theme.PATH_RUN),
            icon="link",
        )

    @ui.refreshable
    def ui_check_logs(self):
        if not self.execution:
            return
        ui.button(
            "Prepare and Run Executions",
            on_click=lambda: ui.open(ui_theme.PATH_RUN),
            icon="link",
        )

    @ui.refreshable
    def ui_execution_info(self):
        if not self.execution_id:
            return
        ui.label(f"Run for execution {self.execution_id}")
        ui.label(f"created: {self.execution['createdAt']}"),
        ui.label(f"inputs: {self.execution['inputs']}"),
        ui.label(f"outputs: {self.execution['outputs']}"),
        ui.label(f"ports: {self.execution['ports']}"),
        ui.label(f"steps: {self.execution['steps']}"),
        ui.label(f"version_tags: {self.execution['version_tags']}"),
        ui.label(f"versions: {self.execution['versions']}"),

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_execution_info()
        self.ui_prepare_execution()
        self.ui_run_execution()
