"""
This scripts contains odtp subcommands for 'new'
"""
import typer
from typing_extensions import Annotated
import logging
import requests
import odtp.mongodb.db as db
import odtp.mongodb.utils as mongodb_utils
import odtp.helpers.parse as odtp_parse
import odtp.helpers.git as git_helpers
import odtp.helpers.validation as validation_helpers
import traceback

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
    repository: Annotated[str, typer.Option(
        help="Specify the repository"
    )],
    component_version: Annotated[str, typer.Option(
        help="Specify the tagged component version. It needs to be available on the GitHub repo"
    )],
    debug: bool = typer.Option(False, "--debug", help="Show full traceback for errors")
):
    """
    CLI command to add a component version from a repository.
    """
    try:
        if not repository or not component_version:
            raise ValueError("Both repository and component version must be provided.")

        log.info(f"Starting process for repository: {repository}, version: {component_version}")

        component_id, version_id = db.add_component_version(
            repository=repository,
            component_version=component_version,
        )

    except git_helpers.OdtpGithubException as e:
        typer.echo(f"Error: An error occurred while fetching information from GitHub: {e}")
        raise typer.Exit(code=2)

    except mongodb_utils.OdtpDbMongoDBValidationException as e:
        typer.echo(f"Error: Component version could not be added: {e}")
        raise typer.Exit(code=3)

    except validation_helpers.OdtpYmlException as e:
        log.error(f"Validation error occurred when parsing odtp.yml")
        typer.echo(f"Error: Validation of odtp.yml failed: {e}")
        raise typer.Exit(code=4)

    except requests.RequestException as e:
        log.error(f"Network error: {e}")
        typer.echo(f"Error: A network error occurred while communicating with GitHub.: {e}")
        raise typer.Exit(code=5)

    except Exception as e:
        error_message = f"Error: An unexpected error occurred: {e}"
        if debug:
            error_message += f"\n{traceback.format_exc()}"
        typer.echo(error_message, err=True)
        raise typer.Exit(code=99)

    else:
        if component_id and version_id:
            typer.echo("✅ odtp.yml is valid!")
            success_message = (
                f"SUCCESS: Component added with details:\n"
                f" - Component ID: {component_id}\n"
                f" - Version ID: {version_id}\n"
            )
            log.info(success_message)
            typer.echo(f"✅ {success_message}")


@app.command()
def digital_twin_entry(
    user_id: str = typer.Option(None, "--user-id", help="Specify the user ID"),
    user_email: str = typer.Option(None, "--user-email", help="Specify the email"),
    name: str = typer.Option(..., "--name", help="Specify the digital twin name"),
):
    if user_id is None and user_email is None:
        raise typer.Exit("Please provide either --user-id or --user-email")

    if user_email:
        user_id = db.get_document_id_by_field_value("email", user_email, "users")

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
        traceback.print_exc()
    print(f"""SUCCESS: execution has been added: see above for the details.
          execution id: {execution_id}
          step_ids: {step_ids}""")
