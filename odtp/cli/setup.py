"""
This scripts contains odtp subcommands for 'setup'
"""
import typer
import logging
from odtp.storage import s3Manager
import odtp.mongodb.db as db

app = typer.Typer()

log = logging.getLogger(__name__)

@app.command()
def initiate():
    db.init_collections()

    odtpS3 = s3Manager()
    try:
        bucketAvailable = odtpS3.test_connection()
    except Exception as e:
        logging.error("S3 bucket not found. Please create the bucket on minio folder or use the dashboard.")
        log.exception(e)


    odtpS3.createFolderStructure(["odtp"])
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
