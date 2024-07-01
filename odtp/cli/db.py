"""
This scripts contains odtp subcommands for 'db'
"""
import typer
from typing_extensions import Annotated

import odtp.mongodb.db as db
import odtp.helpers.utils as odtp_utils

app = typer.Typer()


@app.command()
def get(
    collection: str = typer.Argument(...,help="Specify the collection"),
    id: Annotated[str, typer.Option(help="Specify the id")] = None,
):
    if id:
        db_output = db.get_document_by_id(document_id=id, collection=collection)
    else:
        db_output = db.get_collection(collection=collection)
    odtp_utils.print_output_as_json(db_output)

@app.command()
def ls(collection_name: str):
    """List all documents in a collection"""
    db_output = db.get_collection(collection=collection_name)
    odtp_utils.output_as_pretty_table(db_output, collection_name)

@app.command()
def showAll():
    """show all content of the Mongo DB"""
    db_output = db.get_all_collections()
    odtp_utils.print_output_as_json(db_output)


@app.command()
def digitalTwins_for_user(
    user_id: str = typer.Option(..., "--user-id", help="Specify the user_id"),
):
    db_output = db.get_sub_collection_items(
        collection=db.collection_users,
        sub_collection=db.collection_digital_twins,
        item_id=user_id,
        ref_name=db.collection_digital_twins,
    )
    odtp_utils.print_output_as_json(db_output)


@app.command()
def executions_for_digitalTwin(
    dt_id: str = typer.Option(..., "--dt-id", help="Specify the digital_twin_id"),
):
    db_output = db.get_sub_collection_items(
        collection=db.collection_digital_twins,
        sub_collection=db.collection_executions,
        item_id=dt_id,
        ref_name=db.collection_executions,
    )
    odtp_utils.print_output_as_json(db_output)


@app.command()
def steps_for_execution(
    execution_id: Annotated[
        str, typer.Option("--execution-id", help="Specify the execution_id")
    ],
):
    db_output = db.get_sub_collection_items(
        collection=db.collection_executions,
        sub_collection=db.collection_steps,
        item_id=execution_id,
        ref_name=db.collection_steps,
    )
    odtp_utils.print_output_as_json(db_output)


@app.command()
def delete_document(
    collection: str = typer.Option(..., "--collection", help="Specify the collection"),
    id: str = typer.Option(help="Specify the id")
):
    db.delete_document_by_id(document_id=id, collection=collection)
    print(f"Document with ID {id} was deleted")


@app.command()
def delete_collection(
    collection: str = typer.Option(..., "--collection", help="Specify the collection"),
):
    db.delete_collection(collection=collection)
    print(f"Collection {collection} was deleted.")


@app.command()
def deleteAll():
    db.delete_all()
    print("All collection deleted.")


if __name__ == "__main__":
    app()
