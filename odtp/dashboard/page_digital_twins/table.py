from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.page_digital_twins.storage as storage


class DigitalTwinTable():
    def __init__(self, current_user):
        self.user_id = current_user["user_id"]
        self.get_digital_twins_from_db()
        if not self.digital_twins:
            ui.label("No digital twins yet").classes("text-red-500")
            return
        self.rows = []
        self.build_table()

    def get_digital_twins_from_db(self):
        self.digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=self.user_id,
            ref_name=db.collection_digital_twins,
        )

    @ui.refreshable
    def build_table(self):
        with ui.column().classes("w-1/2"):
            self.add_header()
            self.add_rows()

    def add_header(self):
        headers = [
            {"text": "Name", "col_span": 2},
            {"text": "Id", "col_span": 2},
            {"text": "Created At", "col_span": 1},
            {"text": "Updated At", "col_span": 1},
            {"text": "Executions", "col_span": 1},
        ]
        with ui.row().classes("w-full bg-gray-200 p-2 border-b grid grid-cols-7 gap-4 justify-items-start"):
            for header in headers:
                ui.label(header["text"]).classes(
                    f"font-bold text-center truncate col-span-{header['col_span']}"
                )

    def display_date(self, datetime_field):
        return datetime_field.strftime("%Y-%m-%d")

    def display_count(self, executions):
        return len(executions)

    def refresh_page(self):
        from odtp.dashboard.page_digital_twins.main import (
            ui_digital_twin_select, ui_workarea, ui_tabs
        )
        ui_digital_twin_select.refresh()
        ui_workarea.refresh()
        ui_tabs.refresh()

    def storage_set_current_digital_twin(self, digital_twin):
        storage.set_current_digital_twin(digital_twin)
        self.refresh_page()

    @ui.refreshable
    def add_rows(self):
        for digital_twin in self.digital_twins:
            with ui.row().classes("w-full p-2 border-b grid grid-cols-7 gap-4 flex items-center justify-items-start"):
                ui.button(
                    digital_twin['name'],
                    on_click=lambda digital_twin=digital_twin: self.storage_set_current_digital_twin(
                        digital_twin
                    ),
                ).classes(f"truncate col-span-2").props("flat no-caps")
                ui.label(str(digital_twin["_id"])).classes(f"truncate col-span-2")
                ui.label(self.display_date(digital_twin['created_at'])).classes(f"truncate col-span-1")
                ui.label(self.display_date(digital_twin['updated_at'])).classes(f"truncate col-span-1")
                ui.link(
                    f"{self.display_count(digital_twin['executions'])}",
                    ui_theme.PATH_EXECUTIONS,
                ).classes(f"truncate col-span-1")
