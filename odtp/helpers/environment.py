import os
import shutil
import logging
from slugify import slugify
import odtp.helpers.utils as odtp_utils
import odtp.mongodb.db as db

log = logging.getLogger(__name__)

class OdtpLocalEnvironmentException(Exception):
    pass


def check_project_folder_empty(project_folder):
    if not os.path.exists(project_folder):
        raise OdtpLocalEnvironmentException(
            f"project folder {project_folder} does not exist. Please create it first."
        )
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


def project_folder_exists_file_or_not_empty(project_folder):
    if os.path.exists(project_folder):
        if project_folder_is_empty(project_folder):
            return True
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
    if not output_dirs:
        return False
    for output_dir in output_dirs:
        if len(os.listdir(output_dir)) != 0:
            return True
    return False

def delete_folder(folder_path, keep_project_path=True):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    if keep_project_path:
        os.mkdir(folder_path)

    log.info("Folder deleted: %s", folder_path)


def make_project_dir_for_execution(user_workdir, digital_twin_name, execution_title):
    digital_twin_slug = slugify(digital_twin_name)
    print(digital_twin_slug)
    execution_slug = slugify(execution_title)
    print(execution_slug)
    project_dir = os.path.join(user_workdir, digital_twin_slug, execution_slug)
    print(project_dir)
    print("now create")
    make_project_dir(project_dir)
    return project_dir


def make_project_dir(project_dir):
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    os.makedirs(project_dir)
