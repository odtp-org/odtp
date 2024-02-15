import json
from odtp import __version__


def get_odtp_version():
    return(__version__)


def output_as_json(db_output):
    return json.dumps(db_output, indent=2, default=str)


def print_output_as_json(db_output):
    print(output_as_json(db_output))


def get_workflow(versions):
    return(list(range(len(versions))))

def get_execution_step_name(component_name, component_version, step_index=None):
    if not step_index:
        return f"{component_name}_{component_version}"
    return f"{component_name}_{component_version}_{step_index}"
