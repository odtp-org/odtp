import subprocess
import logging
import odtp.helpers.environment as odtp_env

log = logging.getLogger("__name__")

FOLDER_NOT_SET = 0
FOLDER_DOES_NOT_MATCH = 1
FOLDER_EMPTY = 2
FOLDER_PREPARED = 3
FOLDER_HAS_OUTPUT = 4


def build_cli_command(cmd, execution_id=None, step_nr=None):
    cli_parameters = []
    if execution_id:
        cli_parameters.append(
            f"--execution-id {execution_id}",
        )
    if step_nr:
        cli_parameters.append(
            f"--step-nr {step_nr}",
        )
    cli_command = f"odtp execution {cmd} {'  '.join(cli_parameters)}"
    return cli_command


def get_folder_status(execution_id, project_path):
    if not project_path:
        return FOLDER_NOT_SET
    folder_empty = odtp_env.project_folder_is_empty(project_folder=project_path)
    folder_matches_execution = odtp_env.directory_folder_matches_execution(
        project_folder=project_path, execution_id=execution_id
    )
    folder_has_output = odtp_env.directory_has_output(
        execution_id=execution_id, project_folder=project_path
    )
    if folder_empty:
        return FOLDER_EMPTY
    elif folder_matches_execution and not folder_has_output:
        return FOLDER_PREPARED
    elif folder_matches_execution and folder_has_output:
        return FOLDER_HAS_OUTPUT
    else:
        return FOLDER_DOES_NOT_MATCH


def check_container_running(container_name):
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        running_containers = result.stdout.strip().split("\n")
        return container_name in running_containers
    except Exception as e:
        log.error(f"Check on Docker container {container_name} failed: {e}")
        return False
