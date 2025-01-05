import os
from slugify import slugify
from odtp.helpers.settings import ODTP_PATH

def make_workdir_for_user_name(user_name):
    user_slug = slugify(user_name)
    workdir = os.path.join(ODTP_PATH, user_slug)
    os.makedirs(workdir, exist_ok=True)
    return workdir

def get_workdir_for_user_name(user_name):
    user_slug = slugify(user_name)
    workdir = os.path.join(ODTP_PATH, user_slug)
    return workdir
