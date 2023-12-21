# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).

"""Command line interface to the odpt package."""
from enum import Enum
from typing import List, Optional

import click
import typer
from datetime import datetime
import logging

## ODTP METHODS
from .initial_setup import odtpDatabase, s3Database
from .run import DockerManager
from .workflow import WorkflowManager


## Temporaly placing ObjectID for dealing with stesp. 
## For the next version these methods for data handling will 
## be placed in db
from bson import ObjectId

#from odtp import __version__

app = typer.Typer(add_completion=False)
new = typer.Typer()
db = typer.Typer()
s3 = typer.Typer()
component = typer.Typer()
log = typer.Typer()
setup = typer.Typer()
dashboard = typer.Typer()
execution = typer.Typer()

app.add_typer(new, name="new")
app.add_typer(db, name="db")
app.add_typer(s3, name="s3")
app.add_typer(component, name="component")
app.add_typer(log, name="log")
app.add_typer(setup, name="setup")
app.add_typer(dashboard, name="dashboard")
app.add_typer(execution, name="execution")

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
def user_entry(name: str = typer.Option(
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
    logging.info("User added with ID {}".format(user_id))
    

# New Component. This is to add a compatible available component. We need to specify the version.
# Only implemented the basic features
# Add the possibility to add component by config file
@new.command()
def odtp_component_entry(component_name: str = typer.Option(
                    ...,
                    "--name",
                    help="Specify the name"
                    ),
                    version: str = typer.Option(
                    ...,
                    "--version",
                    help="Specify the version"
                    ),
                    component_version: str = typer.Option(
                    ...,
                    "--component-version",
                    help="Specify the component version"
                    ),
                    repository: str = typer.Option(
                    ...,
                    "--repository",
                    help="Specify the repository"
                    )):

    # New component
    component_data= {"author": "Test",
                    "componentName": component_name,
                    "status": "active",
                    "title": "Title for ComponentX",
                    "description": "Description for ComponentX",
                    "tags": ["tag1", "tag2"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
    

    odtpDB = odtpDatabase()
    component_id = odtpDB.dbManager.add_component(component_data)
    odtpDB.close()
    logging.info("Component added with ID {}".format(component_id))

    # New version
    version_data = {"version": version,
                "component_version": component_version,
                "repoLink": repository,
                "dockerHubLink": "",
                "parameters": {},
                "title": "Title for Version v1.0",
                "description": "Description for Version v1.0",
                "tags": ["tag1", "tag2"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
    
    odtpDB = odtpDatabase()
    version_id = odtpDB.dbManager.add_version(component_id,version_data)
    odtpDB.close()
    logging.info("Version added with ID {}".format(version_id))

# New Digital Twin
@new.command()
def digital_twin_entry(user_id: str = typer.Option(
                    ...,
                    "--user-id",
                    help="Specify the user ID"
                    ),
                    name: str = typer.Option(
                    ...,
                    "--name",
                    help="Specify the name"
                    ) ):
    
    dt_data = {"name" : name,
                "status": "active",
                "public": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "executions": []  
                }
    
    odtpDB = odtpDatabase()
    dt_id = odtpDB.dbManager.add_digital_twin(user_id, dt_data)
    odtpDB.close()

    logging.info("Digital Twin added with ID {}".format(dt_id))

# New Execution 
@new.command()
def execution_entry(dt_id: str = typer.Option(
                ...,
                "--digital-twin-id",
                help="Specify the digital twin ID"
                ),
                name: str = typer.Option(
                ...,
                "--name",
                help="Specify the name of the execution"
                ),
                components: str = typer.Option(
                ...,
                "--components",
                help="Specify the components_ids separated by commas"
                ),
                versions: str = typer.Option(
                ...,
                "--versions",
                help="Specify the version_ids separated by commas"
                ),
                workflow: str = typer.Option(
                ...,
                "--worflow",
                help="Specify the sequential order for the components, starting by 0, and separating values by commas"
                )):
    

    components = [ObjectId(c) for c in components.split(',')]
    versions = [ObjectId(v) for v in versions.split(',')]

    components_list = [{"component": c, "version": v } for c,v in zip(components, versions) ]


    execution_data = {"title": name,
    "description": "Description for Execution",
    "tags": ["tag1", "tag2"],
    "workflowSchema": {
        "workflowExecutor": "odtpwf",
        "worflowExecutorVersion": "0.2.0",
        "components": components_list,  # Array of ObjectIds for components
        "workflowExecutorSchema": [int(i) for i in workflow.split(",")]
    },
    "start_timestamp": datetime.utcnow(),
    "end_timestamp": datetime.utcnow(),
    "steps": []  # Array of ObjectIds referencing Steps collection. Change in a future by DAG graph
    }


    odtpDB = odtpDatabase()
    execution_id = odtpDB.dbManager.append_execution(dt_id, execution_data)
    odtpDB.close()

    logging.info("Digital Twin added with ID {}".format(execution_id))

    steps_ids = []
    for c in components_list:
        step_data = {"timestamp": datetime.utcnow(),
            "start_timestamp": datetime.utcnow(),
            "end_timestamp": datetime.utcnow(),
            "type": "ephemeral",
            "logs": [],
            "inputs": {},
            "outputs": {},
            "component": c["component"],
            "component_version": c["version"],
            "parameters": {}
        }

        odtpDB = odtpDatabase()
        step_id = odtpDB.dbManager.append_step(execution_id, step_data)
        odtpDB.close()

        steps_ids.append(step_id)

    logging.info("STEPS added with ID {}".format(steps_ids))


# Output, Result is always created as a result of an execution

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

#### S3 Download
@s3.command()
def download(s3_path: str = typer.Option(
            ...,
            "--s3-path",
            help="Specify the s3 Path"
        ), 
        output_path: str = typer.Option(
            ...,
            "--output-path",
            help="Specify the path to the folder where the file is going to be downloaded"
        )):
    
    odtpS3 = s3Database()
    odtpS3.download_file(s3_path, output_path)
    odtpS3.close()
    

# Running Individual Components
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


# Running Workflow Executions
###############################################################

@execution.command()
def prepare(execution_id: str = typer.Option(
            ...,
            "--execution-id",
            help="Specify the ID of the execution"
        ),
        project_path: str = typer.Option(
            ...,
            "--project-path",
            help="Specify the path for the execution"
        )):

    odtpDB = odtpDatabase()
    execution_doc = odtpDB.dbManager.get_document_by_id(execution_id, "executions")
    odtpDB.close()

    flowManager = WorkflowManager(execution_doc, project_path)
    flowManager.prepare_workflow()

@execution.command()
def run(execution_id: str = typer.Option(
            ...,
            "--execution-id",
            help="Specify the ID of the execution"
        ),
        project_path: str = typer.Option(
            ...,
            "--project-path",
            help="Specify the path for the execution"
        ),
        env_files: str = typer.Option(
            ...,
            "--env-files",
            help="Specify the path for the env files separated by commas."
        )):

    odtpDB = odtpDatabase()
    execution_doc = odtpDB.dbManager.get_document_by_id(execution_id, "executions")
    odtpDB.close()

    env_files = env_files.split(",")

    flowManager = WorkflowManager(execution_doc, project_path)
    flowManager.run_workflow(env_files)
    

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