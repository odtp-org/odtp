
from nicegui import app, ui
import odtp.mongodb.db as db


def add_digital_twin_form(current_user):
    ui.markdown(
        """
        #### Add a digital twin
        Provide a name for your digital twin project
        """
    )
    with ui.column().classes("w-full"):
        name_input = ui.input(
            label="Name",
            placeholder="name",
            validation={
                "Should be at least 6 characters long": lambda value: len(value.strip())
                >= 6
            },
        ).classes("w-1/2")

        ui.button(
            "Add new digital twin",
            on_click=lambda: add_digital_twin(
                name_input=name_input, user_id=current_user["user_id"]
            ),
            icon="add",
        )


def add_digital_twin(name_input, user_id):
    if not name_input.validate():
        ui.notify(
            "Fill in the form correctly before you can add a new digital twin",
            type="negative",
        )
        return
    try:
        digital_twin_id = db.add_digital_twin(userRef=user_id, name=name_input.value)
        ui.notify(
            f"A digital_twin with id {digital_twin_id} has been created",
            type="positive",
        )
        digital_twin_id = str(digital_twin_id)
        from odtp.dashboard.page_digital_twins.select import store_selected_digital_twin_id
        store_selected_digital_twin_id(digital_twin_id)
    except Exception as e:
        ui.notify(
            f"The digital twin could not be added in the database. An Exception occurred: {e}",
            type="negative",
        )
    else:
        from odtp.dashboard.page_digital_twins.main import (ui_tabs, ui_digital_twin_select,
            ui_digital_twins_table, ui_add_digital_twin
        )
        ui_digital_twin_select.refresh()
        ui_digital_twins_table.refresh()
        ui_add_digital_twin.refresh()
        ui_tabs.refresh()
