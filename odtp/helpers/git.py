import json
from urllib.parse import urlparse

import requests

from odtp.helpers.settings import GITHUB_TOKEN

GITHUB_API_REPOS_URL = "https://api.github.com/repos"


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
        raise OdtpGithubException(f"{repo_url} is not a github repo")


def make_github_api_call(url):
    headers = {"Authorization": "token " + GITHUB_TOKEN}
    response = requests.get(url, headers=headers)
    return response


def get_github_repo_info(repo_url):
    github_api_repo_url = f"{get_github_repo_url(repo_url)}"
    response = make_github_api_call(github_api_repo_url)
    if response.status_code == 200:
        content = json.loads(response.content)
        repo_info = {
            "html_url": content.get("html_url"),
            "description": content.get("description"),
            "visibility": content.get("visibility"),
            "license": content.get("license", {}).get("name"),
            "name": content.get("name"),
        }
        return repo_info


def check_commit_for_repo(repo_url, commit_hash=None):
    github_api_commits_url = f"{get_github_repo_url(repo_url)}/commits"
    response = make_github_api_call(github_api_commits_url)
    if response.status_code == 200:
        content = json.loads(response.content)
        if not commit_hash:
            commit_hash = content[0].get("sha")
            return commit_hash
        else:
            commits = [item.get("sha") for item in content]
            if commit_hash in commits:
                return commit_hash
    raise OdtpGithubException(f"Github repo {repo_url} has no commit {commit_hash}")
