"""
This scripts contains odtp subcommands for 'new'
"""
import typer

import odtp.mongodb.db as db

## Adding listing so we can have multiple flags
from typing import List

app = typer.Typer()


@app.command()
def user_entry(
    name: str = typer.Option(..., "--name", help="Specify the name"),
    email: str = typer.Option(..., "--email", help="Specify the email"),
    github: str = typer.Option(..., "--github", help="Specify the github"),
):
    """Add new user in the MongoDB"""
    user_id = db.add_user(name=name, github=github, email=email)
    print(f"A user has been added {user_id}")


# New Component. This is to add a compatible available component. We need to specify the version.
# Only implemented the basic features
# Add the possibility to add component by config file
@app.command()
def odtp_component_entry(
    component_name: str = typer.Option(..., "--name", help="Specify the name"),
    repository: str = typer.Option(..., "--repository", help="Specify the repository"),
    odtp_version: str = typer.Option(..., "--odtp-version", help="Specify the version of odtp"),
    component_version: str = typer.Option(
        ..., "--component-version", help="Specify the component version"
    ),
<<<<<<< HEAD
    commmit: str = typer.Option(
        ..., "--commit", help="Specify the commit of the repository"),
):
    component_id, version_id = db.add_component_version(
        component_name=component_name,
        repository=repository,
        odtp_version=odtp_version,
        component_version=component_version,
        commit_hash=commmit,
    )
    print(
        f"A component version has been added\nversion_id: {version_id}\ncomponent_id: {component_id}"
    )
=======
    repository: str = typer.Option(..., "--repository", help="Specify the repository"),
    ports: List[str] = typer.Option([], "--port", "-p", help="Specify ports")
):
    # New component
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
        "ports": ports,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    odtpDB = odtpDatabase()
    version_id = odtpDB.dbManager.add_version(component_id, version_data)
    odtpDB.close()
    logging.info("Version added with ID {}".format(version_id))

>>>>>>> b59ecf3 (Ports added to component/version docs (single) and steps docs (pair). It's required when running the component.)

# New Digital Twin
@app.command()
def digital_twin_entry(
    user_id: str = typer.Option(..., "--user-id", help="Specify the user ID"),
    name: str = typer.Option(..., "--name", help="Specify the name"),
):
    dt_id = db.add_digital_twin(userRef=user_id, name=name)
    print(f"Digital Twin added with ID {dt_id}")


# New Execution
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
    ports: List[str] = typer.Option(
        [], "--port", "-p", help="Specify ports pairs i.e. -p 9001:9001"
    ),
):

    execution_id, step_ids = db.add_execution(
        dt_id=dt_id,
        name=name,
        components=components,
        versions=versions,
        workflow=workflow,
        ports=ports,
    )
    print(f"execution has been added with ID {execution_id} and steps: {step_ids}")


if __name__ == "__main__":
    app()
