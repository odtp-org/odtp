"""
This scripts contains odtp subcommands for 'dashboard'
"""
import os
import sys

import streamlit.web.cli as stcli
import subprocess
import typer

app = typer.Typer()


@app.command()
def streamlit(port: str = typer.Option(..., "--port", help="Specify the port")):
    # Execute Strealit
    os.chdir("odtp")
    sys.argv = ["streamlit", "run", "gui/app.py", "--server.port", port]
    sys.exit(stcli.main())


@app.command()
def nicegui():
    # Execute Nicegui
    subprocess.run(["python", "odtp/dashboard/main.py"])


if __name__ == "__main__":
    app()
