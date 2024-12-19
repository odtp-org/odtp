from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme


from nicegui import ui

class ExecutionDisplay:
    def __init__(self, digital_twin_id):
        """init form"""
        self.execution = None
        self.execution_id = None
        self.digital_twin_id = digital_twin_id
        self.execution_options = None
        self.get_execution_options()
        self.build_form()

    def get_execution_options(self):
        """get execution options"""
        self.execution_options = helpers.get_execution_select_options(
            digital_twin_id=self.digital_twin_id
        )

    @ui.refreshable
    def ui_run_execution(self):
        if not self.execution_id:
            return
        ui.button(
            "Prepare and Run Executions",
            on_click=lambda: ui.open(ui_theme.PATH_RUN),
            icon="link",
        )

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_execution_select()
        self.ui_run_execution()
        self.ui_execution_info()

    @ui.refreshable
    def ui_execution_select(self):
        """ui element for component select"""
        ui.select(
            self.execution_options,
            value=self.execution_id,
            on_change=lambda e: self.set_execution(str(e.value)),
            label="execution",
            with_input=True,
        ).classes("w-1/2")

    def set_execution(self, execution_id):
        """called when a new component has been selected"""
        self.execution_id = execution_id
        self.component = db.get_document_by_id(
            document_id=self.execution_id, collection=db.collection_executions
        )
        self.ui_execution_info.refresh()
        self.ui_run_execution.refresh()

    @ui.refreshable
    def ui_execution_info(self):
        """ui execution"""
        if not self.execution_id:
            return
        ui.label(self.execution_id)
        execution = helpers.build_execution_with_steps(self.execution_id)
        execution_title = execution.get("title")
        version_tags = execution.get("version_tags")
        current_ports = execution.get("ports")
        current_parameters = execution.get("parameters")
        ui_theme.ui_execution_display(
            execution_title=execution_title,
            version_tags=version_tags,
            ports=current_ports,
            parameters=current_parameters,
        )
