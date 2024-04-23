import re
import odtp.dashboard.utils.parse as parse
import odtp.helpers.git as otdp_git
import odtp.mongodb.utils as db_utils


def validate_ports_input(value):
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


def validate_github_url(value):
    try:
        repo_info = otdp_git.get_github_repo_info(value)
        if not repo_info.get("tagged_versions"):
            raise otdp_git.OdtpGithubException(f"repo {value} has no versions")
    except Exception as e:
        raise(e)
    return True
