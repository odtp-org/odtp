from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.page_digital_twins.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme


class SelectDigitalTwinForm():
    def __init__(self, current_user):
        self.user_id = current_user["user_id"]
        self.digital_twin_id = ""
        self.digital_twin = None
        self.digital_twin_options = None
        self.get_digital_twin_options()
        self.get_current_digital_twin_from_storage()
        self.build_form()

    def get_digital_twin_options(self):
        db_digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=self.user_id,
            ref_name=db.collection_digital_twins,
        )
        if not db_digital_twins:
            return
        self.digital_twin_options = {
            str(digital_twin["_id"]): digital_twin.get("name")
            for digital_twin in db_digital_twins
        }

    def get_current_digital_twin_from_storage(self):
        self.digital_twin = storage.storage_get_current_digital_twin()

    def ui_no_digital_twins_yet(self):
        if not self.digital_twin_options:
            ui_theme.ui_no_items_yet("digital twins")

    @ui.refreshable
    def build_form(self):
        self.ui_no_digital_twins_yet()
        self.ui_select_form()
        self.show_detail()

    def ui_select_form(self):
        if not self.digital_twin_options:
            return
        ui.select(
            self.digital_twin_options,
            value=self.digital_twin_id,
            label="digital twins",
            on_change=lambda e: self.action_store_selected_digital_twin(str(e.value)),
            with_input=True,
        ).props("size=80")

    def action_store_selected_digital_twin(self, value):
        if not ui_theme.new_value_selected_in_ui_select(value):
            return
        self.digital_twin_id = value
        digital_twin = db.get_document_by_id(
            document_id=self.digital_twin_id, collection=db.collection_digital_twins
        )
        storage.set_current_digital_twin(digital_twin)
        self.get_current_digital_twin_from_storage()
        self.refresh()

    def refresh(self):
        self.build_form.refresh()
        from odtp.dashboard.page_digital_twins.main import ui_workarea
        ui_workarea.refresh()

    def show_detail(self):
        if not self.digital_twin:
            return
        with ui.grid(columns='1fr 5fr').classes('w-full'):
            ui.label("Created At")
            ui.label(self.digital_twin['created_at'])
            ui.label("Updated At")
            ui.label(self.digital_twin['updated_at'])
            ui.label("Executions")
            ui.link(
                self.digital_twin['execution_count'],
                ui_theme.PATH_EXECUTIONS,
            )
