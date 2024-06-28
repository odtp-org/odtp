"""
This scripts contains odtp subcommands for 'setup'
"""
import typer
import logging
from odtp.storage import s3Manager
import odtp.mongodb.db as db
import odtp.helpers.filesystem as odtp_filesystem

app = typer.Typer()

log = logging.getLogger(__name__)

@app.command()
def initiate():
    db.init_collections()

    odtpS3 = s3Manager()
    try:
        odtpS3.test_connection()
    except Exception as e:
        log.error("S3 bucket not found. Please create the bucket on minio folder or use the dashboard.")
        log.exception(e)


    odtpS3.createFolderStructure(["odtp"])
    odtpS3.close()

    odtp_filesystem.create_folders(["users"])

    print("ODTP DB/S3 data generated")


@app.command()
def delete():
    db.delete_all()

    odtpS3 = s3Manager()
    odtpS3.deleteAll()

    odtp_filesystem.delete_folders(["odtp"])

    print("All deleted")


if __name__ == "__main__":
    app()
