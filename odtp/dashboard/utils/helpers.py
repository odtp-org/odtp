import os
from odtp.helpers.settings import ODTP_SECRETS_DIR, ODTP_PASSWORD
import odtp.helpers.secrets as odtp_secrets


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


def get_secrets_files(user_workdir):
    file_names = get_secrets_file_names(user_workdir)
    secrets_path = os.path.join(user_workdir, ODTP_SECRETS_DIR)
    if file_names:
        select_options = {}
        for file_name in file_names:
            file_path = os.path.join(secrets_path, file_name)
            secret_keys = get_secrets_keys(file_path)
            select_options[file_path] = f"{file_name}: {secret_keys}"
        print(select_options)
        return select_options
    return None


def get_secrets_keys(secrets_file):
    decrypted_content = odtp_secrets.decrypt_file_to_dict(
        secrets_file,
        ODTP_PASSWORD
    )
    secret_keys = [str(key) for key in decrypted_content]
    return secret_keys


def get_secrets_file_names(user_workdir):
    secrets_path = os.path.join(user_workdir, ODTP_SECRETS_DIR)
    if os.path.exists(secrets_path) and os.path.isdir(secrets_path):
        file_names = os.listdir(secrets_path)
        return file_names
    return None
