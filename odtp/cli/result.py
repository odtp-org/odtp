"""
This scripts contains odtp subcommands for 'results'
"""
import logging

import typer
from typing_extensions import Annotated
import zipfile

import odtp.mongodb.db as db
from odtp.results import prepare_result

app = typer.Typer()

## Adding listing so we can have multiple flags
from typing import List


@app.command()
def prepare(    
    dt_name: str = typer.Option(
            None, "--digital-twin-name", help="Specify the digital twin name"
    ),
    dt_id: str = typer.Option(
        None, "--digital-twin-id", help="Specify the digital twin ID"
    ),
    component_tag: str = typer.Option(
        None, "--component-tags", help="Specify the components-tag (component-name:version)"
    ),
    repository: str = typer.Option(
        None, "--repository", help="Specify the repository URL"
    ),
    project_path: str = typer.Option(
        ..., "--project-path", help="Specify the path for the result execution"
    ),
):  
    try:
        if dt_name is None and dt_id is None:
            raise typer.Exit("Please provide either --digital-twin-name or --digital-twin-id")

        if dt_name:
            dt_id = db.get_document_id_by_field_value("name", dt_name, "digitalTwins")

        prepare_result(project_path, repository, component_tag, dt_id)

    except Exception as e:
        logging.error(f"ERROR: Prepare result failed: {e}") 
        raise typer.Abort()           
    else:
        logging.info("SUCCESS: images and folder structure for the result have been build") 

@app.command()
def run(
    dt_name: str = typer.Option(
            None, "--digital-twin-name", help="Specify the digital twin name"
    ),
    dt_id: str = typer.Option(
        None, "--digital-twin-id", help="Specify the digital twin ID"
    ),
    component_tag: str = typer.Option(
        None, "--component-tags", help="Specify the components-tag (component-name:version)"
    ),
    project_path: str = typer.Option(
        ..., "--project-path", help="Specify the path for the result execution"
    ),
    secrets_files: Annotated[str, typer.Option(
        help="List the files containing the secrets by step separated by commas"
    )] = None, 
): 
    try:
        componentManager = DockerManager(
            project_folder=folder,
            repo_url=repository,
            commit_hash=commit, 
            image_name=image_name, 
        )
        ports = odtp_parse.parse_port_mappings_for_one_component(ports) 
        parameters = odtp_parse.parse_paramters_for_one_file(parameter_file)
        componentManager.run_component(
            parameters=parameters, 
            ports=ports, 
            container_name=container_name
        )
    except Exception as e:
        print(f"ERROR: Run of component failed: {e}") 
        raise typer.Abort()           
    else:
        print("SUCCESS: container for the component has been started")
        