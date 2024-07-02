"""
This scripts contains odtp subcommands for 'execution'
"""
import sys
import typer
from typing_extensions import Annotated
import logging 

import odtp.mongodb.db as db
import odtp.helpers.parse as odtp_parse
from odtp.workflow import WorkflowManager
from directory_tree import display_tree
import os

app = typer.Typer()

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
        ..., "--project-path", help="Specify the path for the execution"
    ),
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
        step_count = len(execution["workflowSchema"]["workflowExecutorSchema"])
        secrets = [None for i in range(step_count)]
        flowManager = WorkflowManager(execution, project_path, secrets)
        flowManager.prepare_workflow()
    except Exception as e:
        log.error(f"ERROR: Prepare execution failed: {e}") 
        raise typer.Abort()           
    else:
        log.info("SUCCESS: images for the execution have been build")    


@app.command()
def run(
    execution_name: str = typer.Option(
        None, "--execution-name", help="Specify the name of the execution"
    ),
    execution_id: str = typer.Option(
        None, "--execution-id", help="Specify the ID of the execution"
    ),
    project_path: str = typer.Option(
        ..., "--project-path", help="Specify the path for the execution"
    ),
    secrets_files: Annotated[str, typer.Option(
        help="List the files containing the secrets by step separated by commas"
    )] = None, 
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
        step_count = len(execution["workflowSchema"]["workflowExecutorSchema"])
        secrets = odtp_parse.parse_parameters_for_multiple_files(
            parameter_files=secrets_files, step_count=step_count)
        flowManager = WorkflowManager(execution, project_path, secrets)
        flowManager.run_workflow()
    except Exception as e:
        log.error(f"ERROR: Prepare execution failed: {e}")       
        raise typer.Abort()
    else:
        log.info("SUCCESS: containers for the execution have been run")      

@app.command()
def output(

        execution_id: str = typer.Option(
        ..., "--execution-id", help="Specify the ID of the execution"
    ),
    project_path: str = typer.Option(
        ..., "--project-path", help="Specify the path for the execution"
    ),
): 
    try:
        display_tree(project_path)
    except Exception as e:
        print(f"ERROR: Output printing failed: {e}")       
        raise typer.Abort()


@app.command()
def logs(
    project_path: str = typer.Option(
        ..., "--project-path", help="Specify the path for the execution"
    ),
    step_nr: str = typer.Option(
        ..., "--step-nr", help="Specify the step for the execution"
    ),
):
    try:
        log_file_path = f"{project_path}/{step_nr}_*/odtp-logs/*"
        os.system(f"tail -f {log_file_path}")     
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    app()
