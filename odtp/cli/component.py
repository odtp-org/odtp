"""
This scripts contains odtp subcommands for 'components'
"""
import typer
from typing_extensions import Annotated
import logging

from odtp.run import DockerManager
import odtp.helpers.git as odtp_git
import odtp.helpers.parse as odtp_parse
import odtp.helpers.utils as odtp_utils

app = typer.Typer()

log = logging.getLogger(__name__)


## Adding listing so we can have multiple flags
from typing import List

@app.command()
def prepare(
    folder: str = typer.Option(
        ..., "--folder", help="Specify the project folder location"
    ),
    image_name: str = typer.Option(
        ..., "--image_name", help="Specify the name of the component image"
    ),
    image_link: str = typer.Option(
        None, "--image_link", help="Specify the name of the component image link"
    ),
    repository: str = typer.Option(
        ..., "--repository", help="Specify the git repository url"
    ),
):  
    try:
        componentManager = DockerManager(
            repo_url=repository, 
            image_name=image_name,
            image_link=image_link,
            project_folder=folder
        )
        componentManager.prepare_component()
    except Exception as e:
        log.error(f"ERROR: Prepare component failed: {e}") 
        raise typer.Abort()           
    else:
        log.info("SUCCESS: image for the component has been build")

@app.command()
def run(
    folder: str = typer.Option(
        ..., "--folder", help="Specify the project folder location"
    ),
    image_name: str = typer.Option(
        ..., "--image_name", help="Specify the name of the component image"
    ),
    container_name: str = typer.Option(
        ..., "--container_name", help="Specify the name of the container"
    ),   
    repository: str = typer.Option(
        ..., "--repository", help="Specify the git repository url"
    ),
    commit: Annotated[str, typer.Option(
        help="You may specify the commit of the repository. If not provided the latest commit will be fetched"
    )] = None,
    parameter_file: Annotated[str, typer.Option(
        help="Specify the path to the environment file"
    )] = None,
    secrets_file: Annotated[str, typer.Option(
        help="Specify the path to the secrets file"
    )] = None,     
    ports: Annotated[str, typer.Option(
        help="Specify port mappings separated by a plus sign i.e. 8501:8501+8201:8201"
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
        parameters = odtp_parse.parse_parameters_for_one_file(parameter_file)
        secrets = odtp_parse.parse_parameters_for_one_file(secrets_file)
        componentManager.run_component(
            parameters=parameters,
            secrets=secrets, 
            ports=ports, 
            container_name=container_name
        )
    except Exception as e:
        log.error(f"ERROR: Run of component failed: {e}") 
        raise typer.Abort()           
    else:
        log.info("SUCCESS: container for the component has been started")



@app.command()
def delete_instance(
    instance_name: str = typer.Option(
        ..., "--instance_name", help="Specify the name of the docker image"
    )
):
    componentManager = DockerManager()
    componentManager.delete_component(instance_name=instance_name)
    log.info("Container deleted")


@app.command()
def delete_image(
    image_name: str = typer.Option(
        ..., "--image_name", help="Specify the name of the docker image"
    )
):
    componentManager = DockerManager(image_name=image_name)
    componentManager.delete_image()
    log.info("Image deleted")


if __name__ == "__main__":
    app()
