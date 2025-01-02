import requests
import odtp.mongodb.db as db
from odtp.helpers.settings import GITHUB_TOKEN

GITHUB_API_REPOS_URL = "https://api.github.com/users"


def validate_github_user_name(github_user_name):
    headers = {"Authorization": "token " + GITHUB_TOKEN}
    git_api_user_url = f"{GITHUB_API_REPOS_URL}/{github_user_name}"
    response = requests.get(git_api_user_url, headers=headers)
    if not response.status_code == 200:
        return False
    return True


def validate_user_name_unique(user_name):
    users = db.get_collection(db.collection_users)
    user_names = {user.get("displayName") for user in users}
    if user_name in user_names:
        return False
    return True
