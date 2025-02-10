import os
from slugify import slugify
from odtp.helpers.settings import ODTP_PATH, ODTP_SECRETS_DIR

def make_workdir_for_user_name(user_name):
    user_slug = slugify(user_name)
    workdir = os.path.join(ODTP_PATH, user_slug)
    secrets_dir = os.path.join(workdir, ODTP_SECRETS_DIR)
    os.makedirs(workdir, exist_ok=True)
    os.makedirs(secrets_dir, exist_ok=True)
    return workdir

def get_workdir_for_user_name(user_name):
    user_slug = slugify(user_name)
    workdir = os.path.join(ODTP_PATH, user_slug)
    return workdir
