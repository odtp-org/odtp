import json
from urllib.parse import urlparse
import requests

GITHUB_API_REPOS_URL = "https://api.github.com/repos"


def check_commit_for_repo(repo_url, commit_hash=None):
    parsed_repo = urlparse(repo_url)
    if parsed_repo.scheme == "https":
        path = parsed_repo.path.replace(".git", "")
        github_api_commits_url = f"{GITHUB_API_REPOS_URL}{path}/commits"
    elif repo_url.startswith("git@github.com:"):
        path = repo_url.replace("git@github.com:", "").replace(".git", "")
        github_api_commits_url = f"{GITHUB_API_REPOS_URL}/{path}/commits"
    else:
        return None
    response = requests.get(github_api_commits_url)
    if response.status_code == 200:
        content = json.loads(response.content)
        if not commit_hash:
            commit_hash = content[0].get("sha")
            return commit_hash
        else:
            commits = [item.get("sha") for item in content]
            if commit_hash in commits:
                return commit_hash
    return None