import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.info("environment variables loaded")


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
    ODTP_DASHBOARD_RELOAD = eval(os.getenv("ODTP_DASHBOARD_RELOAD"))
    ODTP_PATH = os.getenv("ODTP_PATH")
    ODTP_AUTHENTICATION = os.getenv("ODTP_AUTHENTICATION") == "True"
    ODTP_KEYCLOAK_LOGOUT = os.getenv("ODTP_KEYCLOAK_LOGOUT")
    ODTP_KEYCLOAK_URL = os.getenv("ODTP_KEYCLOAK_URL")
    ODTP_KEYCLOAK_AUDIENCE = os.getenv("ODTP_KEYCLOAK_AUDIENCE")
    ODTP_KEYCLOAK_REDIRECT = os.getenv("ODTP_KEYCLOAK_REDIRECT")
except Exception as e:
    raise OdtpSettingsException(f"Configuration of ODTP raised an exception {e}")
