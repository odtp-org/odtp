import pandas as pd
from nicegui import ui

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
    if not current_user:
        ui_theme.ui_add_first(
            item_name="user",
            page_link=ui_theme.PATH_USERS
        )     
        return
    with ui.right_drawer().style("background-color: #ebf1fa").props(
        "bordered width=500"
    ) as right_drawer:
        ui_workarea(current_user)
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
        ui.markdown(
            """
            #### Users digital twins
            """
        )
        digital_twins = db.get_sub_collection_items(
            collection=db.collection_users,
            sub_collection=db.collection_digital_twins,
            item_id=current_user["user_id"],
            ref_name=db.collection_digital_twins,
        )
        if digital_twins:
            df = pd.DataFrame(data=digital_twins)
            df["_id"] = df["_id"].astype("string")
            df["executions"] = (
                df["executions"].apply(helpers.pd_lists_to_counts).astype("string")
            )
            df = df[["_id", "name", "status", "created_at", "updated_at", "executions"]]
            ui.table.from_pandas(df)
        else:
            ui.label("You don't have digital twins yet. Start adding one.")
    except Exception as e:
        ui.notify(
            f"Digital Twin table could not be loaded. An Exception occured: {e}",
            type="negative",
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
    except Exception as e:
        ui.notify(
            f"Digital Twin Selection could not be loaded. An Exception occured: {e}",
            type="negative",
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
def ui_workarea(current_user):
    ui.markdown(
        """
        ### Work Area
        """
    )
    try:
        digital_twin = storage.get_active_object_from_storage(
            storage.CURRENT_DIGITAL_TWIN
        )
        if not digital_twin:
            ui.markdown(
                f"""
                #### Current Selection
                - **user**: {current_user.get("display_name")}
                
                #### Actions
                - add a digital twin
                - select a digital twin
                - list digital twins
                """
            )
            return            
        ui.markdown(
            f"""
            #### Current Selection
            - **user**: {current_user.get("display_name")}
            - **digital twin**: {digital_twin.get("name")}

            ##### Actions

            - add digital twin
            - select digital twin 
            - list digital twins
            """
        )
        ui.button(
            "Manage Executions",
            on_click=lambda: ui.open(ui_theme.PATH_EXECUTIONS),
            icon="link",
        )
    except Exception as e:
        ui.notify(
            f"Work area could not be loaded. An Exception occured: {e}", type="negative"
        )


def store_selected_digital_twin_id(value):
    if value == "None":
        return
    try:
        storage.storage_update_digital_twin(digital_twin_id=value)
    except Exception as e:
        ui.notify(
            f"Selected digital twin could not be stored. An Exception occured: {e}",
            type="negative",
        )
    else:
        storage.reset_storage_keep([storage.CURRENT_USER, storage.CURRENT_DIGITAL_TWIN])
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
            f"The digital twin could not be added in the database. An Exception occured: {e}",
            type="negative",
        )
    else:
        ui_digital_twin_select.refresh()
        ui_digital_twins_table.refresh()
        ui_add_digital_twin.refresh()
