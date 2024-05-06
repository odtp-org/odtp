import pandas as pd
import json
import logging
from nicegui import ui, app

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db


def content() -> None:
    ui.markdown(
        """
        # Manage Digital Twins
        """
    )
    current_user = storage.get_active_object_from_storage(
        storage.CURRENT_USER
    )
    user_workdir = storage.get_value_from_storage_for_key(
        storage.CURRENT_USER_WORKDIR
    )      
    if not current_user:
        ui_theme.ui_add_first(
            item_name="user",
            page_link=ui_theme.PATH_USERS
        )     
        return     
    with ui.right_drawer().classes("bg-slate-50").props(
        "bordered width=500"
    ) as right_drawer:
        ui_workarea(current_user, user_workdir)
    if current_user:
        with ui.tabs().classes("w-full") as tabs:
            select = ui.tab("Select a digital twin")
            add = ui.tab("Add a new digital twin")
        with ui.tab_panels(tabs, value=select).classes("w-full"):
            with ui.tab_panel(select):
                ui_digital_twin_select(current_user)
                ui_digital_twins_table(current_user)
            with ui.tab_panel(add):
                ui_add_digital_twin(current_user)


@ui.refreshable
def ui_digital_twins_table(current_user):
    try:
        digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=current_user["user_id"],
            ref_name=db.collection_digital_twins,
        )
        if not digital_twins: 
            return
        ui.markdown(
            """
            #### Users digital twins
            """
        )            
        if digital_twins:
            df = pd.DataFrame(data=digital_twins)
            df["_id"] = df["_id"].astype("string")
            df["executions"] = (
                df["executions"].apply(helpers.pd_lists_to_counts).astype("string")
            )
            df = df[["_id", "name", "status", "created_at", "updated_at", "executions"]]
            ui.table.from_pandas(df)
    except Exception as e:
        logging.error(
            f"Digital Twin table could not be loaded. An Exception occured: {e}"
        )


@ui.refreshable
def ui_digital_twin_select(current_user) -> None:
    try:
        ui.markdown(
            """
            #### Select digital twin
            """
        )
        current_digital_twin = storage.get_active_object_from_storage(
            (storage.CURRENT_DIGITAL_TWIN)
        )
        if current_digital_twin:
            value = current_digital_twin["digital_twin_id"]
        else:
            value = ""
        user_id = current_user["user_id"]
        digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=user_id,
            ref_name=db.collection_digital_twins,
        )
        if not digital_twins:
            ui_theme.ui_no_items_yet("Digital Twins")
            return
        digital_twin_options = {
            str(digital_twin["_id"]): digital_twin.get("name")
            for digital_twin in digital_twins
        }
        ui.select(
            digital_twin_options,
            value=value,
            label="digital twins",
            on_change=lambda e: store_selected_digital_twin_id(digital_twin_id=str(e.value)),
            with_input=True,
        ).props("size=80")
    except Exception as e:
        logging.error(
            f"Digital Twin Selection could not be loaded. An Exception occured: {e}"
        )


@ui.refreshable
def ui_add_digital_twin(current_user):
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
            validation={"Should be at least 6 characters long": lambda value: len(value.strip()) >= 6},
        ).classes("w-2/3")

        ui.button(
            "Add new digital twin",
            on_click=lambda: add_digital_twin(
                name_input=name_input, user_id=current_user["user_id"]
            ),
            icon="add",
        )


@ui.refreshable
def ui_workarea(current_user, user_workdir):
    current_digital_twin = storage.get_active_object_from_storage(
        storage.CURRENT_DIGITAL_TWIN
    )
    if not user_workdir:
        user_workdir_display = "-"
    else:
        user_workdir_display = user_workdir     
    if not current_digital_twin: 
        digital_twin_display = "-"  
    else:
        digital_twin_display = current_digital_twin.get("name")           
    ui.markdown(
        """
        ### Work Area
        """
    )
    try:
        ui.markdown(
            f"""
            #### Current Selection
            - **user**: {current_user.get("display_name")}
            - **digital twin**: {digital_twin_display}
            - **work directory**: {user_workdir_display}
            
            #### Actions
            - add a digital twin
            - select a digital twin
            - list digital twins
            """
        )
        ui.button(
            "Manage Executions",
            on_click=lambda: ui.open(ui_theme.PATH_EXECUTIONS),
            icon="link",
        )
    except Exception as e:
        logging.error(
            f"Work area could not be loaded. An Exception happened: {e}"
        )


def store_selected_digital_twin_id(digital_twin_id):
    if not digital_twin_id or digital_twin_id == "":
        return
    try:
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
            [storage.CURRENT_USER, storage.CURRENT_DIGITAL_TWIN, storage.CURRENT_USER_WORKDIR]
        )
        ui_workarea.refresh()


def add_digital_twin(name_input, user_id):
    if not name_input.validate():
        ui.notify("Fill in the form correctly before you can add a new digital twin", type="negative")
        return
    try:
        digital_twin_id = db.add_digital_twin(userRef=user_id, name=name_input.value)
        ui.notify(
            f"A digital_twin with id {digital_twin_id} has been created",
            type="positive",
        )
    except Exception as e:
        ui.notify(
            f"The digital twin could not be added in the database. An Exception occurred: {e}",
            type="negative",
        )
    else:
        ui_digital_twin_select.refresh()
        ui_digital_twins_table.refresh()
        ui_add_digital_twin.refresh()
