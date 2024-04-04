import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.info("environment variables loaded")

ODTP_MONGO_SERVER = os.getenv("ODTP_MONGO_SERVER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ODTP_MONGO_DB = os.getenv("ODTP_MONGO_DB")
ODTP_S3_SERVER = os.getenv("ODTP_S3_SERVER")
ODTP_BUCKET_NAME = os.getenv("ODTP_BUCKET_NAME")
ODTP_ACCESS_KEY = os.getenv("ODTP_ACCESS_KEY")
ODTP_SECRET_KEY = os.getenv("ODTP_SECRET_KEY")
