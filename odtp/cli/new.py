"""
This scripts contains odtp subcommands for 'new'
"""
import typer
from typing_extensions import Annotated

import odtp.mongodb.db as db
import odtp.helpers.parse as odtp_parse
import odtp.mongodb.utils as db_utils
import odtp.helpers.utils as odtp_utils


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


@app.command()
def odtp_component_entry(
    name: Annotated[str, typer.Option(
        help="Specify the name"
    )],
    repository: Annotated[str, typer.Option(
        help="Specify the repository"
    )],
    component_version: Annotated[str, typer.Option(
        help="Specify the component version"
    )],    
    odtp_version: Annotated[str, typer.Option(
        help="Specify the version of odtp"
    )] = None,
    commit: Annotated[str, typer.Option(
        help="""You may specify the commit of the repository. If not provided 
        the latest commit will be fetched"""
    )] = None,
    type: Annotated[str, typer.Option(
        help="""You may specify the type of the component as either 'ephemeral or persistent'"""
    )] = db_utils.COMPONENT_TYPE_EPHERMAL,    
    ports: Annotated[str, typer.Option(
        help="Specify ports seperated by a comma i.e. 8501,8201"
    )] = None,
):  
    try:
        ports = odtp_parse.parse_component_ports(ports)
        component_id, version_id = \
            db.add_component_version(
                component_name=name,
                repository=repository,
                odtp_version=odtp_version,
                component_version=component_version,
                commit_hash=commit,
                type=type,
                ports=ports,
            )
    except Exception as e:
        print(f"ERROR: {e}")
        if hasattr(e, "__notes__"):
            print(f"{','.join(e.__notes__)}") 
        raise typer.Abort()     
    print(f"""SUCCESS: component version has been added: see above for the details.
          component_id: {component_id}
          version_id: {version_id}""")


@app.command()
def digital_twin_entry(
    user_id: str = typer.Option(..., "--user-id", help="Specify the user ID"),
    name: str = typer.Option(..., "--name", help="Specify the name"),
):
    dt_id = db.add_digital_twin(userRef=user_id, name=name)
    print(f"Digital Twin added with ID {dt_id}")


@app.command()
def execution_entry(
    dt_id: str = typer.Option(
        ..., "--digital-twin-id", help="Specify the digital twin ID"
    ),
    execution_name: str = typer.Option(..., "--name", help="Specify the name of the execution"),
    component_versions: str = typer.Option(
        ..., "--component-versions", help="Specify the version_ids separated by commas"
    ),
    parameter_files: Annotated[str, typer.Option(
        help="List the files containing the parameters by step separated by commas"
    )] = None,     
    ports: Annotated[str, typer.Option(
        help="""Specify ports pairs separated by commas within the same step and + between steps i.e. 
        9001:9001+8501:8501,8080:8001+6000:6000"""
    )] = None,    
):  
    try:
        versions = odtp_parse.parse_versions(component_versions)
        step_count = len(versions)
        ports = odtp_parse.parse_ports_for_multiple_components(
            ports=ports, step_count=step_count)
        parameters = odtp_parse.parse_paramters_for_multiple_files(
            parameter_files=parameter_files, step_count=step_count)
        execution_id, step_ids = db.add_execution(
            dt_id=dt_id,
            name=execution_name,
            versions=versions,
            parameters=parameters,
            ports=ports,
        )
    except Exception as e:
        print(f"ERROR: {e}")
        if hasattr(e, "__notes__"):
            print(f"{','.join(e.__notes__)}") 
            raise typer.Abort()     
    print(f"""SUCCESS: execution has been added: see above for the details.
          execution id: {execution_id}
          step_ids: {step_ids}""")


if __name__ == "__main__":
    app()
