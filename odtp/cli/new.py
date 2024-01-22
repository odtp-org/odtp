# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
"""
This scripts contains odtp subcommands for 'new'
"""
import typer
import logging
from datetime import datetime
from odtp.setup import odtpDatabase

## Temporaly placing ObjectID for dealing with steps.
## For the next version these methods for data handling will
## be placed in db
from bson import ObjectId

app = typer.Typer()


@app.command()
def user_entry(
    name: str = typer.Option(..., "--name", help="Specify the name"),
    email: str = typer.Option(..., "--email", help="Specify the email"),
    github: str = typer.Option(..., "--github", help="Specify the github"),
):
    """Add new user in the MongoDB"""
    with odtpDatabase() as dbManager:
        user_id = dbManager.add_user(name=name, github=github, email=email)
        logging.info("User added with ID {}".format(user_id))


@app.command()
def odtp_component_entry(
    component_name: str = typer.Option(..., "--name", help="Specify the name"),
    version: str = typer.Option(..., "--version", help="Specify the version"),
    component_version: str = typer.Option(
        ..., "--component-version", help="Specify the component version"
    ),
    repository: str = typer.Option(..., "--repository", help="Specify the repository"),
):
    """add new component and version in the Mongo DB:
    This is to add a compatible available component. We need to specify the version.
    TODO: Only implemented the basic features.
    TODO: Add the possibility to add component by config file
    """
    component_data = {
        "author": "Test",
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
    version_data = {
        "version": version,
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
    version_id = odtpDB.dbManager.add_version(component_id, version_data)
    odtpDB.close()
    logging.info("Version added with ID {}".format(version_id))


@app.command()
def digital_twin_entry(
    user_id: str = typer.Option(..., "--user-id", help="Specify the user ID"),
    name: str = typer.Option(..., "--name", help="Specify the name"),
):
    """add new digital twin in the Mongo DB"""
    dt_data = {
        "name": name,
        "status": "active",
        "public": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "executions": [],
    }

    odtpDB = odtpDatabase()
    dt_id = odtpDB.dbManager.add_digital_twin(user_id, dt_data)
    odtpDB.close()

    logging.info("Digital Twin added with ID {}".format(dt_id))


@app.command()
def execution_entry(
    dt_id: str = typer.Option(
        ..., "--digital-twin-id", help="Specify the digital twin ID"
    ),
    name: str = typer.Option(..., "--name", help="Specify the name of the execution"),
    components: str = typer.Option(
        ..., "--components", help="Specify the components_ids separated by commas"
    ),
    versions: str = typer.Option(
        ..., "--versions", help="Specify the version_ids separated by commas"
    ),
    workflow: str = typer.Option(
        ...,
        "--workflow",
        help="Specify the sequential order for the components, starting by 0, and separating values by commas",
    ),
):
    """add new execution in the Mongo DB"""
    components = [ObjectId(c) for c in components.split(",")]
    versions = [ObjectId(v) for v in versions.split(",")]

    components_list = [
        {"component": c, "version": v} for c, v in zip(components, versions)
    ]

    execution_data = {
        "title": name,
        "description": "Description for Execution",
        "tags": ["tag1", "tag2"],
        "workflowSchema": {
            "workflowExecutor": "odtpwf",
            "workflowExecutorVersion": "0.2.0",
            "components": components_list,  # Array of ObjectIds for components
            "workflowExecutorSchema": [int(i) for i in workflow.split(",")],
        },
        "start_timestamp": datetime.utcnow(),
        "end_timestamp": datetime.utcnow(),
        "steps": [],  # Array of ObjectIds referencing Steps collection. Change in a future by DAG graph
    }

    odtpDB = odtpDatabase()
    execution_id = odtpDB.dbManager.append_execution(dt_id, execution_data)
    odtpDB.close()

    logging.info("Execution added with ID {}".format(execution_id))

    steps_ids = []
    for c in components_list:
        step_data = {
            "timestamp": datetime.utcnow(),
            "start_timestamp": datetime.utcnow(),
            "end_timestamp": datetime.utcnow(),
            "type": "ephemeral",
            "logs": [],
            "inputs": {},
            "outputs": {},
            "component": c["component"],
            "component_version": c["version"],
            "parameters": {},
        }

        odtpDB = odtpDatabase()
        step_id = odtpDB.dbManager.append_step(execution_id, step_data)
        odtpDB.close()

        steps_ids.append(step_id)

    logging.info("STEPS added with ID {}".format(steps_ids))


if __name__ == "__main__":
    app()
