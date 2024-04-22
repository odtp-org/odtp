def get_workflow_mairmaid(step_names):
    if len(step_names) == 1:
        return step_names[0]
    step_name_tuples = [
        (step_names[i - 1], step_names[i]) for i in range(len(step_names)) if i > 0
    ]
    workflow_in_mermaid = ""
    for step_tuple in step_name_tuples:
        workflow_in_mermaid += f"{step_tuple[0]} --> {step_tuple[1]};"
    return workflow_in_mermaid


def pd_lists_to_counts(items_list):
    if not items_list:
        return 0
    return len([str(item) for item in items_list])


def component_version_for_table(version):
    component = version.get("component")
    version_cleaned = {
        "component": component.get("componentName"),
        "repository": component.get("repoLink"),
        "type": component.get("type"),
        "version": version.get("component_version"),
        "commit": version.get("commitHash")[:8]
    }
    return version_cleaned
