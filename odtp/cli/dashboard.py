"""
This scripts contains odtp subcommands for 'dashboard'
"""
import os
import sys

import streamlit.web.cli as stcli
import typer

app = typer.Typer()


@app.command()
def run(port: str = typer.Option(..., "--port", help="Specify the port")):
    # Execute Strealit
    os.chdir("odtp")
    sys.argv = ["streamlit", "run", "gui/app.py", "--server.port", port]
    sys.exit(stcli.main())


if __name__ == "__main__":
    app()
