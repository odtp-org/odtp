# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
"""
This scripts contains odtp subcommands for 'dashbooard'
"""
import typer
import sys
import os
import streamlit.web.cli as stcli

app = typer.Typer()


@app.command()
def run(port: str = typer.Option(..., "--port", help="Specify the port")):
    """run gui"""
    os.chdir("odtp")
    sys.argv = ["streamlit", "run", "gui/app.py", "--server.port", port]
    sys.exit(stcli.main())


if __name__ == "__main__":
    app()
