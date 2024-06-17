"""
This scripts contains odtp subcommands for 'setup'
"""
import typer

from odtp.storage import s3Manager
import odtp.mongodb.db as db

app = typer.Typer()


@app.command()
def initiate():
    db.init_collections()

    odtpS3 = s3Manager()
    odtpS3.create_folders(["odtp"])
    odtpS3.close()

    print("ODTP DB/S3 data generated")


@app.command()
def delete():
    db.delete_all()

    odtpS3 = s3Manager()
    odtpS3.deleteAll()

    print("All deleted")


if __name__ == "__main__":
    app()
