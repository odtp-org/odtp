# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
"""
This scripts contains odtp subcommands for 'db'
"""
import typer
from odtp.mongodb.db import odtpDatabase

app = typer.Typer()

@app.command()
def showAll():
    """show all content of the Mongo DB"""
    with odtpDatabase() as dbManager:
        out = dbManager.get_all_collections(as_json=True)
    print(out)


@app.command()
def get(
    id: str = typer.Option(..., "--id", help="Specify the id"),
    collection: str = typer.Option(..., "--collection", help="Specify the collection"),
):
    """get a collection from the mongo db"""
    with odtpDatabase() as dbManager:
        out = dbManager.get_document_by_id(id, collection)
    print(out)


@app.command()
def getcollection(
    collection: str = typer.Option(..., "--collection", help="Specify the collection"),
):
    """get a collection from the mongo db"""
    with odtpDatabase() as dbManager:
        out = dbManager.get_all_documents(collection)
    print(out)


@app.command()
def getdigitaltwin(
    id: str = typer.Option(..., "--userid", help="Specify the id"),
):
    """get a collection from the mongo db"""
    with odtpDatabase() as dbManager:
        out = dbManager.get_digital_twins_by_user_id(id)
    print(out)



@app.command()
def deleteAll():
    """delete all content in the db"""
    with odtpDatabase() as dbManager:
        dbManager.deleteAll()
    print("All collection deleted.")


if __name__ == "__main__":
    app()
