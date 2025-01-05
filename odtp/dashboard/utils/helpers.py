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


def get_execution_step_display_name(
    component_name,
    component_version,
):
    display_name = f"{component_name}:{component_version}"
    return display_name
