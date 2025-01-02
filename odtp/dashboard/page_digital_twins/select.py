from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.page_digital_twins.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme


class SelectDigitalTwinForm():
    def __init__(self, current_user):
        self.user_id = current_user["user_id"]
        self.digital_twins = None
        self.digital_twin_id = ""
        self.digital_twin_name = None
        self.digital_twin_options = None
        self.get_digital_twin_options()
        self.build_form()

    def get_digital_twin_options(self):
        self.digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=self.user_id,
            ref_name=db.collection_digital_twins,
        )
        if not self.digital_twins:
            return
        self.digital_twin_options = {
            str(digital_twin["_id"]): digital_twin.get("name")
            for digital_twin in self.digital_twins
        }

    def get_current_digital_twin_from_storage(self):
        current_digital_twin = storage.storage_get_current_digital_twin()
        if not current_digital_twin:
            return
        self.digital_twin_id = current_digital_twin["digital_twin_id"]
        self.digital_name = current_digital_twin["digital_twin_name"]

    def ui_no_digital_twins_yet(self):
        if not self.digital_twins:
            ui_theme.ui_no_items_yet("digital twins")

    @ui.refreshable
    def build_form(self):
        self.ui_no_digital_twins_yet()
        self.get_current_digital_twin_from_storage()
        if not self.digital_twin_options:
            return
        self.ui_select_form()

    def ui_select_form(self):
        ui.select(
            self.digital_twin_options,
            value=self.digital_twin_id,
            label="digital twins",
            on_change=lambda e: self.store_selected_digital_twin(str(e.value)),
            with_input=True,
        ).props("size=80")

    def storage_set_current_digital_twin(self):
        storage.set_current_digital_twin(
            digital_twin_id=self.digital_twin_id,
            digital_twin_name=self.digital_twin_name
        )

    def get_digital_twin_from_db(self):
        digital_twin = db.get_document_by_id(
            document_id=self.digital_twin_id, collection=db.collection_digital_twins
        )
        self.digital_twin_name = digital_twin.get("name")

    def store_selected_digital_twin(self, value):
        if not ui_theme.new_value_selected_in_ui_select(value):
            return
        self.digital_twin_id = value
        self.get_digital_twin_from_db()
        self.storage_set_current_digital_twin()
        self.build_form.refresh()
        from odtp.dashboard.page_digital_twins.main import ui_workarea
        ui_workarea.refresh()
