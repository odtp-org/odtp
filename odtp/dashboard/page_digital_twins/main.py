import logging

from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.page_digital_twins.table as table
import odtp.dashboard.page_digital_twins.select as select
import odtp.dashboard.page_digital_twins.add as add
import odtp.dashboard.page_digital_twins.workarea as workarea
import odtp.mongodb.db as db

TAB_SELECT = "Select a digital twin"
TAB_ADD = "Add a new digital twin"


log = logging.getLogger("__name__")


def content() -> None:
    current_user = storage.get_active_object_from_storage(storage.CURRENT_USER)
    ui_workarea(current_user)
    if current_user:
        ui_tabs(current_user)


@ui.refreshable
def ui_tabs(current_user):
    with ui.tabs() as tabs:
        select = ui.tab(TAB_SELECT)
        add = ui.tab(TAB_ADD)
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(select):
            ui_digital_twin_select(current_user)
            ui_digital_twins_table(current_user)
        with ui.tab_panel(add):
            ui_add_digital_twin(current_user)


@ui.refreshable
def ui_digital_twins_table(current_user):
    try:
        current_digital_twin = storage.get_active_object_from_storage(
            (storage.CURRENT_DIGITAL_TWIN)
        )
        digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=current_user["user_id"],
            ref_name=db.collection_digital_twins,
        )
        table.ui_table_layout(
            digital_twins=digital_twins
        )   
    except Exception as e:
        log.exception(
            f"Digital Twin table could not be loaded. An Exception occurred: {e}"
        )

@ui.refreshable
def ui_digital_twins_nodf_table(current_user):
    current_digital_twin = storage.get_active_object_from_storage(
        (storage.CURRENT_DIGITAL_TWIN)
    )

    digital_twins = db.get_sub_collection_items(
        collection=db.collection_users,
        sub_collection=db.collection_digital_twins,
        item_id=current_user["user_id"],
        ref_name=db.collection_digital_twins,
    )

    with ui.column().classes("w-full"):
        if not digital_twins:
            ui_theme.ui_no_items_yet("Digital Twins")
            return

        versions_cleaned = [
            helpers.component_version_for_table(version) for version in versions
        ]
        
        df = pd.DataFrame(data=versions_cleaned)
        df = df.sort_values(by=["component", "version"], ascending=False)

        repo_col_index = df.columns.get_loc("repository")

        # Container for the table
        with ui.column().classes("w-full border rounded-lg overflow-hidden"):
            # Header row
            with ui.row().classes("w-full bg-gray-100 p-2 font-bold border-b"):
                # Data columns
                for col in df.columns:
                    ui.label(col.capitalize()).classes("flex-1 px-4")
                # Action column header
                ui.label("Actions").classes("w-24 text-center")

            # Data rows
            for _, row in df.iterrows():
                with ui.row().classes("w-full hover:bg-gray-50 border-b last:border-b-0"):
                    # Data columns
                    for idx, value in enumerate(row):
                        with ui.element().classes("flex-1 px-4 py-2"):
                            if idx == repo_col_index:
                                ui.link(str(value), str(value)).classes("text-blue-500 hover:text-blue-700")
                            else:
                                ui.label(str(value))
                    # Action button
                    with ui.element().classes("w-24 p-2 flex justify-center"):
                        ui.button(
                            "Delete", 
                            on_click=lambda v=row["id"]: handle_action(v)
                        ).classes(
                            "bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
                        )

def handle_action(_id: str):
    _ = helpers.delete_component(_id)
    ui_component_nodf_table.refresh()


@ui.refreshable
def ui_digital_twin_select(current_user) -> None:
    try:
        current_digital_twin = storage.get_active_object_from_storage(
            (storage.CURRENT_DIGITAL_TWIN)
        )
        user_id = current_user["user_id"]
        digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=user_id,
            ref_name=db.collection_digital_twins,
        )        
        select.digital_twin_select_form(
            current_user=current_user,
            current_digital_twin=current_digital_twin,
            digital_twins=digital_twins,
        )
    except Exception as e:
        log.exception(
            f"Digital Twin Selection could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_add_digital_twin(current_user):
    try:
        add.add_digital_twin_form(current_user)
    except Exception as e:
        log.exception(
            f"Digital Twin Selection could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_workarea(current_user):
    try:
        user_workdir = storage.get_value_from_storage_for_key(storage.CURRENT_USER_WORKDIR)    
        current_digital_twin = storage.get_active_object_from_storage(
            storage.CURRENT_DIGITAL_TWIN
        )
        workarea.ui_workarea_form(
            current_user=current_user,
            current_digital_twin=current_digital_twin,
            user_workdir=user_workdir
        )
    except Exception as e:
        log.exception(f"Work area could not be loaded. An Exception happened: {e}")    
