from nicegui import ui, app
import pandas as pd
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.format as format
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db


def content() -> None:
    current_digital_twin = storage.get_active_object_from_storage("digital_twin")
    with ui.right_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as right_drawer:
        ui_workarea(current_digital_twin)
    if current_digital_twin:
        ui.markdown("""
                    # Manage Executions
                    """)
        with ui.tabs().classes('w-full') as tabs:
            select = ui.tab('Select an execution')
            add = ui.tab('Add an execution')
        with ui.tab_panels(tabs, value=select).classes('w-full'):
            with ui.tab_panel(select):
                ui_execution_select(current_digital_twin)
                ui_executions_table(current_digital_twin)
            with ui.tab_panel(add):
                ui_add_execution(current_digital_twin)


@ui.refreshable
def ui_executions_table(current_digital_twin):
    try:
        executions = db.get_sub_collection_items(
            collection=db.collection_digital_twins,
            sub_collection=db.collection_executions,
            item_id=current_digital_twin["digital_twin_id"],
            ref_name=db.collection_executions
        )
        if executions:
            df = pd.DataFrame(data=executions)
            df["_id"] = df["_id"].astype("string")
            df["_id"] = df["_id"].astype("string")
            df["steps"] = df["steps"].apply(format.pd_lists_to_counts).astype("string")
            df = df[["_id", "title", "steps", "start_timestamp", "end_timestamp"]]
            ui.table.from_pandas(df)
        else:
            ui.label("You don't have executions yet. Start adding one.")
    except Exception as e:
        ui.notify(f"Execution table could not be loaded. An Exception occured: {e}", 
                  type="negative")         


@ui.refreshable
def ui_execution_select(current_digital_twin) -> None:
    try:
        ui.markdown("""
            #### Select digital twin
            Here you can select a digital twin to work with:
            """)
        digital_twin_id = current_digital_twin["digital_twin_id"]
        executions = db.get_sub_collection_items(
            collection=db.collection_digital_twins,
            sub_collection=db.collection_executions,
            item_id=digital_twin_id,
            ref_name=db.collection_executions
        )
        execution_options = {
            str(execution["_id"]): f"{execution.get('title')}: {len(execution['workflowSchema']['components'])} steps"
            for execution in executions
        }
        if execution_options:
            ui.select(
                execution_options,
                label="executions",
                on_change=lambda e: store_selected_execution_id(str(e.value)),
                with_input=True,
            ).props("size=80")
    except Exception as e:
        ui.notify(f"Execution selection could not be loaded. An Exception occured: {e}", 
                  type="negative")             


@ui.refreshable
def ui_add_execution(current_digital_twin):
    components = storage.get_active_object_from_storage("components") 
    if components:
        ui.markdown("""
            #### Add an execution
            """)
        with ui.column():
            try:
                name_input = ui.input(label='Name', placeholder='name',
                                        validation={'Can not be empty': lambda value: len(value.strip()) != 0})\
                                        .props("size=300")
                components = storage.get_active_object_from_storage("components")  

                components_options = {
                    (component["component_id"], component["version"]["version_id"], i): component["name"]
                    for i, component in enumerate(components)}
                components_input = ui.select(
                    components_options,
                    multiple=True, value=components, label='components',
                    with_input=True,
                ).classes('w-full').props("use-chips")
                ui.button('Add new execution',
                            on_click=lambda: add_execution(
                                name=name_input.value,
                                components=components_input.value,
                                digital_twin_id=current_digital_twin["digital_twin_id"]
                            )
                    )
            except Exception as e:
                ui.notify(f"Component selection could not be loaded. An Exception occured: {e}", 
                        type="negative")         


@ui.refreshable
def ui_workarea(current_digital_twin):
    ui.markdown("""
            ### Work Area
            """)
    if not current_digital_twin:
        ui.button("Select a digital twin", 
            on_click=lambda: ui.open(ui_theme.PATH_DIGITAL_TWINS))
    else:
        digital_twin = storage.get_active_object_from_storage("digital_twin")
        current_user = storage.get_active_object_from_storage("user")
        ui.markdown("""
                    #### User / Digital Twin
                    """)
        ui.label(f"{current_user.get('display_name')} / {current_digital_twin.get('name')}")
        components = storage.get_active_object_from_storage("components")
        if storage.app_storage_is_set("components"):
            ui.markdown("""
                #### Component Versions
                these can be used for the steps of the digital twin        
                """)
            for component in components:
                version = component.get("version")
                if component and version:
                    component_version_output = f"""
                        **{component.get('name')}**:  
                        {version.get('odtp_version')} {version.get('component_version')} 
                        """
                    ui.markdown(component_version_output)
            ui.button("Change components", 
                        on_click=lambda: ui.open(ui_theme.PATH_COMPONENTS))        
        else:
            ui.button("Select components", 
                      on_click=lambda: ui.open(ui_theme.PATH_COMPONENTS))   
        current_execution = storage.get_active_object_from_storage("execution")    
        if current_execution:
            print(current_execution)
            ui.markdown("""
                        #### Execution       
                        """)
            ui.label(current_execution.get("title"))  
            ui.button('Reset work area', on_click=lambda: app_storage_reset())                           
         

def store_selected_execution_id(value):
    try:
        storage.storage_update_execution(execution_id=value)
    except Exception as e:
        ui.notify(f"Selected execution could not be stored. An Exception occured: {e}", 
                  type="negative")
    finally:        
        ui_workarea.refresh()
        ui.ui_execution_select.refresh() 


def add_execution(
    digital_twin_id,
    name,
    components
):
    try:
        if digital_twin_id and name and components:
            component_id_list = [c[0] for c in components]
            version_id_list = [c[1] for c in components]
            workflow = ",".join(list([str(i) for i in range(len(component_id_list))]))
            execution_id = db.add_execution(
                dt_id=digital_twin_id,
                name=name,
                components=",".join(component_id_list),
                versions=",".join(version_id_list),
                workflow=workflow)
            ui.notify(f"A execution with id {execution_id} has been created", type="positive")
    except Exception as e:
        ui.notify(f"Execution could not be added. An exception occured:", type="negative")
    finally:
        ui_executions_table.refresh()
        ui_execution_select.refresh()  
        ui_add_execution.refresh()


def app_storage_reset():
    try:
        storage.app_storage_reset("execution")
    except Exception as e:
        ui.notify(f"Work area could not be reset. An Exception occured: {e}", 
                  type="negative")
    finally:
        ui_workarea.refresh()
