# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
"""
This scripts contains odtp subcommands for building and running
docker images for individual components
"""
import typer

app = typer.Typer()
from odtp.run import DockerManager


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
    """prepare a component as docker container"""
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
        ..., "--env_file", help="Specify the path to the environment file"
    ),
    instance_name: str = typer.Option(
        ..., "--instance_name", help="Specify the name of the instance"
    ),
):
    """run a component that has been previously build as docker image
    as docker container"""
    componentManager = DockerManager(
        repo_url=repository, image_name=image_name, project_folder=folder
    )

    # TODO: Detect if previous steps has been completed
    # componentManager.download_repo()
    # componentManager.build_image()
    componentManager.run_component(env_file, instance_name=instance_name)


@app.command()
def stop():
    """TODO:Stop Component"""
    pass


@app.command()
def delete_instance(
    instance_name: str = typer.Option(
        ..., "--instance_name", help="Specify the name of the docker image"
    )
):
    """delete component"""
    componentManager = DockerManager()
    componentManager.delete_component(instance_name=instance_name)
    print("Component Deleted")


@app.command()
def delete_image(
    image_name: str = typer.Option(
        ..., "--image_name", help="Specify the name of the docker image"
    )
):
    """delete docker image"""
    componentManager = DockerManager(image_name=image_name)
    componentManager.delete_image()
    print("Component Deleted")


if __name__ == "__main__":
    app()
