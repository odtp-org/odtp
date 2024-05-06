import pandas as pd
from nicegui import ui, app
import json
from odtp.dashboard.utils.file_picker import local_file_picker
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.validators as validators
import odtp.helpers.utils as odtp_utils
import odtp.helpers.parse as odtp_parse
import odtp.mongodb.db as db


STEPPERS = (
    "Start",
    "Workflow",
    "Confirm", 
    "Ports",
    "Parameters",
    "Save"
)

STEPPER_START_INDEX = 0
STEPPER_WORKFLOW_INDEX = 1
STEPPER_CONFIRM_INDEX = 2
STEPPER_CONFIGURATION_PORTS_INDEX = 3
STEPPER_CONFIGURATION_PARAMETERS_INDEX = 4
STEPPER_SAVE_INDEX = 5



def content() -> None:
    ui.markdown(
        """
        # Manage Executions
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
    if not user_workdir:
        ui_theme.ui_add_first(
            item_name="workdir",
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
            current_user=current_user,
            user_workdir=user_workdir
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
            ui_add_execution(current_digital_twin, user_workdir)
        with ui.tab_panel(table):
            ui_executions_table(current_digital_twin)


def ui_new_execution_start_form(current_digital_twin, current_execution_to_add):    
    if current_execution_to_add:  
        presets = {
            "name": current_execution_to_add.get("name", ""),
            "nr_steps": current_execution_to_add.get("step_count", 0),
            "port_count": current_execution_to_add.get("port_count", 1),
            "parameter_count": current_execution_to_add.get("parameter_count", 6),
        }
    else:
        presets = {
            "name": "",
            "nr_steps": 0,
            "port_count": 1,
            "parameter_count": 6,
        }             
    name_input = ui.input(
        label="Execution title",
        placeholder="Execution title",
        validation={f"Please provide an execution title":
                    lambda value: validators.validate_required_input(value)},
        value=presets["name"],       
    ).classes("text-lg font-bold w-full")
    nr_steps_input = ui.number(
        label='Number of steps', value=presets["nr_steps"], format='%d', min=0, max=10,
        on_change=lambda e: result.set_content(
            helpers.get_workflow_mermaid(
                [f"Step{str(i + 1)}" for i in range(int(e.value))], init='graph LR;'
            )
        ),
        validation={f"Must be an integer <= 10 and >= 0":
                    lambda value: validators.validate_integer_input_below_threshold(
                        value, lower_bound=1, upper_bound=10
                    )},    
    ).classes("w-1/2")
    result = ui.mermaid('graph LR;').classes("w-full")          
 
    ui.label("Maximal Number of Ports per Step").classes("w-1/4")
    max_nr_ports = ui.slider(min=0, max=3, value=presets["port_count"]).classes("w-1/4")
    ui.label().bind_text_from(max_nr_ports, 'value').classes("w-1/4") 

    ui.label("Maximal Number of Parameters per Step").classes("w-1/4")
    max_nr_parameters = ui.slider(min=0, max=10, value=presets["parameter_count"]).classes("w-1/4")
    ui.label().bind_text_from(max_nr_parameters, 'value').classes("w-1/4")
    with ui.row().classes('w-full'):  
        ui.button(
            "Next",
            on_click=lambda: store_new_execution_init(
                name_input=name_input,
                digital_twin=current_digital_twin,
                nr_steps_input=nr_steps_input,
                port_count=max_nr_ports.value,
                parameter_count=max_nr_parameters.value,            
                current_execution_to_add=current_execution_to_add 
            ),
        )


def ui_execution_workflow_template_form(current_execution_to_add):
    if not current_execution_to_add: 
        return  
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_WORKFLOW_INDEX:
        return           
    step_count = current_execution_to_add.get("step_count")
    component_versions = db.get_collection_sorted(
        collection=db.collection_versions,
        sort_tuples=[("component.componentName", db.ASCENDING), ("component_version", db.DESCENDING)]
    )
    if not component_versions:
        ui.label("There are no components yet.")
        return     
    select_options = {}
    for version in component_versions:
        version_display_name = helpers.get_execution_step_display_name(
            component_name=version["component"]["componentName"],
            component_version=version["component_version"],
        )
        select_options[
            (str(version["_id"]), version_display_name)
        ] = f"{version_display_name}"                       
    workflow = []
    presets = ["" for i in range(step_count)]
    current_version_tags = current_execution_to_add.get("version_tags")
    current_versions = current_execution_to_add.get("versions")
    if current_versions:
        for i in range(len(current_versions)):
            if i < step_count:
                presets[i] = (current_versions[i], current_version_tags[i])  
    with ui.row().classes('w-full'):    
        for i in range(step_count):        
            workflow.append(
                ui.select(
                    select_options,
                    label="component versions",
                    validation={f"Please provide an component version":
                    lambda value: validators.validate_required_input(value)},
                    value=presets[i],
                )                
                .classes("w-full font-bold text-lg")
            ) 
    with ui.row().classes('w-full'):                  
        ui.button(
            "Next",
            on_click=lambda: store_new_execution_workflow(
                current_execution_to_add=current_execution_to_add,
                workflow=workflow,
            ),
        ) 
        ui.button(
            "Back",
            on_click=lambda: execution_form_step_back(
                current_execution_to_add=current_execution_to_add,
            ),
        ).props('flat')      


def ui_execution_workflow_confirmation_form(current_execution_to_add):
    if not current_execution_to_add: 
        return    
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_CONFIRM_INDEX:
        return          
    version_tags = current_execution_to_add.get("version_tags")
    if not version_tags:
        return
    with ui.grid(columns=1):
        with ui.row().classes('w-full'):      
            ui.mermaid(
                helpers.get_workflow_mermaid(version_tags, init='graph TB;')
            ) 
        with ui.row().classes('w-full'):      
            ui.button(
                "Next",
                on_click=lambda: confirm_new_execution_workflow(
                    current_execution_to_add=current_execution_to_add,
                ),
            ) 
            ui.button(
                "Back",
                on_click=lambda: execution_form_step_back(
                    current_execution_to_add=current_execution_to_add,
                ),
            ).props('flat') 


def ui_execution_configuration_ports_form(current_execution_to_add):
    if not current_execution_to_add: 
        return
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_CONFIGURATION_PORTS_INDEX:
        return         
    version_tags = current_execution_to_add.get("version_tags")
    if not version_tags:
        return  
    port_count = current_execution_to_add["port_count"]   
    step_count = current_execution_to_add["step_count"]  
    current_version_tags = current_execution_to_add.get("version_tags")
    current_ports = current_execution_to_add.get("ports")
    if not current_ports:
        current_ports = [[] for i in range(step_count)]  
    else:
        current_ports = (current_ports + [[] * (step_count - len(current_ports))])[:step_count]    
    presets = []
    for component_ports in current_ports:
        preset = component_ports + [''] * (port_count - len(component_ports))  
        presets.append(preset)
    all_ports_inputs = []
    for j, version_tag in enumerate(current_version_tags):
        ui.mermaid(
            helpers.get_workflow_mermaid([version_tag])
        ).classes("w-full")  
        add_ports = ui.checkbox('add ports', value=bool(len(current_ports[j])))         
        ports_for_component = []     
        with ui.row().bind_visibility_from(add_ports, 'value'): 
            for i in range(port_count):        
                ports_for_component.append(
                    ui.input(
                        label="port mapping",
                        validation={f"Please provide a valid port mapping":
                        lambda value: validators.validate_ports_mapping_input(value)},
                        value=presets[j][i],
                        placeholder="8001:8001"
                    )                
                    .classes("w-1/8 font-bold text-lg")
                )
        all_ports_inputs.append(ports_for_component)                        
    with ui.row().classes('w-full'):    
        ui.button(
            "Next",
            on_click=lambda: add_ports_configuration_to_workflow(
                current_execution_to_add=current_execution_to_add,
                all_ports_inputs=all_ports_inputs
            ),
        ) 
        ui.button(
            "Back",
            on_click=lambda: execution_form_step_back(
                current_execution_to_add=current_execution_to_add,
            ),
        ).props('flat') 


def ui_execution_configuration_parameters_form(current_execution_to_add, user_workdir):
    if not current_execution_to_add: 
        return     
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_CONFIGURATION_PARAMETERS_INDEX:
        return         
    version_tags = current_execution_to_add.get("version_tags")
    if not version_tags:
        return    
    parameter_count = current_execution_to_add["parameter_count"]    
    step_count = current_execution_to_add["step_count"] 
    current_parameters = current_execution_to_add.get("parameters")
    if not current_parameters:
        current_parameters = [{} for i in range(step_count)]  
    else:
        current_parameters = current_parameters[:step_count]  
        if len(current_parameters) < step_count:
            fill_up =  [{} for i in range(step_count - len(current_parameters))]   
            current_parameters += fill_up           
    current_version_tags = current_execution_to_add.get("version_tags")
    all_parameters = []
    for j, version_tag in enumerate(current_version_tags):
        ui.mermaid(
            helpers.get_workflow_mermaid([version_tag])
        ).classes("w-full")  
        parameters_for_component = []
        keys_for_component = []
        values_for_component = []
        current_component_parameters = current_parameters[j] 
        add_parameters = ui.checkbox('add parameters', value=bool(len(current_component_parameters)))               
        with ui.row().bind_visibility_from(add_parameters, 'value'):
            ui.button(
                f"Pick parameters from file for {version_tag}", 
                on_click=lambda step_index=j: pick_parameter_file(
                    step_index,
                    user_workdir=user_workdir,
                    current_execution_to_add=current_execution_to_add,
                    step_count=step_count,
                ), 
                icon="folder"
            )
            preset_keys = []
            preset_values = []
            for i in range(parameter_count):    
                preset_keys.append(helpers.get_key_from_parameters(current_component_parameters, i))
                preset_values.append(helpers.get_value_from_parameters(current_component_parameters, i))
            for i in range(parameter_count):      
                with ui.row().classes("w-full no-wrap"):
                    with ui.column().classes("w-1/2"):
                        keys_for_component.append(
                            ui.input(
                                "key", 
                                value=preset_keys[i],
                            ).classes("w-full")
                        )
                    with ui.column().classes("w-1/2"):
                        values_for_component.append(
                            ui.input(
                                "value", 
                                value=preset_values[i],
                            ).classes("w-full")
                        )
            parameters_for_component = [
                (keys_for_component[i], values_for_component[i]) for i in range(parameter_count)
            ]                   
        all_parameters.append(parameters_for_component)                           
    with ui.row().classes('w-full'):    
        ui.button(
            "Next",
            on_click=lambda: add_parameters_configuration_to_workflow(
                current_execution_to_add=current_execution_to_add,
                parameters=all_parameters,             
            ),
        ) 
        ui.button(
            "Back",
            on_click=lambda: execution_form_step_back(
                current_execution_to_add=current_execution_to_add,
            ),
        ).props('flat') 


def ui_execution_save_form(current_execution_to_add):
    if not current_execution_to_add: 
        return     
    stepper = current_execution_to_add["stepper"]
    if stepper and STEPPERS.index(stepper) < STEPPER_SAVE_INDEX:
        return 
    execution_title = current_execution_to_add.get('name')
    version_tags = current_execution_to_add.get("version_tags")
    current_ports = current_execution_to_add.get("ports")
    current_parameters = current_execution_to_add.get("parameters")        
    ui_theme.ui_execution_display(
        execution_title=execution_title,
        version_tags=version_tags,
        ports=current_ports,
        parameters=current_parameters,
    )                
    with ui.row().classes('w-full'):    
        ui.button(
            "Save",
            on_click=lambda: save_new_execution(
                current_execution_to_add=current_execution_to_add,
            ),
        ) 
        ui.button(
            "Back",
            on_click=lambda: execution_form_step_back(
                current_execution_to_add=current_execution_to_add,
            ),
        ).props('flat') 


@ui.refreshable
def ui_add_execution(current_digital_twin, user_workdir):
    ui.button(
        "Cancel Execution Entry",
        on_click=lambda: cancel_execution_entry(),
        icon="cancel",
    )    
    ui.markdown(
        """
        #### Add Execution
        """
    )
    current_execution_to_add = storage.get_active_object_from_storage(
        storage.NEW_EXECUTION
    )
    if current_execution_to_add:
        ui.label(f"Digital Twin: {current_execution_to_add.get('digital_twin_name')}").classes("text-lg w-full")         
        stepper = current_execution_to_add.get("stepper")
    else:
        stepper = STEPPERS[STEPPER_START_INDEX]   
    with ui.stepper(value=stepper).props('vertical').classes('w-full') as stepper:
        with ui.step(STEPPERS[STEPPER_START_INDEX]):
            with ui.stepper_navigation():
                ui_new_execution_start_form(current_digital_twin, current_execution_to_add)             
        with ui.step(STEPPERS[STEPPER_WORKFLOW_INDEX]):
            with ui.stepper_navigation():
                ui_execution_workflow_template_form(current_execution_to_add)
        with ui.step(STEPPERS[STEPPER_CONFIRM_INDEX]):
            with ui.stepper_navigation():
                ui_execution_workflow_confirmation_form(current_execution_to_add)      
        with ui.step(STEPPERS[STEPPER_CONFIGURATION_PORTS_INDEX]):
            with ui.stepper_navigation():
                ui_execution_configuration_ports_form(current_execution_to_add)                  
        with ui.step(STEPPERS[STEPPER_CONFIGURATION_PARAMETERS_INDEX]):
            with ui.stepper_navigation():
                ui_execution_configuration_parameters_form(current_execution_to_add, user_workdir) 
        with ui.step(STEPPERS[STEPPER_SAVE_INDEX]):
            with ui.stepper_navigation():
                ui_execution_save_form(current_execution_to_add)
    return


def store_new_execution_init(
    name_input, digital_twin, parameter_count, nr_steps_input, port_count, current_execution_to_add
):
    if not name_input.validate() or not nr_steps_input.validate():
        ui.notify("Please fill in the form as required", type="negative")
        return
    if not current_execution_to_add:
        current_execution_to_add = {
            "digital_twin_id": digital_twin["digital_twin_id"], 
            "digital_twin_name": digital_twin["name"], 
        }
    current_execution_to_add["name"] = name_input.value
    current_execution_to_add["step_count"] = int(nr_steps_input.value)
    current_execution_to_add["parameter_count"] = parameter_count
    current_execution_to_add["port_count"] = port_count
    current_execution_to_add["stepper"] = STEPPERS[STEPPER_WORKFLOW_INDEX]
    app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)  
    ui_add_execution.refresh()


def store_new_execution_workflow(current_execution_to_add, workflow):
    if False in [item.validate() for item in workflow]:
        ui.notify("You must provide all steps for the execution", type="negative")
        return
    workflow=[item.value for item in workflow] 
    current_execution_to_add["versions"] = [item[0] for item in workflow]
    current_execution_to_add["version_tags"] = [item[1] for item in workflow] 
    current_execution_to_add["stepper"] = STEPPERS[STEPPER_CONFIRM_INDEX]
    app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)  
    ui_add_execution.refresh() 


def cancel_execution_entry():
    storage.reset_storage_delete([storage.NEW_EXECUTION])
    ui_add_execution.refresh()


def execution_form_step_back(current_execution_to_add):
    next_stepper = None
    current_stepper = current_execution_to_add["stepper"]
    current_stepper_index = STEPPERS.index(current_stepper)
    next_stepper_index = current_stepper_index - 1
    next_stepper = STEPPERS[next_stepper_index]       
    current_execution_to_add["stepper"] = next_stepper
    app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    ui_add_execution.refresh()


def confirm_new_execution_workflow(current_execution_to_add):
    current_execution_to_add["stepper"] = STEPPERS[STEPPER_CONFIGURATION_PORTS_INDEX]
    app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    ui_add_execution.refresh() 


def add_ports_configuration_to_workflow(current_execution_to_add, all_ports_inputs): 
    all_port_mappings = []
    for component_port_inputs in all_ports_inputs:
        component_port_mappings = [
            port_mapping_input.value for port_mapping_input in component_port_inputs
            if port_mapping_input.value
        ]
        all_port_mappings.append(component_port_mappings) 
    current_execution_to_add["ports"] = all_port_mappings
    current_execution_to_add["stepper"] = STEPPERS[STEPPER_CONFIGURATION_PARAMETERS_INDEX]
    app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    ui_add_execution.refresh()     


def add_parameters_configuration_to_workflow(
    current_execution_to_add, parameters, 
):
    parameters_all_steps = []
    for step_parameters in parameters:
        parameters_for_step = {}
        for parameter_key, parameter_value in step_parameters:
            if parameter_key.value:
                parameters_for_step[parameter_key.value] = parameter_value.value
        parameters_all_steps.append(parameters_for_step)    
    current_execution_to_add["parameters"] = parameters_all_steps 
    current_execution_to_add["stepper"] = STEPPERS[STEPPER_SAVE_INDEX]
    app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    ui_add_execution.refresh() 


async def pick_parameter_file(step_index, user_workdir, current_execution_to_add, step_count) -> None:
    root = user_workdir
    result = await local_file_picker(root, multiple=False)
    if result:
        file_path = result[0]
        parameters = dict(odtp_parse.parse_parameters_for_one_file(file_path))
        if len(parameters) > current_execution_to_add["parameter_count"]:
            current_execution_to_add["parameter_count"] = len(parameters)
        if current_execution_to_add.get("parameters"):
            current_execution_to_add["parameters"][step_index] = parameters
        else:
            current_execution_to_add["parameters"] = [{} for i in range(step_count)]
            current_execution_to_add["parameters"][step_index] = parameters   
        app.storage.user[storage.NEW_EXECUTION] = json.dumps(current_execution_to_add)
    ui_add_execution.refresh()     


def save_new_execution(current_execution_to_add):  
    try:       
        execution_id, step_ids = db.add_execution(
            dt_id=current_execution_to_add["digital_twin_id"],
            name=current_execution_to_add["name"],
            versions=current_execution_to_add["versions"],
            parameters=current_execution_to_add["parameters"],
            ports=current_execution_to_add["ports"],
        )
        execution_id_display = str(execution_id)
        step_ids_display = ",".join([str(step_id) for step_id in step_ids])
        ui.notify(
            f"An execution with id {execution_id_display} and steps: {step_ids_display} has been created",
            type="positive",
        )         
    except Exception as e:
        ui.notify(
            f"Execution could not be added. An exception happened: {e}", type="negative"
        )
    else:
        storage.reset_storage_delete([storage.NEW_EXECUTION])
        ui_add_execution.refresh()
        ui_executions_table.refresh()
        ui_execution_select.refresh()
        ui_execution_details.refresh()


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
        execution_options = helpers.get_execution_select_options(
            digital_twin_id=digital_twin_id)    
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
        df = df[["timestamp", "title", "steps"]]
        df = df.sort_values(by="timestamp", ascending=False)
        ui.table.from_pandas(df)
    except Exception as e:
        ui.notify(
            f"Execution table could not be loaded. An Exception occured: {e}",
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
        execution_title = current_execution.get('title')
        version_tags = current_execution.get("version_tags")
        current_ports = current_execution.get("ports")
        current_parameters = current_execution.get("parameters")        
        ui_theme.ui_execution_display(
            execution_title=execution_title,
            version_tags=version_tags,
            ports=current_ports,
            parameters=current_parameters,
        )         
    except Exception as e:
        ui.notify(
            f"Execution details could not be loaded. An Exception occurred: {e}",
            type="negative",
        )


@ui.refreshable
def ui_workarea(current_digital_twin, current_user, user_workdir):
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
            - **work directory**: {user_workdir}

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
        storage.store_execution_selection(
            storage.CURRENT_EXECUTION,
            execution_id = value
        )
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


def cancel_execution_selection():
    storage.reset_storage_delete([storage.CURRENT_EXECUTION])
    ui_execution_details.refresh()
    ui_execution_select.refresh()
