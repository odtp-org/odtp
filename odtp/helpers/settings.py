from pathlib import Path

from dotenv import dotenv_values

odtp_config_file_path = Path(__file__).parent.parent.parent.joinpath(".env")
odtp_config = dotenv_values(odtp_config_file_path)

ODTP_MONGO_SERVER = odtp_config["ODTP_MONGO_SERVER"]
GITHUB_TOKEN = odtp_config["GITHUB_TOKEN"]
ODTP_MONGO_DB = odtp_config["ODTP_MONGO_DB"]
ODTP_S3_SERVER = odtp_config["ODTP_S3_SERVER"]
ODTP_BUCKET_NAME = odtp_config["ODTP_BUCKET_NAME"]
ODTP_ACCESS_KEY = odtp_config["ODTP_ACCESS_KEY"]
ODTP_SECRET_KEY = odtp_config["ODTP_SECRET_KEY"]
