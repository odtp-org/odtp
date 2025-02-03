"""
This scripts contains odtp subcommands for 'execution'
"""
import typer
from typing_extensions import Annotated
from rich.console import Console
import logging

import odtp.mongodb.db as db
import odtp.helpers.parse as odtp_parse
from odtp.workflow import WorkflowManager
import odtp.helpers.environment as odtp_env
from odtp.storage import s3Manager
import odtp.helpers.environment as env_helpers


app = typer.Typer()
console = Console()

log = logging.getLogger(__name__)

## Adding listing so we can have multiple flags
from typing import List


@app.command()
def prepare(
    execution_name: str = typer.Option(
        None, "--execution-name", help="Specify the name of the execution"
    ),
    execution_id: str = typer.Option(
        None, "--execution-id", help="Specify the ID of the execution"
    ),
    project_path: str = typer.Option(
        None, "--project-path", help="Specify the path for the execution"
    ),
):
    try:
        if execution_id is None and execution_name is None:
            console.print(f"[bold red]❌ ERROR: Please provide either --execution-name or --execution-id [/bold red] ")
            raise typer.Exit(code=1)

        if execution_name:
            execution_id = db.get_document_id_by_field_value("title", execution_name, "executions")
            if not execution_id:
                console.print(f"[bold red]❌ ERROR: Execution with name {execution_name} was not found.[/bold red] ")
                raise typer.Exit(code=1)


        execution = db.get_document_by_id(
            document_id=execution_id,
            collection=db.collection_executions
        )
        if not execution.get("execution_path") and not project_path:
            console.print(f"[bold red]❌ ERROR: Project path not provided.[/bold red]")
            raise typer.Exit(code=1)

        if not env_helpers.project_folder_exists_file_or_not_empty(project_path):
            console.print(f"[bold yellow]⚠️ WARNING: Project path exists and is not an empty directory[/bold yellow]")
            raise typer.Exit(code=1)
        env_helpers.make_project_dir(project_path)

        if project_path:
            db.set_execution_path(execution_id, execution_path=project_path)
            execution = db.get_document_by_id(
                document_id=execution_id,
                collection=db.collection_executions
            )
        print(execution)

        if not execution.get("execution_path"):
            console.print(f"[bold red]❌ ERROR:[/bold red] Failed to set execution path")
            raise typer.Exit(code=1)
        flowManager = WorkflowManager(execution)
        flowManager.prepare_workflow()

    except typer.Exit:
        pass

    except Exception as e:
        msg = f"ERROR: Prepare execution failed: {e}"
        log.exception(msg)
        print(msg)
        raise typer.Abort()
    else:
        success_message = f"[bold green]✅ SUCCESS: images for the execution have been build![/bold green]"
        console.print(success_message)


@app.command()
def run(
    execution_name: str = typer.Option(
        None, "--execution-name", help="Specify the name of the execution"
    ),
    execution_id: str = typer.Option(
        None, "--execution-id", help="Specify the ID of the execution"
    ),
    secrets_files: Annotated[str, typer.Option(
        help="List the files containing the secrets by step separated by commas"
    )] = None,
    run_steps: Annotated[str, typer.Option(
        help="List the run of steps as list of T and F separated by commas"
    )] = None
):
    try:
        if execution_id is None and execution_name is None:
            raise typer.Exit("Please provide either --execution-name or --execution-id")

        if execution_name:
            execution_id = db.get_document_id_by_field_value("title", execution_name, "executions")

        execution = db.get_document_by_id(
            document_id=execution_id,
            collection=db.collection_executions
        )
        if not execution.get("execution_path"):
            console.print(f"[bold red]❌ ERROR:[/bold red] Execution has no execution path: prepare execution first.")
            raise typer.Exit(code=1)

        step_count = len(execution["workflowSchema"]["workflowExecutorSchema"])

        if run_steps:
            run_flags = odtp_parse.parse_run_flags(run_steps, step_count)
            for i, step_id in enumerate(execution.get("steps")):
                step_id = str(step_id)
                if run_flags[i] == "T":
                    update_value = True
                elif run_flags[i] == "F":
                    update_value = False
                db.update_step(step_id, {"run": update_value})

        # get document again after updates
        steps = db.get_document_by_ids_in_collection(
            document_ids=execution["steps"], collection=db.collection_steps
        )
        steps_to_run = [step.get("run_step") for step in steps if step.get("run_step")]
        if not steps_to_run:
            console.print(f"[bold yellow]⚠️ WARNING: No step selected for run.[/bold yellow] ")
            raise typer.Exit(code=1)

        secrets = odtp_parse.parse_parameters_for_multiple_files(
            parameter_files=secrets_files, step_count=step_count)
        flowManager = WorkflowManager(execution, secrets)
        flowManager.run_workflow()

    except typer.Exit:
        pass

    except odtp_parse.OdtpParameterParsingException as e:
        console.print(f"[bold red]❌ ERROR:[/bold red] Exception parsing parameters occurred: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        msg = f"ERROR: Run execution failed: {e}"
        log.exception(msg)
        print(msg)
        raise typer.Abort()
    else:
        msg = "containers for the execution have been run"
        success_message = f"[bold green]✅ SUCCESS: {msg}[/bold green]"
        console.print(success_message)


@app.command()
def delete(
    execution_name: str = typer.Option(
        None, "--execution-name", help="Specify the name of the execution"
    ),
    execution_id: str = typer.Option(
        None, "--execution-id", help="Specify the ID of the execution"
    ),
    project_path: str = typer.Option(
        None, "--project-path", help="Specify the path for the execution"
    ),
    keep_project_path: bool = typer.Option(
        True, "--keep-project-path", help="Keep the project directory after deleting contents"
    ),
):
    try:
        if execution_id is None and execution_name is None:
            raise typer.Exit("Please provide either --execution-name or --execution-id")

        if execution_name:
            execution_id = db.get_document_id_by_field_value("title", execution_name, db.collection_executions)

        # S3
        s3_keys = db.get_all_outputs_s3_keys(execution_id)
        s3M = s3Manager()
        s3M.deletePaths(s3_keys)

        # DB
        db.delete_execution(execution_id)

        # Folders
        if project_path:
            odtp_env.delete_folder(project_path, keep_project_path=keep_project_path)

    except Exception as e:
        msg = f"ERROR: Delete execution failed: {e}"
        log.exception(msg)
        print(msg)
        raise typer.Abort()
    else:
        msg = "SUCCESS: execution has been deleted"
        log.info(msg)
        print(msg)

if __name__ == "__main__":
    app()
