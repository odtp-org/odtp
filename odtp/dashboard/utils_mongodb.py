from odtp.setup import odtpDatabase
import json


def get_user_options():
    with odtpDatabase() as dbManager:
        documents = dbManager.get_all_documents("users")
        user_options = {user["_id"]: user["displayName"] for user in documents}
    return user_options


def get_users():
    with odtpDatabase() as dbManager:
        documents = dbManager.get_all_documents("users")
        users = list(documents)
    return users

def get_digital_twins():
    with odtpDatabase() as dbManager:
        documents = dbManager.get_all_documents("digitalTwins")
        digital_twins = list(documents)
    return digital_twins


def add_new_user(name, github, email):
    with odtpDatabase() as dbManager:
        user_id = dbManager.add_user(name=name, github=github, email=email)
    return user_id


def get_current_user(user_id):
    with odtpDatabase() as dbManager:
        user = dbManager.get_document_by_id(user_id, "users")
        user_dict = json.loads(user)
        print(type(user_dict))
        print(user_dict)
    return user_dict
