"""
This scripts contains odtp subcommands for 'setup'
"""
import typer

from odtp.setup import odtpDatabase, s3Database

app = typer.Typer()


@app.command()
def initiate():
    odtpDB = odtpDatabase()
    odtpDB.run_initial_setup()

    # Save all collections as JSON
    odtpDB.dbManager.export_all_collections_as_json("odtpDB.json")

    odtpS3 = s3Database()
    odtpS3.create_folders(["odtp"])

    odtpDB.close()
    odtpS3.close()

    print("ODTP DB/S3 and Mockup data generated")


@app.command()
def delete():
    odtpDB = odtpDatabase()
    odtpDB.deleteAll()

    odtpS3 = s3Database()
    odtpS3.deleteAll()

    print("All deleted")


if __name__ == "__main__":
    app()
