"""
This scripts contains odtp subcommands for 'db'
"""
import typer

from odtp.mongodb.db import odtpDatabase

app = typer.Typer()


@app.command()
def get(
    id: str = typer.Option(..., "--id", help="Specify the id"),
    collection: str = typer.Option(..., "--collection", help="Specify the collection"),
):
    with odtpDatabase() as dbManager:
        out = dbManager.get_document_by_id(id, collection)

    print(out)


@app.command()
def showAll():
    with odtpDatabase() as dbManager:
        out = dbManager.get_all_collections_as_json_string

    print(out())


@app.command()
def deleteAll():
    with odtpDatabase() as dbManager:
        dbManager.deleteAll()

    print("All collection deleted.")


if __name__ == "__main__":
    app()
