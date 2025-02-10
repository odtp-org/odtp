"""
This scripts contains odtp subcommands for 'new'
"""
import typer
from typing_extensions import Annotated
import logging
from rich.console import Console
import odtp.mongodb.db as db
import odtp.helpers.parse as odtp_parse
import odtp.helpers.git as git_helpers
import odtp.helpers.validation as validation_helpers
import odtp.mongodb.utils as mongodb_utils
import traceback

app = typer.Typer()
console = Console()

log = logging.getLogger(__name__)

@app.command()
def user_entry(
    name: str = typer.Option(..., "--name", help="Specify the name"),
    email: str = typer.Option(..., "--email", help="Specify the email"),
    github: str = typer.Option(..., "--github", help="Specify the github"),
):
    """Add new user in the MongoDB"""
    try:
        if name is None or email is None or github is None:
            console.print("[bold red]❌ ERROR:[/bold red] Please provide either --name or --email and --github")
            raise typer.Exit(code=1)

        if not validation_helpers.validate_user_name_unique(name):
            console.print("[bold red]❌ ERROR:[/bold red] --name must be unique.")
            raise typer.Exit(code=1)

        if not validation_helpers.validate_github_user_name(github):
            console.print("[bold red]❌ ERROR:[/bold red] --github must be a valid github user name.")
            raise typer.Exit(code=1)

        user_id = db.add_user(name=name, github=github, email=email)

    except typer.Exit:
        pass

    except Exception as e:
        log.exception("Unexpected error in user_entry")
        console.print(f"[bold red]❌ ERROR:[/bold red] Failed to add user. Details: {str(e)}")
        raise typer.Exit(code=1)
    else:
        success_message = f"[bold green]✅ SUCCESS: User with User Id {user_id} has been added![/bold green]"
        console.print(success_message)


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
        console.print(f"[bold red]❌ ERROR:An error occurred while fetching information from GitHub: {e}[/bold red]")
        raise typer.Exit(code=1)

    except mongodb_utils.OdtpDbMongoDBValidationException as e:
        console.print(f"[bold yellow]⚠️ WARNING: Component was not added in db: {e}[/bold yellow] ")
        raise typer.Exit(code=1)

    except validation_helpers.OdtpYmlException as e:
        console.print(f"[bold red]❌ ERROR: Validation error occurred when parsing odtp.yml: {e}[/bold red]")
        log.error(f"Validation error occurred when parsing odtp.yml")
        raise typer.Exit(code=1)

    except requests.RequestException as e:
        log.error(f"Network error: {e}")
        console.print(f"[bold red]❌ ERROR:[/bold red]: A network error occurred while communicating with GitHub.: {e}[/bold red]")
        raise typer.Exit(code=1)

    except Exception as e:
        error_message = f"Error: An unexpected error occurred: {e}"
        if debug:
            error_message += f"\n{traceback.format_exc()}"
        typer.echo(error_message, err=True)
        raise typer.Exit(code=1)

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
    try:
        if user_id is None and user_email is None:
            console.print("[bold red]❌ ERROR: Please provide either --user-id or --user-email[/bold red]")
            raise typer.Exit(code=1)

        if user_email:
            user_id = db.get_document_id_by_field_value("email", user_email, "users")

        if not user_id:
            console.print("[bold red]❌ ERROR: User does not exist. Please add the user first.[/bold red]")
            raise typer.Exit(code=1)

        if not validation_helpers.validate_digital_twin_name_unique(digital_twin_name=name, user_id=user_id):
            console.print("[bold yellow]⚠️ WARNING: Digital Twin has not been created since it already exists.[/bold yellow]")
            raise typer.Exit(code=1)

        dt_id = db.add_digital_twin(userRef=user_id, name=name)

        if not dt_id:
            console.print("[bold red]❌ ERROR:Failed to create Digital Twin due to a database issue.[/bold red]")
            raise typer.Exit(code=1)

    except typer.Exit:
        pass

    except Exception as e:
        console.print(f"[bold red]❌ ERROR:An unexpected error occurred: {str(e)}[/bold red] ")
        log.exception("Unexpected error in digital_twin_entry")
        raise typer.Exit(code=1)

    else:
        success_message = f"[bold green]✅ SUCCESS: Digital Twin with id {dt_id} has been added![/bold green]"
        console.print(success_message)


@app.command()
def workflow_entry(
    workflow_name: str = typer.Option(..., "--name", help="Specify the name of the workflow"),
    component_tags: str = typer.Option(
        None, "--component-tags", help="Specify the components-tags (component-name:version) separated by commas"
    ),
    component_versions: str = typer.Option(
        None, "--component-versions", help="Specify the version_ids separated by commas"
    )
):
    try:
        if component_tags is None and component_versions is None:
            console.print("[bold red]❌ ERROR: Please provide either --component-tags or --component-versions[/bold red]")
            raise typer.Exit(code=1)
        if component_tags:
            component_versions = ",".join(odtp_parse.parse_component_tags(component_tags))
        versions = odtp_parse.parse_versions(component_versions)
        workflow_id = db.add_workflow(
            name=workflow_name,
            workflow=versions,
        )
    except Exception as e:
        console.print(f"[bold red]❌ ERROR: An unexpected error occurred: {str(e)}[/bold red]")
        log.exception("Unexpected error in workflow_entry")
        raise typer.Exit(code=1)
    success_message = (
        f"SUCCESS: Workflow has been added:\n"
        f" - Workflow ID: {workflow_id}\n"
    )
    console.print(f"[bold green]✅ {success_message}[/bold green]")


@app.command()
def execution_entry(
    execution_name: str = typer.Option(..., "--name", help="Specify the name of the execution"),
    wf_id: str = typer.Option(
        None, "--workflow-id", help="Specify the workflow ID"
    ),
    component_tags: str = typer.Option(
        None, "--component-tags", help="Specify the components-tags (component-name:version) separated by commas"
    ),
    dt_name: str = typer.Option(None, "--digital-twin-name", help="Specify the digital twin name"),
    dt_id: str = typer.Option(
        None, "--digital-twin-id", help="Specify the digital twin ID"),
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
            console.print("[bold red]❌ ERROR: Please provide either --digital-twin-name or --digital-twin-id[/bold red]")
            raise typer.Exit(code=1)
        if wf_id is None and component_tags is None:
            console.print("[bold red]❌ ERROR: Please provide either --workflow-id or --component-tags")
            raise typer.Exit(code=1)
        if dt_name:
            dt_id = db.get_document_id_by_field_value("name", dt_name, "digitalTwins")
            if not dt_id:
                console.print("[bold red]❌ ERROR: Digital Twin with name {dt_name} was not found")
                raise typer.Exit(code=1)
        if not validation_helpers.validate_execution_name_unique(execution_name, dt_id):
            console.print("[bold yellow]⚠️ WARNING: Execution already exists: you can rerun it [/bold yellow]")
            raise typer.Exit(code=1)
        if wf_id:
            workflow = db.get_document_by_id(wf_id, db.collection_workflows)

        if component_tags:
            component_versions = ",".join(odtp_parse.parse_component_tags(component_tags))
            versions = odtp_parse.parse_versions(component_versions)
            workflow = db.get_workflow_or_create_by_versions(execution_name, versions)
        step_count = len(workflow.get("versions"))
        if parameter_files is None:
            parameters = db.get_default_parameters_for_workflow(workflow["versions"])
        else:
            parameters = odtp_parse.parse_parameters_for_multiple_files(
                parameter_files=parameter_files, step_count=step_count
            )
        if ports is None:
            ports = db.get_default_port_mappings_for_workflow(workflow["versions"])
        else:
            ports = odtp_parse.parse_port_mappings_for_multiple_components(
                ports=ports, step_count=step_count
            )
        execution_id, step_ids = db.add_execution(
            dt_id=dt_id,
            workflow_id=workflow["_id"],
            name=execution_name,
            parameters=parameters,
            ports=ports,
        )
    except Exception as e:
        log.error(f"ERROR: {e}")
        traceback.print_exc()
    else:
        success_message = (
            f"SUCCESS: execution has been added: see above for the details.\n"
            f" - execution id: {execution_id}\n"
            f" - step_ids: {step_ids}\n"
        )
        log.info(success_message)
        console.print(f"[bold green]✅ {success_message}[/bold green]")


if __name__ == "__main__":
    app()
