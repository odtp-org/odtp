"""
This scripts contains odtp subcommands for 'execution'
"""
import logging

import typer

import odtp.mongodb.db as db
from odtp.workflow import WorkflowManager

app = typer.Typer()

## Adding listing so we can have multiple flags
from typing import List


@app.command()
def prepare(
    execution_id: str = typer.Option(
        ..., "--execution-id", help="Specify the ID of the execution"
    ),
    project_path: str = typer.Option(
        ..., "--project-path", help="Specify the path for the execution"
    ),
):  
    try:
        execution = db.get_document_by_id(
            document_id=execution_id, 
            collection=db.collection_executions
        )
        flowManager = WorkflowManager(execution, project_path)
        flowManager.prepare_workflow()
    except Exception as e:
        print(f"ERROR: Prepare execution failed: {e}") 
        raise typer.Abort()           
    else:
        print("SUCCESS: images for the execution have been build")    


@app.command()
def run(
    execution_id: str = typer.Option(
        ..., "--execution-id", help="Specify the ID of the execution"
    ),
    project_path: str = typer.Option(
        ..., "--project-path", help="Specify the path for the execution"
    ),
): 
    try:
        execution = db.get_document_by_id(
            document_id=execution_id, 
            collection=db.collection_executions
        )
        flowManager = WorkflowManager(execution, project_path)
        flowManager.run_workflow()
    except Exception as e:
        print(f"ERROR: Run execution failed: {e}")       
        raise typer.Abort()
    else:
        print("SUCCESS: containers for the execution have been run")      


if __name__ == "__main__":
    app()
