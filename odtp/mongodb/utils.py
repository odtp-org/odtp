import json
import re

PORT_PATTERN = "\d{2,4}"
PORT_MAPPING_PATTERN = f"{PORT_PATTERN}:{PORT_PATTERN}"
COMPONENT_TYPE_PERSISTENT = "persistent"
COMPONENT_TYPE_EPHERMAL = "ephemeral"


class OdtpDbMongoDBValidationException(Exception):
    pass


def get_list_from_cursor(cursor):
    document_list = []
    for document in cursor:
        document_list.append(document)
    return document_list


def check_port_mappings_for_execution(ports):
    if not ports:
        return True
    if not isinstance(ports, list):
        raise OdtpDbMongoDBValidationException(f"ports '{ports}' are not a list")
    for list_of_ports in ports:
        check_port_mappings_for_component_runs(ports=list_of_ports)


def check_port_mappings_for_component_runs(ports):
    if not ports:
        return True
    if not isinstance(ports, list):
        raise OdtpDbMongoDBValidationException(
            f"some component ports '{ports}' are not a list"
        )
    for port in ports:
        print(f"=========== {port} {type(port)}")
        if not re.match(PORT_MAPPING_PATTERN, port):
            raise OdtpDbMongoDBValidationException(
                f"'{port}' is not a valid port mapping"
            )


def check_parameters_for_execution(parameters):
    if not isinstance(parameters, list):
        raise OdtpDbMongoDBValidationException(f"{parameters} should be a list")
    for parameters_per_version in parameters:
        check_parameters_for_component(parameters_per_version)


def check_parameters_for_component(parameters):
    try:
        json.dumps(parameters)
    except Exception as e:
        raise OdtpDbMongoDBValidationException(f"{parameters} be convertible to json")


def check_component_type(type):
    if not type in [COMPONENT_TYPE_PERSISTENT, COMPONENT_TYPE_EPHERMAL]:
        raise OdtpDbMongoDBValidationException(
            f"{type} should be either {COMPONENT_TYPE_EPHERMAL} or {COMPONENT_TYPE_PERSISTENT}"
        )


def check_component_ports(ports):
    if not ports:
        return True
    if not isinstance(ports, list):
        raise OdtpDbMongoDBValidationException(
            f"component ports '{ports}' are not a list"
        )
    for port in ports:
        if not re.match(PORT_PATTERN, port):
            raise OdtpDbMongoDBValidationException(f"'{port}' is not a valid port")
