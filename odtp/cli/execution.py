# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
"""
This scripts contains odtp subcommands for 'execution'
"""
import typer
from odtp.setup import odtpDatabase

app = typer.Typer()
# Running Workflow Executions
###############################################################


@app.command()
def prepare(
    execution_id: str = typer.Option(
        ..., "--execution-id", help="Specify the ID of the execution"
    ),
    project_path: str = typer.Option(
        ..., "--project-path", help="Specify the path for the execution"
    ),
):
    odtpDB = odtpDatabase()
    execution_doc = odtpDB.dbManager.get_document_by_id_as_dict(
        execution_id, "executions"
    )
    odtpDB.close()

    flowManager = WorkflowManager(execution_doc, project_path)
    flowManager.prepare_workflow()


@app.command()
def run(
    execution_id: str = typer.Option(
        ..., "--execution-id", help="Specify the ID of the execution"
    ),
    project_path: str = typer.Option(
        ..., "--project-path", help="Specify the path for the execution"
    ),
    env_files: str = typer.Option(
        ...,
        "--env-files",
        help="Specify the path for the env files separated by commas.",
    ),
):
    odtpDB = odtpDatabase()
    execution_doc = odtpDB.dbManager.get_document_by_id_as_dict(
        execution_id, "executions"
    )
    odtpDB.close()

    env_files = env_files.split(",")
    logging.info(env_files)

    flowManager = WorkflowManager(execution_doc, project_path)
    flowManager.run_workflow(env_files)
