import json
import os

from dotenv import dotenv_values

import odtp.mongodb.db as db

class OdtpParamterParsingException(Exception):
    pass


def parse_paramters_for_one_file(parameter_file):
    if not parameter_file:
        return {}
    if not os.path.isfile(parameter_file):
        raise OdtpParamterParsingException(
            f"Parsing of file {parameter_file} failed: file path not valid"
        )
    try:
        parameters = dotenv_values(parameter_file)
        json.dumps(parameters)
    except Exception as e:
        raise OdtpParamterParsingException(f"Parsing of file {parameter_file} failed")
    else:
        return parameters


def parse_paramters_for_multiple_files(parameter_files, step_count):
    if not parameter_files:
        return [None for i in range(step_count)]
    try:
        parameters_output = []
        parameters_per_step = parameter_files.split(",")
        for parameter_file in parameters_per_step:
            parameters = parse_paramters_for_one_file(parameter_file)
            parameters_output.append(parameters)
        if not len(parameters_output) == step_count:
            raise OdtpParamterParsingException(
                "Invalid ports specification: not as many ports definition  as steps: {ports}"
            )
    except Exception as e:
        raise OdtpParamterParsingException(f"Parsing of file {parameter_file} failed")
    else:
        return parameters_output


def parse_port_mappings_for_multiple_components(ports, step_count):
    if not ports:
        return [None for i in range(step_count)]
    try:
        ports_output = []
        ports_per_step = ports.split(",")
        for ports in ports_per_step:
            ports_output.append(parse_port_mappings_for_one_component(ports))
        if not len(ports_output) == step_count:
            raise OdtpParamterParsingException(
                "Invalid ports specification: not as many ports definition  as steps: {ports}"
            )
    except Exception as e:
        raise OdtpParamterParsingException(f"Parsing of ports {ports} failed")
    else:
        return ports_output


def parse_port_mappings_for_one_component(ports):
    if not ports:
        return None
    try:
        ports = ports.split("+")
    except Exception as e:
        raise OdtpParamterParsingException(f"Parsing of ports {ports} failed")
    else:
        return ports


def parse_component_ports(ports):
    if not ports:
        return None
    try:
        ports = ports.split(",")
    except Exception as e:
        raise OdtpParamterParsingException(f"Parsing of ports {ports} failed")
    else:
        return ports


def parse_versions(component_versions):
    return component_versions.split(",")

def parse_component_tags(component_tags):
    steps_components_tags = component_tags.split(",")

    versions_ids = []
    for step_components_tag in steps_components_tags:
        component_name = step_components_tag.split(":")[0]
        component_version = step_components_tag.split(":")[1]

        component_id = db.get_document_id_by_field_value("componentName", component_name, "components")
        component_doc = db.get_document_by_id(component_id,"components")
        for version in component_doc["versions"]:
            version_doc = db.get_document_by_id(version, "versions")
            if version_doc["component_version"] == component_version:
                versions_ids.append(str(version_doc["_id"]))
            else:
                versions_ids.append(None)

    print(versions_ids)
    return versions_ids

