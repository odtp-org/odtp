"""
This scripts contains odtp subcommands for 'components'
"""
import typer

from odtp.run import DockerManager

app = typer.Typer()

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
    repository: str = typer.Option(
        ..., "--repository", help="Specify the git repository url"
    ),
):
    componentManager = DockerManager(
        repo_url=repository, image_name=image_name, project_folder=folder
    )
    componentManager.download_repo()
    componentManager.build_image()


@app.command()
def run(
    folder: str = typer.Option(
        ..., "--folder", help="Specify the project folder location"
    ),
    image_name: str = typer.Option(
        ..., "--image_name", help="Specify the name of the component image"
    ),
    repository: str = typer.Option(
        ..., "--repository", help="Specify the git repository url"
    ),
    env_file: str = typer.Option(
        None, "--env_file", help="Specify the path to the environment file"
    ),
    instance_name: str = typer.Option(
        ..., "--instance_name", help="Specify the name of the instance"
    ),
    ports: List[str] = typer.Option(
        None, "--port", "-p", help="Specify ports"
    ),
):
    componentManager = DockerManager(
        repo_url=repository, image_name=image_name, project_folder=folder
    )


    # TODO: Detect if previous steps has been completed
    # componentManager.download_repo()
    # componentManager.build_image()
    componentManager.run_component(env_file, ports, instance_name=instance_name)


#### TODO: Stop Component
@app.command()
def stop():
    pass


@app.command()
def delete_instance(
    instance_name: str = typer.Option(
        ..., "--instance_name", help="Specify the name of the docker image"
    )
):
    componentManager = DockerManager()
    componentManager.delete_component(instance_name=instance_name)
    print("Component Deleted")


@app.command()
def delete_image(
    image_name: str = typer.Option(
        ..., "--image_name", help="Specify the name of the docker image"
    )
):
    componentManager = DockerManager(image_name=image_name)
    componentManager.delete_image()
    print("Component Deleted")


if __name__ == "__main__":
    app()
