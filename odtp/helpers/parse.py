import json
import os

from dotenv import dotenv_values

import odtp.mongodb.db as db

class OdtpParameterParsingException(Exception):
    pass


def parse_parameters_for_one_file(parameter_file):
    if not parameter_file:
        return {}
    if not os.path.isfile(parameter_file):
        raise OdtpParameterParsingException(
            f"Parsing of file {parameter_file} failed: file path not valid"
        )
    try:
        parameters = dotenv_values(parameter_file)
        json.dumps(parameters)
    except Exception as e:
        raise OdtpParameterParsingException(f"Parsing of file {parameter_file} failed")
    else:
        return parameters


def parse_parameters_for_multiple_files(parameter_files, step_count):
    if not parameter_files:
        return [None for i in range(step_count)]
    try:
        parameters_output = []
        parameters_per_step = parameter_files.split(",")
        for parameter_file in parameters_per_step:
            parameters = parse_parameters_for_one_file(parameter_file)
            parameters_output.append(parameters)
        if not len(parameters_output) == step_count:
            raise OdtpParameterParsingException(
                "Invalid ports specification: not as many ports definition  as steps: {ports}"
            )
    except Exception as e:
        raise OdtpParameterParsingException(f"Parsing of file {parameter_file} failed")
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
            raise OdtpParameterParsingException(
                "Invalid ports specification: not as many ports definition  as steps: {ports}"
            )
    except Exception as e:
        raise OdtpParameterParsingException(f"Parsing of ports {ports} failed")
    else:
        return ports_output


def parse_port_mappings_for_one_component(ports):
    if not ports:
        return None
    try:
        ports = ports.split("+")
    except Exception as e:
        raise OdtpParameterParsingException(f"Parsing of ports {ports} failed")
    else:
        return ports


def parse_component_ports(ports):
    if not ports:
        return None
    try:
        ports = ports.split(",")
    except Exception as e:
        raise OdtpParameterParsingException(f"Parsing of ports {ports} failed")
    else:
        return ports


def parse_versions(component_versions):
    return component_versions.split(",")

def parse_component_tags(component_tags):
    version_ids = []
    steps_components_tags = component_tags.split(",")
    for step_components_tag in steps_components_tags:
        component_name = step_components_tag.split(":")[0]
        component_version = step_components_tag.split(":")[1]
        version_documents = db.get_component_version(
            component_name=component_name,
            version_tag=component_version,
        )
        if len(version_documents) > 1:
            raise OdtpParameterParsingException(
                f"Found more than one component version for {component_version}"
            )
        elif len(version_documents) == 0:
            raise OdtpParameterParsingException(
                f"Component version {component_version} not found"
            )
        version_id = str(version_documents[0]["_id"])
        version_ids.append(version_id)
    return version_ids


def parse_run_flags(run_flags_param, step_count):
    run_flags = ",".split(run_flags_param)
    wrong_flag = [flag for flag in run_flags if flag not in ["T", "F"]]
    wrong_flag_count = len(run_flags) != step_count
    if wrong_flag or wrong_flag_count:
        raise OdtpParameterParsingException(
            f"Run flags {run_flags_param} must be a comma separated list of 'T' and 'F' for all steps"
        )
    return run_flags
