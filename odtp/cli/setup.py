"""
This scripts contains odtp subcommands for 'setup'
"""
import typer

from odtp.setup import s3Database
import odtp.mongodb.db as db

app = typer.Typer()


@app.command()
def initiate():
    db.init_collections()

    odtpS3 = s3Database()
    odtpS3.create_folders(["odtp"])
    odtpS3.close()

    print("ODTP DB/S3 data generated")



@app.command()
def delete():
    db.delete_all()

    odtpS3 = s3Database()
    odtpS3.deleteAll()

    print("All deleted")


if __name__ == "__main__":
    app()
