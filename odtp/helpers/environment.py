import os
import shutil
import logging

import odtp.helpers.utils as utils
import odtp.helpers.utils as odtp_utils
import odtp.mongodb.db as db


class OdtpLocalEnvironmentException(Exception):
    pass


def check_project_folder_empty(project_folder):
    if not project_folder_is_empty(project_folder):
        raise OdtpLocalEnvironmentException(
            f"project folder {project_folder} was not empty"
        )


def check_directory_folder_matches_execution(execution_id, project_folder):
    if not directory_folder_matches_execution(execution_id, project_folder):
        raise OdtpLocalEnvironmentException(
            f"""project folder {project_folder} does not match execution. 
            First run 'prepare' on an empty folder to prepare for the run of the execution"""
        )


def project_folder_is_empty(project_folder):
    empty_directory = os.path.isdir(project_folder) and not os.listdir(project_folder)
    if not empty_directory:
        return False
    return True


def directory_folder_matches_execution(execution_id, project_folder):
    if not os.path.isdir(project_folder):
        return False
    subdirs = os.listdir(project_folder)
    execution = db.get_document_by_id(
        document_id=execution_id, collection=db.collection_executions
    )
    step_names = odtp_utils.get_version_names_for_execution(execution)
    expected_dir_names = [f"{i}_{step}" for i, step in enumerate(step_names)]
    if set(subdirs) != set(expected_dir_names):
        return False
    return True


def directory_has_output(execution_id, project_folder):
    if not directory_folder_matches_execution(execution_id, project_folder):
        return False
    subdirs = os.listdir(project_folder)
    output_dirs = [
        os.path.join(project_folder, subdir, "odtp-output") for subdir in subdirs
    ]
    for output_dir in output_dirs:
        if len(os.listdir(output_dir)) != 0:
            return True
    return False

def delete_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    logging.info("Folder deleted: %s", folder_path)