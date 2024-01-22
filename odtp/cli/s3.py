# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
"""
This scripts contains odtp subcommands for 's3'
TODO: S3 Create, S3 Delete, S3 Check
"""
import typer
from odtp.setup import s3Database

app = typer.Typer()


@app.command()
def download(
    s3_path: str = typer.Option(..., "--s3-path", help="Specify the s3 Path"),
    output_path: str = typer.Option(
        ...,
        "--output-path",
        help="Specify the path to the folder where the file is going to be downloaded",
    ),
):
    """This commands downloads a file from the S3 database"""
    odtpS3 = s3Database()
    odtpS3.download_file(s3_path, output_path)
    odtpS3.close()


if __name__ == "__main__":
    app()
