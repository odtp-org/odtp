import logging
import os
import odtp.mongodb.db as db
from odtp.storage import s3Manager
from odtp.run import DockerManager
import zipfile

REPO_DIR = "repository"
INPUT_DIR = "odtp-input"
OUTPUT_DIR = "odtp-output"


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def prepare_result(project_path, repository, image_name, dt_id):

    _ = _create_project_folder(project_path)
    _ = _prepare_component(repository, image_name, project_path)
    outputs_ids = _get_result_outputs(dt_id)
    _ = _download_outputs(outputs_ids, project_path)

    log.info("Result prepared successfully")



def _create_project_folder(project_path):
    os.makedirs(project_path, exist_ok=True)
    log.info(f"Project folder created at {project_path}")

def _prepare_component(repository, image_name, folder):
    componentManager = DockerManager(
        repo_url=repository, 
        image_name=image_name, 
        project_folder=folder
    )
    componentManager.prepare_component()
    log.info(f"Component prepared at {folder}")

def _get_result_outputs(dt_id):
    dt_doc = db.get_document_by_id(
        document_id=dt_id, 
        collection=db.collection_digital_twins
    )

    result_doc = db.get_document_by_id(
        document_id=dt_doc["result"][0], 
        collection=db.collection_results
    )

    outputs_ids = result_doc["output"]
    log.info(f"Result output retrieved {dt_id}")

    return outputs_ids

def _download_outputs(outputs_ids, project_path):

    for output_id in outputs_ids:
        # Get the output document
        output_doc = db.get_document_by_id(
            document_id=output_id, 
            collection=db.collection_outputs
        )

        s3_key = output_doc["s3_key"]
        filename = output_doc["filename"]

        # Download input data in the in the project folder
        s3M = s3Manager()
        s3M.download_file(s3_key + "/" + filename, project_path)
        s3M.closeConnection()

        output_zip_path = os.path.join(project_path, filename)

        # Uncompress it
        with zipfile.ZipFile(output_zip_path, 'r') as zip_ref:
            zip_ref.extractall(project_path)

        # Remove zip
        os.remove(output_zip_path)

    log.info(f"Output Downloaded {outputs_ids}")