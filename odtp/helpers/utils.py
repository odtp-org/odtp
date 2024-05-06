import json

import odtp.mongodb.db as db
from odtp import __version__


def get_odtp_version():
    return __version__


def output_as_json(db_output):
    return json.dumps(db_output, indent=2, default=str)


def print_output_as_json(db_output):
    print(output_as_json(db_output))


def get_workflow(versions):
    return list(range(len(versions)))


def get_execution_step_name(component_name, component_version, step_index=None):
    if step_index is None:
        return f"{component_name}_{component_version}"
    return f"{step_index}_{component_name}_{component_version}"


def get_version_name_dict_for_version_ids(version_ids, naming_function=get_execution_step_name):
    versions = db.get_document_by_ids_in_collection(
        collection=db.collection_versions, document_ids=version_ids
    )
    versions_dict = {}
    for version in versions:
        version_display_name = naming_function(
            component_name=version["component"]["componentName"],
            component_version=version["component_version"],
        )
        versions_dict[str(version["_id"])] = version_display_name
    return versions_dict


def get_version_names_for_execution(execution, naming_function=get_execution_step_name):
    version_ids = execution["workflowSchema"]["component_versions"]
    version_dict = get_version_name_dict_for_version_ids(version_ids, naming_function=naming_function)
    version_names = [version_dict[version_id] for version_id in version_ids]
    return version_names
