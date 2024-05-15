import re
import os
import odtp.helpers.git as otdp_git
import odtp.mongodb.utils as db_utils
import odtp.mongodb.db as db
import logging 

logger = logging.getLogger(__name__)


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


def validate_github_repo(value):
    try:
        repo_info = otdp_git.get_github_repo_info(value)
        if not repo_info:
            logger.error(f"repo info was not received for {value}")
            return f"repo info was not received for {value}. This is not a valid github repo"
        if not repo_info.get("tagged_versions"):
            logger.error(f"repo {value} has no tagged versions {err}")
            return f"repo {value} has no tagged versions"
        repo_url =  repo_info.get("html_url")
        component = db.get_document_id_by_field_value("repoLink", repo_url, db.collection_components)    
        if component:
            logger.error(f"repo {value} already exists as component in odtp")
            return f"repo {value} already exists as component in odtp"
    except Exception as e:
        logger.exception(f"github repo got an error {e}", exc_info=True)
        return f"github repo got an error {e}"
    return None


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

def validate_name(value):
    if not value:
        return "you need to provide a value"
    elif len(value) < 3:
        return "much too short"
    elif len(value) < 5:
        return "must be at least 5"
    return None
