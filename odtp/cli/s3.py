"""
This scripts contains odtp subcommands for 's3'
"""
import typer

from odtp.setup import s3Database

app = typer.Typer()

#### TODO: S3 Create

#### TODO: S3 Delete

#### TODO: S3 Check


@app.command()
def download(
    s3_path: str = typer.Option(..., "--s3-path", help="Specify the s3 Path"),
    output_path: str = typer.Option(
        ...,
        "--output-path",
        help="Specify the path to the folder where the file is going to be downloaded",
    ),
):
    odtpS3 = s3Database()
    odtpS3.download_file(s3_path, output_path)
    odtpS3.close()


if __name__ == "__main__":
    app()
