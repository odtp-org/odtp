"""
This scripts contains odtp subcommands for 's3'
"""
from pprint import pprint
import logging
import typer

from odtp.storage import s3Manager

app = typer.Typer()


log = logging.getLogger(__name__)


@app.command()
def download(
    s3_path: str = typer.Option(..., "--s3-path", help="Specify the s3 Path"),
    output_path: str = typer.Option(
        ...,
        "--output-path",
        help="Specify the path to the folder where the file is going to be downloaded",
    ),
):
    odtpS3 = s3Manager()
    odtpS3.downloadFile(s3_path, output_path)
    odtpS3.close()


@app.command()
def check():  
    try:
        s3 = s3Manager()
        bucket = s3.test_connection()
        print("S3 is connected. Bucket is ready to use")
    except Exception as e:
        log.exception(f"S3 connection could not be established: an Exception {e} occurred")
        print(f"S3 connection could not be established: an Exception {e} occurred")    


if __name__ == "__main__":
    app()
