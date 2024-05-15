import os
import logging
from dotenv import load_dotenv

load_dotenv()


class OdtpSettingsException(Exception):
    pass


try:
    ODTP_MONGO_SERVER = os.getenv("ODTP_MONGO_SERVER")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    ODTP_MONGO_DB = os.getenv("ODTP_MONGO_DB")
    ODTP_S3_SERVER = os.getenv("ODTP_S3_SERVER")
    ODTP_BUCKET_NAME = os.getenv("ODTP_BUCKET_NAME")
    ODTP_ACCESS_KEY = os.getenv("ODTP_ACCESS_KEY")
    ODTP_SECRET_KEY = os.getenv("ODTP_SECRET_KEY")
    ODTP_DASHBOARD_PORT = int(os.getenv("ODTP_DASHBOARD_PORT"))
    ODTP_DASHBOARD_RELOAD = eval(os.getenv("ODTP_DASHBOARD_RELOAD", "False"))
    ODTP_DASHBOARD_JSON_EDITOR = eval(os.getenv("ODTP_DASHBOARD_JSON_EDITOR", "False"))
    ODTP_PATH = os.getenv("ODTP_PATH")
except Exception as e:
    raise OdtpSettingsException(f"Configuration of ODTP raised an exception {e}")
