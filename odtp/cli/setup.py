# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
"""
This scripts contains odtp subcommands for 'setup'
"""
import typer
import json
from odtp.setup import mongoDatabase, s3Database

app = typer.Typer()


@app.command()
def initiate():
    """initial setup of the Mongo DB and S3"""
    odtpDB = mongoDatabase()
    odtpDB.run_initial_setup()

    # Save all collections as JSON
    all_data_as_json = odtpDB.dbManager.get_all_collections(as_json=True)
    with open("odtpDB.json", 'w') as json_file:
        print(all_data_as_json)

    odtpS3 = s3Database()
    odtpS3.create_folders(["odtp"])

    odtpDB.close()
    odtpS3.close()

    print("ODTP DB/S3 and Mockup data generated")


@app.command()
def delete():
    """delete Mongo DB and S3"""
    odtpDB = odtpDatabase()
    odtpDB.deleteAll()

    odtpS3 = s3Database()
    odtpS3.deleteAll()

    print("All deleted")


if __name__ == "__main__":
    app()
