import os
from odtp.helpers.settings import ODTP_PATH

def make_workdir_for_user_name(user_name):
    workdir = os.path.join(ODTP_PATH, user_name)
    os.makedirs(workdir, exist_ok=True)
    return workdir

def get_workdir_for_user_name(user_name):
    workdir = os.path.join(ODTP_PATH, user_name)
    return workdir
