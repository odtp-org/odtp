"""
This scripts contains odtp subcommands for 'new'
"""
import typer
from typing_extensions import Annotated
import logging 

import odtp.mongodb.db as db
import odtp.helpers.parse as odtp_parse
import odtp.mongodb.utils as db_utils
import odtp.helpers.git as odtp_git


## Adding listing so we can have multiple flags
from typing import List

app = typer.Typer()

log = logging.getLogger(__name__)

@app.command()
def user_entry(
    name: str = typer.Option(..., "--name", help="Specify the name"),
    email: str = typer.Option(..., "--email", help="Specify the email"),
    github: str = typer.Option(..., "--github", help="Specify the github"),
):
    """Add new user in the MongoDB"""
    user_id = db.add_user(name=name, github=github, email=email)
    log.info(f"A user has been added {user_id}")


@app.command()
def odtp_component_entry(
    name: Annotated[str, typer.Option(
        help="Specify the name"
    )],
    repository: Annotated[str, typer.Option(
        help="Specify the repository"
    )],
    component_version: Annotated[str, typer.Option(
        help="Specify the tagged component version. It needs to be available on the github repo"
    )],
    type: Annotated[str, typer.Option(
        help="""You may specify the type of the component as either 'ephemeral or persistent'"""
    )] = db_utils.COMPONENT_TYPE_EPHERMAL,    
    ports: Annotated[str, typer.Option(
        help="Specify ports seperated by a comma i.e. 8501,8201"
    )] = None,
):
    try:
        ports = odtp_parse.parse_component_ports(ports)
        repo_info = odtp_git.get_github_repo_info(repository)
        component_id, version_id = \
            db.add_component_version(
                component_name=name,
                repo_info=repo_info,
                component_version=component_version,
                type=type,
                ports=ports,
            )
    except Exception as e:
        log.error(f"ERROR: {e}")
        if hasattr(e, "__notes__"):
            log.error(f"{','.join(e.__notes__)}") 
        raise typer.Abort()     
    log.info(f"""SUCCESS: component version has been added: see above for the details.
          component_id: {component_id}
          version_id: {version_id}""")


@app.command()
def digital_twin_entry(
    user_id: str = typer.Option(None, "--user-id", help="Specify the user ID"),
    user_email: str = typer.Option(None, "--user-email", help="Specify the email"),
    name: str = typer.Option(..., "--name", help="Specify the digital twin name"),
):
    if user_id is None and user_email is None:
        raise typer.Exit("Please provide either --user-id or --user-email")

    if user_email:
        user_id = db.get_document_id_by_field_value("user_email", user_email, "users")

    dt_id = db.add_digital_twin(userRef=user_id, name=name)
    log.info(f"Digital Twin added with ID {dt_id}")


@app.command()
def execution_entry(
    execution_name: str = typer.Option(..., "--name", help="Specify the name of the execution"),
    dt_name: str = typer.Option(None, "--digital-twin-name", help="Specify the digital twin name"),
    dt_id: str = typer.Option(
        None, "--digital-twin-id", help="Specify the digital twin ID"
    ),
    component_tags: str = typer.Option(
        None, "--component-tags", help="Specify the components-tags (component-name:version) separated by commas"
    ),
    component_versions: str = typer.Option(
        None, "--component-versions", help="Specify the version_ids separated by commas"
    ),
    parameter_files: Annotated[str, typer.Option(
        help="List the files containing the parameters by step separated by commas"
    )] = None,     
    ports: Annotated[str, typer.Option(
        help="""Specify ports mappings separated by plus within the same step and , between steps i.e. 
        9001:9001+8501:8501,8080:8001+6000:6000"""
    )] = None,    
):  
    try:
        if dt_name is None and dt_id is None:
            raise typer.Exit("Please provide either --digital-twin-name or --digital-twin-id")

        if component_tags is None and component_versions is None:
            raise typer.Exit("Please provide either --component-tags or --component-versions")

        if dt_name:
            dt_id = db.get_document_id_by_field_value("name", dt_name, "digitalTwins")

        if component_tags:
            component_versions = ",".join(odtp_parse.parse_component_tags(component_tags))
        
        versions = odtp_parse.parse_versions(component_versions)
        step_count = len(versions)
        ports = odtp_parse.parse_port_mappings_for_multiple_components(
            ports=ports, step_count=step_count)
        parameters = odtp_parse.parse_parameters_for_multiple_files(
            parameter_files=parameter_files, step_count=step_count)
        execution_id, step_ids = db.add_execution(
            dt_id=dt_id,
            name=execution_name,
            versions=versions,
            parameters=parameters,
            ports=ports,
        )
    except Exception as e:
        log.error(f"ERROR: {e}")
        if hasattr(e, "__notes__"):
            log.error(f"{','.join(e.__notes__)}") 
            raise typer.Abort()     
    log.info(f"""SUCCESS: execution has been added: see above for the details.
          execution id: {execution_id}
          step_ids: {step_ids}""")


if __name__ == "__main__":
    app()
