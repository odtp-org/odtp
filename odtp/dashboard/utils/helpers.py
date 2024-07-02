import odtp.helpers.utils as odtp_utils
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
        sort_by=[("createdAt", db.DESCENDING)],
    )
    if not executions:
        return {}
    execution_options = {}
    for execution in executions:
        execution_options[str(execution["_id"])] = (
            f"{execution['createdAt'].strftime('%d/%m/%y')} {execution.get('title')}"
        )
    return execution_options


def build_execution_with_steps(execution_id):
    execution = db.get_document_by_id(
        document_id=execution_id, collection=db.collection_executions
    )
    version_tags = odtp_utils.get_version_names_for_execution(
        execution=execution,
        naming_function=get_execution_step_display_name,
    )
    step_ids = [str(step_id) for step_id in execution["steps"]]
    step_documents = db.get_document_by_ids_in_collection(
        document_ids=step_ids, collection=db.collection_steps
    )
    step_dict = {}
    for step_document in step_documents:
        step_dict[str(step_document["_id"])] = step_document
    ports = []
    parameters = []
    outputs = []
    inputs = []
    for step_id in step_ids:
        parameters.append(step_dict[step_id].get("parameters", {}))
        ports.append(step_dict[step_id].get("ports", []))
        output = step_dict[step_id].get("output")
        if output:
            outputs.append(str(output))
        inputs.append(step_dict[step_id].get("input", {}))
    execution_with_steps = {
        "execution_id": execution_id,
        "title": execution.get("title"),
        "createdAt": execution.get("createdAt").strftime("%m/%d/%Y, %H:%M:%S"),
        "versions": execution["workflowSchema"]["component_versions"],
        "version_tags": version_tags,
        "steps": step_ids,
        "ports": ports,
        "parameters": parameters,
        "outputs": outputs,
        "inputs": inputs,
    }
    return execution_with_steps
