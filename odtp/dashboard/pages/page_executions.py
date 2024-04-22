import pandas as pd
from nicegui import ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.helpers.utils as odtp_utils
import odtp.mongodb.db as db


def content() -> None:
    ui.markdown(
        """
        # Manage Executions
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
    current_digital_twin = storage.get_active_object_from_storage(
        storage.CURRENT_DIGITAL_TWIN
    )
    if not current_digital_twin:
        ui_theme.ui_add_first(
            item_name="digital twin",
            page_link=ui_theme.PATH_DIGITAL_TWINS
        )     
        return
    with ui.right_drawer(fixed=False).classes("bg-slate-50").props(
        "bordered width=500"
    ):
        ui_workarea(
            current_digital_twin=current_digital_twin, 
            current_user=current_user
        )
    with ui.tabs().classes("w-full") as tabs:
        select = ui.tab("Select an execution")
        add = ui.tab("Add an execution")
        table = ui.tab("Execution table")
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(select):
            ui_execution_select(current_digital_twin)
            ui_execution_details()
        with ui.tab_panel(add):
            ui_add_execution(current_digital_twin)
        with ui.tab_panel(table):
            ui_executions_table(current_digital_twin)


@ui.refreshable
def ui_execution_select(current_digital_twin) -> None:
    try:
        ui.markdown(
            """
            #### Select Execution
            """
        )
        digital_twin_id = current_digital_twin["digital_twin_id"]
        current_execution = storage.get_active_object_from_storage(
            storage.CURRENT_EXECUTION
        )
        if current_execution:
            selected_value = current_execution["execution_id"]
        else:
            selected_value = None
        executions = db.get_sub_collection_items(
            collection=db.collection_digital_twins,
            sub_collection=db.collection_executions,
            item_id=digital_twin_id,
            ref_name=db.collection_executions,
        )
        if not executions:
            ui.label("You don't have executions yet. Start adding one.")
            return
        execution_options = {}
        for execution in executions:
            execution_options[
                str(execution["_id"])
            ] = f"{execution['start_timestamp'].strftime('%d/%m/%y')} {execution.get('title')}"
        if execution_options:
            ui.select(
                execution_options,
                value=selected_value,
                label="executions",
                on_change=lambda e: store_selected_execution(e.value),
                with_input=True,
            ).classes("w-full")
            ui.button(
                "Cancel Execution Selection",
                on_click=lambda: cancel_execution_selection(),
                icon="cancel",
            )
    except Exception as e:
        ui.notify(
            f"Execution selection could not be loaded. An Exception occured: {e}",
            type="negative",
        )


@ui.refreshable
def ui_executions_table(current_digital_twin):
    try:
        executions = db.get_sub_collection_items(
            collection=db.collection_digital_twins,
            sub_collection=db.collection_executions,
            item_id=current_digital_twin["digital_twin_id"],
            ref_name=db.collection_executions,
        )
        if not executions:
            ui.label("You don't have executions yet. Start adding one.")
            return
        df = pd.DataFrame(data=executions)
        df["_id"] = df["_id"].astype("string")
        df["timestamp"] = df["start_timestamp"]
        df["steps"] = df["steps"].apply(helpers.pd_lists_to_counts).astype("string")
        df = df[["_id", "timestamp", "title", "steps"]]
        ui.table.from_pandas(df)
    except Exception as e:
        ui.notify(
            f"Execution table could not be loaded. An Exception occured: {e}",
            type="negative",
        )


@ui.refreshable
def ui_add_execution(current_digital_twin):
    ui.markdown(
        """
        #### Add Execution
        """
    )
    ui.button(
        "Cancel Execution Entry",
        on_click=lambda: cancel_execution_entry(),
        icon="cancel",
    )
    try:
        digital_twin_id = current_digital_twin.get("digital_twin_id")
        current_execution_to_add = storage.get_active_object_from_storage(
            storage.NEW_EXECUTION
        )
        if not current_execution_to_add:
            component_versions = db.get_collection(collection=db.collection_versions)
            if not component_versions:
                ui.label("There are no components yet.")
                return
            select_options = {}
            for i, version in enumerate(component_versions):
                versin_display_name = odtp_utils.get_execution_step_name(
                    component_name=version["component"]["componentName"],
                    component_version=version["component_version"],
                )
                select_options[
                    (str(version["_id"]), i, versin_display_name)
                ] = versin_display_name
            name_input = ui.input(
                label="Execution title",
                placeholder="Execution title",
                validation={
                    "Must be at least 4 characters long": lambda value: len(
                        value.strip()
                    )
                    >= 4
                },
            ).classes("w-full")
            component_versions_input = (
                ui.select(
                    select_options,
                    multiple=True,
                    label="component versions",
                    with_input=False,
                )
                .classes("w-full")
                .props("use-chips")
            )
            parameter_count_input = ui.number(
                value=3, label="Maximal number of parameters per step"
            )
            ui.button(
                "Proceed to next step",
                on_click=lambda: store_new_execution_init(
                    form_state=storage.FORM_STATE_START,
                    name=name_input.value,
                    version_tuples=component_versions_input.value,
                    digital_twin_id=digital_twin_id,
                    parameter_count=parameter_count_input.value,
                ),
            )
            return
        step_count = int(current_execution_to_add["step_count"])
        current_step_nr = int(current_execution_to_add["current_step_nr"])
        if current_step_nr < step_count:
            parameter_count = int(current_execution_to_add["parameter_count"])
            step_name = current_execution_to_add["step_names"][current_step_nr]
            parameter_keys = []
            parameter_values = []
            ui.markdown(
                f"""
                ###### Extras for step {current_step_nr} / {step_count}
            """
            )
            ui.mermaid(
                f"""
            graph TD;
                {helpers.get_workflow_mairmaid([step_name])};
            """
            )
            with ui.row().classes("w-full no-wrap"):
                ui.label("Parameters").classes("text-lg")
            for i in range(parameter_count):    
                with ui.row().classes("w-full no-wrap"):
                    with ui.column().classes("w-1/2"):
                        parameter_keys.append(ui.input(f"key").classes("w-full"))
                    with ui.column().classes("w-1/2"):
                        parameter_values.append(ui.input(f"value").classes("w-full"))
            with ui.row():
                ui.label("Add Port mappings: optional").classes("w-full text-lg")
                ports_input = ui.input(
                    f"comma separated list of port mappingss",
                    placeholder="8080:8001,6000:6001",
                ).classes("w-full")
            ui.button(
                "Proceed to next step",
                on_click=lambda: store_new_execution_step(
                    parameter_keys=[
                        input_value.value
                        for input_value in parameter_keys
                        if input_value.value
                    ],
                    parameter_values=[
                        input_value.value
                        for input_value in parameter_values
                        if input_value.value
                    ],
                    ports_mapping_inputs=ports_input.value,
                ),
            )
            return
        ui_new_execution_details(current_execution_to_add)
        ui.button(
            "Save execution",
            on_click=lambda: save_new_execution(
                name=current_execution_to_add.get("name"),
                versions=current_execution_to_add.get("versions"),
                ports=current_execution_to_add.get("ports"),
                dt_id=current_execution_to_add.get("digital_twin_id"),
                parameters=current_execution_to_add.get("parameters"),
            ),
        )
    except Exception as e:
        ui.notify(
            f"Component selection could not be loaded. An Exception occured: {e}",
            type="negative",
        )


def store_new_execution_init(
    name, version_tuples, digital_twin_id, form_state, parameter_count
):
    try:
        if form_state == storage.FORM_STATE_START:
            storage.storage_update_add_execution_init(
                name=name,
                version_tuples=version_tuples,
                digital_twin_id=digital_twin_id,
                form_state=form_state,
                parameter_count=parameter_count,
            )
    except Exception as e:
        ui.notify("Execution could not be stored: execption occured: {e}")
    else:
        ui_add_execution.refresh()


def store_new_execution_step(parameter_keys, parameter_values, ports_mapping_inputs):
    try:
        storage.storage_update_add_execution_step(
            parameter_keys=parameter_keys,
            parameter_values=parameter_values,
            ports_mapping_inputs=ports_mapping_inputs,
        )
    except Exception as e:
        ui.notify(f"Execution could not be stored: execption occured: {e}")
    else:
        ui_add_execution.refresh()


def save_new_execution(
    dt_id,
    name,
    versions,
    parameters,
    ports,
):
    try:
        execution_id, step_ids = db.add_execution(
            dt_id=dt_id,
            name=name,
            versions=versions,
            parameters=parameters,
            ports=ports,
        )
        execution_id_display = str(execution_id)
        step_ids_display = ",".join([str(step_id) for step_id in step_ids])
        ui.notify(
            f"An execution with id {execution_id_display} and steps: {step_ids_display} has been created",
            type="positive",
        )
    except Exception as e:
        ui.notify(
            f"Execution could not be added. An exception occured: {e}", type="negative"
        )
    else:
        storage.reset_storage_delete([storage.NEW_EXECUTION])
        ui_add_execution.refresh()
        ui_executions_table.refresh()
        ui_execution_select.refresh()
        ui_execution_details.refresh()


def ui_new_execution_details(new_execution):
    try:
        if not new_execution:
            return
        step_names = new_execution.get("step_names")
        ports_all = new_execution.get("ports")
        parameters_all = new_execution.get("parameters")
        with ui.row().classes("w-full no-wrap"):
            with ui.column().classes("w-1/2"):
                ui.mermaid(
                    f"""
                    graph TD;
                        {helpers.get_workflow_mairmaid(step_names)};
                    """
                )
            with ui.column().classes("w-1/2"):
                for i, step in enumerate(step_names):
                    with ui.card().classes("bg-violet-100"):
                        ports = ports_all[i]
                        parameters = parameters_all[i]
                        if ports:
                            ports_display = ",  ".join(ports)
                        else:
                            ports_display = "NA"
                        if parameters:
                            parameters_display = ", ".join(
                                [
                                    f"{key} : {value}"
                                    for key, value in parameters.items()
                                ]
                            )
                        else:
                            parameters_display = "NA"
                        ui.label(step_names[i])
                        ui.markdown(
                            f"""
                            - Ports: {ports_display}
                            - Paramters: {parameters_display}
                        """
                        )
    except Exception as e:
        ui.notify(
            f"Execution details could not be loaded. An Exception occured: {e}",
            type="negative",
        )


@ui.refreshable
def ui_execution_details():
    try:
        current_execution = storage.get_active_object_from_storage(
            storage.CURRENT_EXECUTION
        )
        if not current_execution:
            return
        step_ids = current_execution["steps"]
        steps = db.get_document_by_ids_in_collection(
            document_ids=step_ids, collection=db.collection_steps
        )
        step_names = current_execution.get("step_names")
        ui.markdown(
            f"""
            - **title**: {current_execution.get('title')} 
            - **created at**: {current_execution.get('timestamp')}   
            """
        )
        with ui.row().classes("w-full no-wrap"):
            with ui.column().classes("w-1/2"):
                ui.mermaid(
                    f"""
                    graph TD;
                        {helpers.get_workflow_mairmaid(step_names)};
                    """
                )
            with ui.column().classes("w-1/2"):
                for i, step in enumerate(steps):
                    with ui.card().classes("bg-violet-100"):
                        ports = step.get("ports")
                        parameters = step.get("parameters")
                        if ports:
                            ports_display = ",  ".join(ports)
                        else:
                            ports_display = "NA"
                        if parameters:
                            parameters_display = ", ".join(
                                [
                                    f"{key} : {value}"
                                    for key, value in parameters.items()
                                ]
                            )
                        else:
                            parameters_display = "NA"
                        step_in_workflow = [step_names[i]]
                        ui.label(step_names[i])
                        ui.markdown(
                            f"""
                            - Ports: {ports_display}
                            - Paramters: {parameters_display}
                        """
                        )
                        ui.button(
                            "View component details",
                            on_click=lambda: view_component_details(
                                step.get("component_version")
                            ),
                            icon="info",
                        )
    except Exception as e:
        ui.notify(
            f"Execution details could not be loaded. An Exception occured: {e}",
            type="negative",
        )


@ui.refreshable
def ui_workarea(current_digital_twin, current_user):
    ui.markdown(
        """
        ### Work Area
        """
    )
    current_execution = storage.get_active_object_from_storage(
        storage.CURRENT_EXECUTION
    )
    if not current_execution:
        ui.markdown(
            f"""
            #### Current Selection
            - **user**: {current_user.get("display_name")}
            - **digital twin**: {current_digital_twin.get("name")}

            ##### Actions
            - add execution
            - select execution 
            """
        )
        return
    step_names = current_execution.get("step_names")
    ui.markdown(
        f"""
        #### Current Selection
        - **user**: {current_user.get("display_name")}
        - **digital twin**: {current_digital_twin.get("name")}
        - **current execution** {current_execution.get("title")}
        """
    )
    ui.mermaid(
        f"""
        graph TD;
            {helpers.get_workflow_mairmaid(step_names)};
        """
    )
    ui.button(
        "Prepare and Run Executions",
        on_click=lambda: ui.open(ui_theme.PATH_RUN),
        icon="link",
    )
    ui.markdown(
        f"""
        ##### Actions
        - add executions
        - select executions 
        """
    )


def store_selected_execution(value):
    try:
        storage.reset_storage_keep(
            [
                storage.CURRENT_USER,
                storage.CURRENT_DIGITAL_TWIN,
            ]
        )
        storage.storage_update_execution(execution_id=value)
    except Exception as e:
        ui.notify(
            f"Selected execution could not be stored. An Exception occured: {e}",
            type="negative",
        )
    else:
        ui_execution_details.refresh()
        ui_workarea.refresh()


def view_component_details(version_id):
    version = db.get_document_by_id(
        document_id=version_id, collection=db.collection_versions
    )
    component_id = str(version["component"]["componentId"])
    storage.storage_update_component(component_id=component_id)
    ui.open(ui_theme.PATH_COMPONENTS)


def cancel_execution_entry():
    storage.reset_storage_delete([storage.NEW_EXECUTION])
    ui_add_execution.refresh()


def cancel_execution_selection():
    storage.reset_storage_delete([storage.CURRENT_EXECUTION])
    ui_execution_details.refresh()
    ui_execution_select.refresh()
