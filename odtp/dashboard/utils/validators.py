import odtp.dashboard.utils.parse as parse
import odtp.helpers.git as otdp_git
import odtp.mongodb.utils as db_utils


def validate_ports_input(value):
    try:
        ports = parse.parse_ports(value)
        db_utils.check_component_ports(value)
    except Exception as e:
        return False
    return True


def validate_required_input(value):
    if not value:
        return False
    return True


def validate_github_url(value):
    try:
        otdp_git.check_commit_for_repo(value)
        repo_info = otdp_git.get_github_repo_info(value)
        print(repo_info)
    except Exception as e:
        return False
    return True


def validate_versions_git(value):
    try:
        repo_info = otdp_git.get_github_repo_info(value)
        print(repo_info)
        if not repo_info.get("tagged_versions"):
            return False
    except Exception as e:
        return False
    return True
