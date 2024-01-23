"""
This scripts contains odtp subcommands for 'db'
"""
import typer
from odtp.setup import odtpDatabase


app = typer.Typer()


@app.command()
def get(id: str = typer.Option(
    ...,
    "--id",
    help="Specify the id"
),
        collection: str = typer.Option(
            ...,
            "--collection",
            help="Specify the collection"
        )):
    odtpDB = odtpDatabase()
    out = odtpDB.dbManager.get_document_by_id(id, collection)
    odtpDB.close()

    print(out)


@app.command()
def showAll():
    odtpDB = odtpDatabase()
    out = odtpDB.dbManager.get_all_collections_as_json_string
    odtpDB.close()

    print(out())


@app.command()
def deleteAll():
    odtpDB = odtpDatabase()
    odtpDB.deleteAll()
    odtpDB.close()

    print("All collection deleted.")


if __name__ == "__main__":
    app()
