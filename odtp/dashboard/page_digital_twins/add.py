
from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.page_digital_twins.storage as storage
import odtp.dashboard.page_digital_twins.validation as validation


class DigitalTwinAddForm:
    def __init__(self, current_user):
        self.user_id = current_user.get("user_id")
        self.build_form()

    def build_form(self):
        ui.markdown(
            """
            #### Add a digital twin
            Provide a unique name for your digital twin project
            """
        )
        with ui.column().classes("w-full"):
            name_input = ui.input(
                label="Name",
                placeholder="name",
                validation={
                    "Should be unique and at least 6 characters long" \
                    : lambda value: validation.validate_digital_twin_name_unique(value.strip())
                },
            ).classes("w-1/2")

            ui.button(
                "Add new digital twin",
                on_click=lambda: self.db_add_digital_twin(
                    name_input=name_input, user_id=self.user_id
                ),
                icon="add",
            )

    def db_add_digital_twin(self, name_input, user_id):
        if not name_input.validate():
            ui.notify(
                "Fill in the form correctly before you can add a new digital twin",
                type="negative",
            )
            return
        self.digital_twin_name = name_input.value
        digital_twin_id = db.add_digital_twin(userRef=user_id, name=self.digital_twin_name)
        ui.notify(
            f"A digital_twin with the name {self.digital_twin_name} has been created",
            type="positive",
        )
        self.digital_twin_id = str(digital_twin_id)
        digital_twin = db.get_document_by_id(
            document_id=self.digital_twin_id, collection=db.collection_digital_twins
        )
        storage.set_current_digital_twin(digital_twin)
        self.refresh_page()

    def refresh_page(self):
        from odtp.dashboard.page_digital_twins.main import (
            ui_digital_twin_select, ui_digital_twins_manage, ui_add_digital_twin, ui_workarea, ui_tabs
        )
        ui_digital_twin_select.refresh()
        ui_add_digital_twin.refresh()
        ui_workarea.refresh()
        ui_digital_twins_manage.refresh()
        ui_tabs.refresh()
