# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).

"""Command line interface to the odpt package."""
from enum import Enum
from typing import List, Optional

import click
import typer
import datetime

## ODTP METHODS
from .initial_setup import odtpDatabase, s3Database
from .run import DockerManager

#from odtp import __version__

app = typer.Typer(add_completion=False)
new = typer.Typer()
db = typer.Typer()
s3 = typer.Typer()
component = typer.Typer()
log = typer.Typer()
setup = typer.Typer()
dashboard = typer.Typer()

app.add_typer(new, name="new")
app.add_typer(db, name="db")
app.add_typer(s3, name="s3")
app.add_typer(component, name="component")
app.add_typer(log, name="log")
app.add_typer(setup, name="setup")
app.add_typer(dashboard, name="dashboard")

# Used to autogenerate docs with sphinx-click
@click.group()
def cli():
    """Command line group"""
    pass

def version_callback(value: bool):
    if value:
        # TODO: Fix
        print(f"odtp {__version__}")
        # Exits successfully
        raise typer.Exit()
    


typer_cli = typer.main.get_command(app)
cli.add_command(typer_cli, "cli")

### New Commands
###############################################################

# New user
@new.command()
def user(name: str = typer.Option(
            ...,
            "--name",
            help="Specify the name"
        ),
        email: str = typer.Option(
            ...,
            "--email",
            help="Specify the email"
        ),
        github: str = typer.Option(
            ...,
            "--github",
            help="Specify the github"
        )):

    # This need to be manage by Database class
    user_data = {
                "displayName": name,
                "email": email,
                "github": github,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

    odtpDB = odtpDatabase()
    user_id = odtpDB.dbManager.add_user(user_data)
    odtpDB.close()
    print("User added with ID {}".format(user_id))
    

# New Digital Twin
@new.command()
def digital_twin():
    pass

# New Execution 
@new.command()
def execution():
    pass

# New Component. This is to add a compatible available component. We need to specify the version.
@new.command()
def odtp_component():
    pass

# Step, Output, Result is always created as a result of an execution

### Setup Commands
###############################################################

@setup.command()
def initiate():
    odtpDB = odtpDatabase()
    odtpDB.run_initial_setup()

    # Save all collections as JSON
    odtpDB.dbManager.export_all_collections_as_json('odtpDB.json')

    odtpS3 = s3Database()
    odtpS3.create_folders(["odtp"])


    odtpDB.close()
    odtpS3.close()

    print("ODTP DB/S3 and Mockup data generated")

@setup.command()
def delete():
    odtpDB = odtpDatabase()
    odtpDB.deleteAll()

    odtpS3 = s3Database()
    odtpS3.deleteAll()

    print("All deleted")


### MongoDB Commands
###############################################################

# Create, delete, check Schema?
@db.command()
def get(id: str = typer.Option(
            ...,
            "--id",
            help="Specify the id"
        ), 
        collection: str = typer.Option(
            ...,
            "--collection",
            help="Specify the collection"
        )):
    
    odtpDB = odtpDatabase()
    out = odtpDB.dbManager.get_document_by_id(id, collection)
    odtpDB.close()

    print(out)

@db.command()
def showAll():
    odtpDB = odtpDatabase()
    out = odtpDB.dbManager.get_all_collections_as_json_string
    odtpDB.close()

    print(out())

@db.command()
def deleteAll():
    odtpDB = odtpDatabase()
    odtpDB.deleteAll()
    odtpDB.close()

    print("All collection deleted.")

# S3
###############################################################


#### TODO: S3 Create

#### TODO: S3 Delete

#### TODO: S3 Check

#### TODO: S3 Download

# Running
###############################################################

@component.command()
def prepare(folder: str = typer.Option(
            ...,
            "--folder",
            help="Specify the project folder location"
        ), 
        image_name: str = typer.Option(
            ...,
            "--image_name",
            help="Specify the name of the component image"
        ), 
        repository: str = typer.Option(
            ...,
            "--repository",
            help="Specify the git repository url"
        )):
    
    componentManager = DockerManager(repo_url=repository, 
                                     image_name=image_name, 
                                     project_folder=folder)
    componentManager.download_repo()
    componentManager.build_image()

@component.command()
def run(folder: str = typer.Option(
            ...,
            "--folder",
            help="Specify the project folder location"
        ), 
        image_name: str = typer.Option(
            ...,
            "--image_name",
            help="Specify the name of the component image"
        ), 
        repository: str = typer.Option(
            ...,
            "--repository",
            help="Specify the git repository url"
        ), 
        env_file: str = typer.Option(
            ...,
            "--env_file",
            help="Specify the path to the environment file"
        ),
        instance_name: str = typer.Option(
            ...,
            "--instance_name",
            help="Specify the name of the instance"
        )):

    componentManager = DockerManager(repo_url=repository, 
                                     image_name=image_name, 
                                     project_folder=folder)
    
    # TODO: Detect if previous steps has been completed
    #componentManager.download_repo()
    #componentManager.build_image()
    componentManager.run_component(env_file, instance_name=instance_name)


#### TODO: Stop Component
@component.command()
def stop():
    pass

@component.command()
def delete_instance(instance_name: str = typer.Option(
            ...,
            "--instance_name",
            help="Specify the name of the docker image"
        )):
    componentManager = DockerManager()
    componentManager.delete_component(instance_name=instance_name)
    print("Component Deleted")

@component.command()
def delete_image(image_name: str = typer.Option(
            ...,
            "--image_name",
            help="Specify the name of the docker image"
        )):
    componentManager = DockerManager(image_name=image_name)
    componentManager.delete_image()
    print("Component Deleted")


# GUI
###############################################################
import streamlit.web.cli as stcli
import sys
import os 

@dashboard.command()
def run(port: str = typer.Option(
                    ...,
                    "--port",
                    help="Specify the port"
                )):
    
    # Execute Strealit
    os.chdir("odtp")
    sys.argv = ["streamlit", "run", "gui/app.py", "--server.port", port]
    sys.exit(stcli.main())

    #stcli.run('gui/app.py', port)


# This callback is triggered when odtp is called without subcommand
@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback
    )
):
    """odtp runs and organize digital twins."""
    

if __name__ == "__main__":
    app()