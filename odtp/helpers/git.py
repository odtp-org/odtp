import json
import logging
import requests
import re
import yaml
import base64
from urllib.parse import urlparse
from odtp.helpers.validation import validate_odtp_yml_file

import requests

from odtp.helpers.settings import GITHUB_TOKEN

GITHUB_API_REPOS_URL = "https://api.github.com/repos"
ODTP_YML_FILE_PATH = "odtp.yml"


log = logging.getLogger(__name__)


class OdtpGithubException(Exception):
    pass


def get_github_repo_url(repo_url):
    parsed_repo = urlparse(repo_url)
    if parsed_repo.scheme == "https":
        path = parsed_repo.path.replace(".git", "")
        return f"{GITHUB_API_REPOS_URL}{path}"
    elif repo_url.startswith("git@github.com:"):
        path = repo_url.replace("git@github.com:", "").replace(".git", "")
        return f"{GITHUB_API_REPOS_URL}/{path}"
    else:
        log.exception(f"{repo_url} is not a github repo")
        raise OdtpGithubException(f"{repo_url} is not a github repo")


def make_github_api_call(url):
    log.info(f"make github api call: {url}")
    headers = {"Authorization": "token " + GITHUB_TOKEN}
    response = requests.get(url, headers=headers)
    return response


def get_git_tagged_versions(github_api_tag_url):
    if not github_api_tag_url:
        return []
    response = make_github_api_call(github_api_tag_url)
    if response.status_code != 200:
        return []
    content = json.loads(response.content)
    tagged_versions = []
    for item in content:
        item_dict = {
            "name": item.get("name"),
            "commit": item["commit"]["sha"],
        }
        tagged_versions.append(item_dict)
    return tagged_versions


def get_github_repo_info(repo_url):
    github_api_repo_url = f"{get_github_repo_url(repo_url)}"
    response = make_github_api_call(github_api_repo_url)
    if response.status_code == 200:
        content = json.loads(response.content)
        github_api_tag_url = content.get("tags_url")
        tagged_versions = get_git_tagged_versions(github_api_tag_url)
        repo_info = {
            "html_url": content.get("html_url"),
            "contents_url": content.get("contents_url").replace("{+path}", ""),
            "description": content.get("description"),
            "visibility": content.get("visibility"),
            "license": content.get("license", {}).get("name"),
            "name": content.get("name"),
            "tag_url": github_api_tag_url,
            "commits_url": content.get("commits_url"),
            "tagged_versions": tagged_versions,
        }
        return repo_info


def check_commit_for_repo(repo_url, commit_hash=None):
    if commit_hash:
        github_api_commit_url = f"{get_github_repo_url(repo_url)}/commits/{commit_hash}"
        response = make_github_api_call(github_api_commit_url)
        if response.status_code == 200:
            return commit_hash
        else:
            log.exception(f"Github repo {repo_url} has no commit {commit_hash}.")
            raise OdtpGithubException(f"Github repo {repo_url} has no commit {commit_hash}.")
    github_api_commits_url = f"{get_github_repo_url(repo_url)}/commits"
    response = make_github_api_call(github_api_commits_url)
    if response.status_code == 200:
        content = json.loads(response.content)
        if not commit_hash:
            latest_commit_hash = content[0].get("sha")
            return latest_commit_hash
    log.exception(f"Github repo {repo_url} has no commits, see {github_api_commits_url}.")
    raise OdtpGithubException(f"Github repo {repo_url} has no commits, see {github_api_commits_url}.")


def get_commit_of_component_version(repo_info, component_version):
    tagged_versions = repo_info.get("tagged_versions")
    if not tagged_versions:
        raise OdtpGithubException(f"Github repo {repo_info.get('html_url')} has no versions.")
    version_commit = [version["commit"] for version in tagged_versions
                      if version["name"] == component_version]
    if not version_commit:
        log.exception(f"Github repo {repo_info.get('html_url')} has no version {component_version}")
        version_names = [version["name"] for version in tagged_versions]
        raise OdtpGithubException(f"""Github repo {repo_info.get('html_url')} has no version {component_version}
Existing versions are {",".join(version_names)}""")
    return version_commit[0]


def test_token():
    github_api_user_url = "https://api.github.com/user"
    response = make_github_api_call(github_api_user_url)
    return response


def parse_file_from_github(repo_info, file_path, commit_hash):
    contents_url = repo_info.get("contents_url")
    if not file_path:
        raise OdtpGithubException(f"file_path must be provided to parse content from github repo.")
    github_content_url = f"{contents_url}/{file_path}?ref={commit_hash}"
    response = make_github_api_call(github_content_url)
    content = response.json()
    base64_content = content["content"]
    decoded_content = base64.b64decode(base64_content).decode("utf-8")
    sanitized_content = re.sub(r'\t', '    ', decoded_content)
    parsed_yaml = yaml.safe_load(sanitized_content)
    validate_odtp_yml_file(parsed_yaml)
    return parsed_yaml


def extract_parameters_with_defaults(data):
    """
    Extracts parameters and their default values from parsed YAML data.
    """
    parameters = data.get("parameters", [])
    result = {param["name"]: param["default-value"] for param in parameters}
    return result


def get_metadata_from_github(repo_info, commit_hash):
    get_commit_of_component_version
    parsed_data = parse_file_from_github(repo_info, ODTP_YML_FILE_PATH, commit_hash)
    return parsed_data
