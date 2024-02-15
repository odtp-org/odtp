import os


class OdtpLocalEnvironmentException(Exception):
    pass


def check_project_folder_empty(project_folder):    
    """check whether the project folder is an empty folder"""
    empty_directory = os.path.isdir(project_folder) and not os.listdir(project_folder)
    if not empty_directory:
        raise OdtpLocalEnvironmentException(f"project folder {project_folder} was not empty")
