import re
import os
from nicegui import ui
import odtp.helpers.git as otdp_git
import odtp.mongodb.utils as db_utils
import odtp.mongodb.db as db


def validate_port_input(value):
    if not value:
        return True
    try:
        if re.match(db_utils.PORT_PATTERN, value):
            return True
    except Exception as e:
        return False


def validate_required_input(value):
    if not value:
        return False
    return True


def validate_integer_input_below_threshold(value, lower_bound, upper_bound):
    if not int(value) == value:
        return False
    if not lower_bound <= value <= upper_bound:
        return False    
    return True        


def validate_github_url(value):
    try:
        repo_info = otdp_git.get_github_repo_info(value)
        if not repo_info.get("tagged_versions"):
            raise otdp_git.OdtpGithubException(f"Repo {value} has no version tags")
        repo_url =  repo_info.get("html_url")    
        component = db.get_document_id_by_field_value("repoLink", repo_url, db.collection_components)    
        if component:
            raise otdp_git.OdtpGithubException(f"Component with {value} already exists") 
    except Exception as e:
        raise otdp_git.OdtpGithubException(e) 


def validate_ports_mapping_input(value):
    if not value:
        return True
    try:
        if re.match(db_utils.PORT_MAPPING_PATTERN, value):
            return True
    except Exception as e:
        return False


def validate_folder_does_not_exist(value, workdir):
    project_path = os.path.join(workdir, value)
    if os.path.exists(project_path):
        return False
    return True
    