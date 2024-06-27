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


def get_execution_step_name(component_name, component_version, step_index):
    component_version_name = get_component_version_name(component_name, component_version)
    return f"{step_index}_{component_version_name}"


def get_component_version_name(component_name, component_version, delimiter="_"):
    return f"{component_name}{delimiter}{component_version}"


def get_version_name_dict_for_version_ids(version_ids, delimiter):
    versions = db.get_document_by_ids_in_collection(
        collection=db.collection_versions, document_ids=version_ids
    )
    versions_dict = {}
    for version in versions:
        version_display_name = get_component_version_name(
            component_name=version["component"]["componentName"],
            component_version=version["component_version"],
            delimiter=delimiter
        )
        versions_dict[str(version["_id"])] = version_display_name
    return versions_dict


def get_version_names_for_execution(version_ids):
    version_dict = get_version_name_dict_for_version_ids(version_ids, delimiter=":")
    version_names = [version_dict[version_id] for version_id in version_ids]
    return version_names


def get_folder_names_for_execution(version_ids):
    version_dict = get_version_name_dict_for_version_ids(version_ids, delimiter="_")
    folder_names = [f"{i}_{version_dict[version_id]}" for i, version_id in enumerate(version_ids)]
    return folder_names   


def get_image_names_for_execution(version_ids):
    version_dict = get_version_name_dict_for_version_ids(version_ids, delimiter="_")
    image_names = [f"{i}_{version_dict[version_id]}" for i, version_id in enumerate(version_ids)]
    return image_names

