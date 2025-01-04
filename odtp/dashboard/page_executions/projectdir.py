import os
import shutil
from slugify import slugify

def make_project_dir_for_execution(user_workdir, digital_twin_name, execution_title):
    digital_twin_slug = slugify(digital_twin_name)
    execution_slug = slugify(execution_title)
    project_dir = os.path.join(user_workdir, digital_twin_slug, execution_slug)
    shutil.rmtree(project_dir)
    os.makedirs(project_dir)
    return project_dir
