from odtp.helpers.models import OdtpDotYamlSchema
from pydantic import ValidationError
import requests
import odtp.mongodb.db as db
from odtp.helpers.settings import GITHUB_TOKEN

GITHUB_API_REPOS_URL = "https://api.github.com/users"


class OdtpYmlException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


def validate_odtp_yml_file(yaml_data):
    try:
        validated_data = OdtpDotYamlSchema(**yaml_data)
        return validated_data
    except ValidationError as ve:
        error_details = "\n".join(
            [f"{err['loc']}: {err['msg']} (type: {err['type']})" for err in ve.errors()]
        )
        raise OdtpYmlException(f"Validation failed for odtp.yml:\n{error_details}")
    except Exception as e:
        raise OdtpYmlException(f"Unexpected error during odtp.yml validation: {e}")


import odtp.mongodb.db as db


def validate_digital_twin_name_unique(digital_twin_name, user_id):
    if len(digital_twin_name) < 6:
        return False
    digital_twins = db.get_collection(db.collection_digital_twins, query={"userRef": user_id})
    digital_twin_names = {digital_twin.get("name") for digital_twin in digital_twins}
    if digital_twin_name in digital_twin_names:
        return False
    return True


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


def validate_execution_name_unique(execution_name, digital_twin_id):
    if len(execution_name) < 6:
        return False
    executions = db.get_collection(db.collection_executions, query={"digitalTwinRef": ObjectId(digital_twin_id)})
    execution_names = {execution.get("title") for execution in executions}
    if execution_name in execution_names:
        return False
    return True
