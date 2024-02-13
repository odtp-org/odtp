import json
import os
import re
from urllib.parse import urlparse

import requests
from dotenv import dotenv_values
from nicegui import ui

config = dotenv_values(".env")

ODTP_WORKDIR = config.get("ODTP_WORKDIR", None)

ODTP_INPUT = "odtp-input"
ODTP_OUTPUT = "odtp-output"
ODTP_REPO = "repository"


def get_workdir_path(name=None):
    if not name:
        return ODTP_WORKDIR
    return os.path.join(ODTP_WORKDIR, name)


def check_project_folder(project_dir_name):
    if not ODTP_WORKDIR:
        return False
    project_path = os.path.join(ODTP_WORKDIR, project_dir_name)
    if os.path.exists(project_path):
        if not os.path.isdir(project_path):
            return False
        if len(os.listdir(project_path)) != 0:
            return False
    return True


def check_env_file(env_file_name):
    if not ODTP_WORKDIR:
        return False
    config_path = os.path.join(ODTP_WORKDIR, env_file_name)
    if not os.path.exists(config_path) or not os.path.isfile(config_path):
        return False
    return True


def create_project_folder(project_folder_name):
    project_path = os.path.join(ODTP_WORKDIR, project_folder_name)
    if check_project_folder(project_folder_name):
        try:
            if not os.path.exists(project_path):
                project_folder = os.mkdir(project_folder_name)
        except Exception as e:
            ui.notify(
                f"project path could not be set. Exception e occured: {e}",
                type="negative",
            )
        finally:
            return project_folder


def map_output_folder(project_path):
    project_content = {}
    output_path = os.path.join(project_path, ODTP_OUTPUT)
    input_path = os.path.join(project_path, ODTP_INPUT)
    if os.path.exists(output_path):
        project_content[ODTP_OUTPUT] = os.listdir(output_path)
    if os.path.exists(input_path):
        project_content[ODTP_INPUT] = os.listdir(input_path)
    print(project_content)
    return project_content


def check_docker_image_name(value):
    if not len(value) >= 4:
        return False
    if not re.match("^[a-z]+$", value):
        return False
    return True


def check_commit_for_repo(repo_url, commit_hash=None):
    parsed_repo = urlparse(repo_url)
    if parsed_repo.scheme == "https":
        path = parsed_repo.path.replace(".git", "")
        github_api_commits_url = f"https://api.github.com/repos{path}/commits"
    elif repo_url.startswith("git@github.com:"):
        path = repo_url.replace("git@github.com:", "").replace(".git", "")
        github_api_commits_url = f"https://api.github.com/repos/{path}/commits"
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
