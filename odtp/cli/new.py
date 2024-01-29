"""
This scripts contains odtp subcommands for 'new'
"""
import typer

import odtp.mongodb.db as db

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
):
    component_id = db.add_component(
        component_name=component_name,
        repository=repository,
    )
    print(
        f"A component has been added with \ncomponent_id={component_id} \nversion_id={version_id}"
    )


def odtp_component_version_entry(
    component_id: str = typer.Option(..., "--name", help="Specify the name"),
    version: str = typer.Option(..., "--version", help="Specify the version"),
    component_version: str = typer.Option(
        ..., "--component-version", help="Specify the component version"
    ),
    repository_commit: str = typer.Option(..., "--repository", help="Specify the repository"),
):
    version_id = db.add_version(
        componentRef=component_id,
        version=version,
        component_version=component_version,
        repository_commit=repository_commit,
    )
    print(
        f"A version {version_id} has been added to the component_id={component_id}"
    )

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
):
    execution_id, step_ids = db.add_execution(
        dt_id=dt_id,
        name=name,
        components=components,
        versions=versions,
        workflow=workflow,
    )
    print(f"execution has been added with ID {execution_id} and steps: {step_ids}")


if __name__ == "__main__":
    app()
