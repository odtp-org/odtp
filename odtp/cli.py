# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).

"""Command line interface to the odpt package."""
from enum import Enum
from typing import List, Optional

import click
import typer

from odtp import __version__

app = typer.Typer(add_completion=False)
db = typer.Typer()
s3 = typer.Typer()
run = typer.Typer()
log = typer.Typer()

app.add_typer(db, name="db")
app.add_typer(s3, name="s3")
app.add_typer(run, name="run")
app.add_typer(log, name="log")

# Used to autogenerate docs with sphinx-click
@click.group()
def cli():
    """Command line group"""
    pass

def version_callback(value: bool):
    if value:
        print(f"odtp {__version__}")
        # Exits successfully
        raise typer.Exit()
    



typer_cli = typer.main.get_command(app)
cli.add_command(typer_cli, "cli")

### MongoDB Commands
@db.command()
def createSchema(
                url: str = typer.Option(
                    ...,
                    "--mongodb-url",
                    help="Specify the url to your mongo database including the port"
                )):
    
    # Execute DB initiateDB
    pass

@db.command()
def deleteSchema(
                url: str = typer.Option(
                    ...,
                    "--mongodb-url",
                    help="Specify the url to your mongo database including the port"
                )):
    
    # Execute DB initiateDB
    pass

@db.command()
def checkSchema(
                url: str = typer.Option(
                    ...,
                    "--mongodb-url",
                    help="Specify the url to your mongo database including the port"
                )):
    
    # Execute DB initiateDB
    pass


#### TODO: S3 Create

#### TODO: S3 Delete

#### TODO: S3 Check


#### TODO: Run Component

#### TODO: Stop Component

#### TODO: Print Logs

# This callback is triggered when odtp is called without subcommand
@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback
    )
):
    """odtp runs and organize digital twins."""
    

if __name__ == "__main__":
    app()