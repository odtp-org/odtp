# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).

"""Command line interface to the odpt package."""
from enum import Enum
from typing import List, Optional

import click
import typer

## ODTP METHODS
from .initial_setup import odtpDatabase, s3Database

#from odtp import __version__

app = typer.Typer(add_completion=False)
db = typer.Typer()
s3 = typer.Typer()
run = typer.Typer()
log = typer.Typer()
setup = typer.Typer()
dashboard = typer.Typer()

app.add_typer(db, name="db")
app.add_typer(s3, name="s3")
app.add_typer(run, name="run")
app.add_typer(log, name="log")
app.add_typer(setup, name="setup")
app.add_typer(dashboard, name="dashboard")

# Used to autogenerate docs with sphinx-click
@click.group()
def cli():
    """Command line group"""
    pass

def version_callback(value: bool):
    if value:
        # TODO: Fix
        print(f"odtp {__version__}")
        # Exits successfully
        raise typer.Exit()
    



typer_cli = typer.main.get_command(app)
cli.add_command(typer_cli, "cli")

### Setup Commands
###############################################################

@setup.command()
def initiate():
    odtpDB = odtpDatabase()
    odtpDB.run_initial_setup()

    # Save all collections as JSON
    odtpDB.dbManager.export_all_collections_as_json('odtpDB.json')

    odtpS3 = s3Database()
    odtpS3.create_folders(["odtp"])


    odtpDB.close()
    odtpS3.close()

    print("ODTP DB/S3 and Mockup data generated")

@setup.command()
def delete():
    odtpDB = odtpDatabase()
    odtpDB.deleteAll()

    odtpS3 = s3Database()
    odtpS3.deleteAll()

    print("All deleted")


### MongoDB Commands
###############################################################

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

# S3
###############################################################


#### TODO: S3 Create

#### TODO: S3 Delete

#### TODO: S3 Check

# Running
###############################################################

#### TODO: Run Component

#### TODO: Stop Component

#### TODO: Print Logs

# GUI
###############################################################
import streamlit.web.cli as stcli
import sys
import os 

@dashboard.command()
def run(port: str = typer.Option(
                    ...,
                    "--port",
                    help="Specify the port"
                )):
    
    # Execute Strealit
    os.chdir("odtp")
    sys.argv = ["streamlit", "run", "gui/app.py", "--server.port", port]
    sys.exit(stcli.main())

    #stcli.run('gui/app.py', port)


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