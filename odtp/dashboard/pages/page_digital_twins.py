import pandas as pd
from nicegui import app, ui

import odtp.dashboard.utils.format as format
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db


def content() -> None:
    ui.markdown(
        """
        # Manage Digital Twins
        """
    )
    current_user = storage.get_active_object_from_storage("user")
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
                df["executions"].apply(format.pd_lists_to_counts).astype("string")
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
            validation={"Can not be empty": lambda value: len(value.strip()) != 0},
        ).classes("w-2/3")

        ui.button(
            "Add new digital twin",
            on_click=lambda: add_digital_twin(
                name=name_input.value, user_id=current_user["user_id"]
            ),
        )


@ui.refreshable
def ui_workarea(current_user):
    ui.markdown(
        """
        ### Work Area
        """
    )
    try:
        if not current_user:
            ui.button("Select a user", on_click=lambda: ui.open(ui_theme.PATH_USERS))
        else:
            digital_twin = storage.get_active_object_from_storage("digital_twin")
            if digital_twin:
                ui.markdown(
                    f"""
                    #### User / Digital Twin
                    - {current_user.get("display_name")} / {digital_twin.get("name")}
                    
                    #### Actions
                    - [manage executions of the digital twin](/executions)
                    """
                )
                with ui.button(
                    "Manage Executions",
                    on_click=lambda: ui.open(ui_theme.PATH_EXECUTIONS),
                ):
                    ui.tooltip(
                        "Click here to manage the executions for this digital twin"
                    )
                with ui.button("Reset work area", on_click=lambda: app_storage_reset()):
                    ui.tooltip(f"Click here to reset the user workarea")
            else:
                ui.markdown(
                    f"""
                    #### User
                    - {current_user.get("display_name")}
                    
                    #### Actions
                    - add a digital twin
                    - select a digital twin
                    """
                )
    except Exception as e:
        ui.notify(
            f"Work area could not be loaded. An Exception occured: {e}", type="negative"
        )


def store_selected_digital_twin_id(value):
    try:
        storage.storage_update_digital_twin(digital_twin_id=value)
    except Exception as e:
        ui.notify(
            f"Selected digital twin could not be stored. An Exception occured: {e}",
            type="negative",
        )
    finally:
        ui_workarea.refresh()


def app_storage_reset():
    try:
        storage.app_storage_reset("digital_twin")
    except Exception as e:
        ui.notify(
            f"Work area could not be reset. An Exception occured: {e}", type="negative"
        )
    finally:
        ui_workarea.refresh()
        ui_digital_twin_select.refresh()


def add_digital_twin(name, user_id):
    if name and user_id:
        try:
            digital_twin_id = db.add_digital_twin(userRef=user_id, name=name)
            ui.notify(
                f"A digital_twin with id {digital_twin_id} has been created",
                type="positive",
            )
        except Exception as e:
            ui.notify(
                f"The digital twin could not be added in the database. An Exception occured: {e}",
                type="negative",
            )
        finally:
            ui_digital_twin_select.refresh()
            ui_digital_twins_table.refresh()
            ui_add_digital_twin.refresh()
    else:
        ui.notify(
            f"A digital twin can only be added once the form is filled", type="negative"
        )
