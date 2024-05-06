import odtp.mongodb.db as db


def get_workflow_mermaid(step_names, init="graph TB;"):
    mermaid_graph = init
    step_count = len(step_names)
    if step_count == 1:
        mermaid_graph += f"{step_names[0]};"
    elif step_count > 1:    
        step_name_tuples = [
            (step_names[i - 1], step_names[i]) for i in range(step_count) if i > 0
        ]
        for i, step_tuple in enumerate(step_name_tuples):
            mermaid_graph += f"C{i}[{step_tuple[0]}] --> C{i+1}[{step_tuple[1]}];"
    return mermaid_graph


def pd_lists_to_counts(items_list):
    if not items_list:
        return 0
    return len([str(item) for item in items_list])


def component_version_for_table(version):
    component = version.get("component")
    version_cleaned = {
        "component": component.get("componentName"),
        "version": version.get("component_version"),        
        "repository": component.get("repoLink"),
        "commit": version.get("commitHash")[:8],
        "type": component.get("type"),
    }
    return version_cleaned


def get_execution_step_display_name(
    component_name, 
    component_version, 
):
    display_name = f"{component_name}:{component_version}"
    return display_name    


def get_key_from_parameters(current_component_parameters, index):
    if index >= len(current_component_parameters):
        return ""
    parameters_keys_as_list = list(current_component_parameters.keys())  
    return parameters_keys_as_list[index]


def get_value_from_parameters(current_component_parameters, index):
    if index >= len(current_component_parameters):
        return ""    
    parameters_values_as_list = list(current_component_parameters.values())
    return parameters_values_as_list[index]           


def get_execution_select_options(digital_twin_id):
    executions = db.get_sub_collection_items(
        collection=db.collection_digital_twins,
        sub_collection=db.collection_executions,
        item_id=digital_twin_id,
        ref_name=db.collection_executions,
        sort_by=[("start_timestamp", db.DESCENDING)]
    )        
    if not executions:
        return {}
    execution_options = {}
    for execution in executions:
        execution_options[
            str(execution["_id"])
        ] = f"{execution['start_timestamp'].strftime('%d/%m/%y')} {execution.get('title')}"
    return execution_options
