# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).

"""Command line interface to the odpt package."""
import click
import typer
from typing import Optional
from odtp.cli import db, new, component, dashboard, execution, s3, setup
from odtp import __version__

app = typer.Typer(add_completion=False)

app.add_typer(new.app, name="new")
app.add_typer(db.app, name="db")
app.add_typer(s3.app, name="s3")
app.add_typer(component.app, name="component")
app.add_typer(setup.app, name="setup")
app.add_typer(dashboard.app, name="dashboard")
app.add_typer(execution.app, name="execution")


@click.group()
def cli():
    """Command line group"""
    pass


def version_callback(value: bool):
    """get version of odtp"""
    if value:
        print(f"odtp {__version__}")
        # Exits successfully
        raise typer.Exit()


typer_cli = typer.main.get_command(app)
cli.add_command(typer_cli, "cli")


# This callback is triggered when odtp is called without subcommand
@app.callback()
def callback(
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback)
):
    """odtp runs and organize digital twins."""
    pass

if __name__ == "__main__":
    app()
