import json
import logging

from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db


def digital_twin_select_form(current_user, current_digital_twin, digital_twins):
    if not digital_twins:
        ui_theme.ui_no_items_yet("Digital Twins")
        return
    if current_digital_twin:
        value = current_digital_twin["digital_twin_id"]
    else:
        value = ""
    digital_twin_options = {
        str(digital_twin["_id"]): digital_twin.get("name")
        for digital_twin in digital_twins
    }
    ui.select(
        digital_twin_options,
        value=value,
        label="digital twins",
        on_change=lambda e: store_selected_digital_twin_id(str(e.value)),
        with_input=True,
    ).props("size=80")


def store_selected_digital_twin_id(value):
    try:
        if not ui_theme.new_value_selected_in_ui_select(value):
            return
        digital_twin_id = value
        digital_twin = db.get_document_by_id(
            document_id=digital_twin_id, collection=db.collection_digital_twins
        )
        current_digital_twin = json.dumps(
            {"digital_twin_id": digital_twin_id, "name": digital_twin.get("name")}
        )
        app.storage.user[storage.CURRENT_DIGITAL_TWIN] = current_digital_twin
    except Exception as e:
        logging.error(
            f"Selected digital twin could not be stored. An Exception happened: {e}"
        )
    else:
        storage.reset_storage_keep(
            [
                storage.CURRENT_USER,
                storage.CURRENT_DIGITAL_TWIN,
                storage.CURRENT_USER_WORKDIR,
            ]
        )
        from odtp.dashboard.page_digital_twins.main import ui_workarea
        ui_workarea.refresh()

