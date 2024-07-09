import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = "ERROR"
DEFAULT_RUN_LOG_LEVEL = "INFO"

class OdtpSettingsException(Exception):
    pass


ODTP_MONGO_SERVER = os.getenv("ODTP_MONGO_SERVER")
ODTP_MONGO_DB = os.getenv("ODTP_MONGO_DB")

ODTP_S3_SERVER = os.getenv("ODTP_S3_SERVER")
ODTP_BUCKET_NAME = os.getenv("ODTP_BUCKET_NAME")
ODTP_ACCESS_KEY = os.getenv("ODTP_ACCESS_KEY")
ODTP_SECRET_KEY = os.getenv("ODTP_SECRET_KEY")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

ODTP_DASHBOARD_PORT = int(os.getenv("ODTP_DASHBOARD_PORT"))


ODTP_DASHBOARD_RELOAD = os.getenv("ODTP_DASHBOARD_RELOAD")
if ODTP_DASHBOARD_RELOAD in ["False", "True"]:
    ODTP_DASHBOARD_RELOAD = eval(ODTP_DASHBOARD_RELOAD)
else:
    ODTP_DASHBOARD_RELOAD = False

ODTP_DASHBOARD_JSON_EDITOR = os.getenv("ODTP_DASHBOARD_JSON_EDITOR")
if ODTP_DASHBOARD_JSON_EDITOR in ["False", "True"]:
    ODTP_DASHBOARD_JSON_EDITOR = eval(ODTP_DASHBOARD_JSON_EDITOR)
else:
    ODTP_DASHBOARD_JSON_EDITOR = False

ODTP_PATH = os.getenv("ODTP_PATH")

ODTP_AUTHENTICATION = os.getenv("ODTP_AUTHENTICATION")
if ODTP_AUTHENTICATION in ["False", "True"]:
    ODTP_AUTHENTICATION = eval(ODTP_AUTHENTICATION)
else:
    ODTP_AUTHENTICATION = False

ODTP_KEYCLOAK_LOGOUT = os.getenv("ODTP_KEYCLOAK_LOGOUT")
ODTP_KEYCLOAK_URL = os.getenv("ODTP_KEYCLOAK_URL")
ODTP_KEYCLOAK_AUDIENCE = os.getenv("ODTP_KEYCLOAK_AUDIENCE")
ODTP_KEYCLOAK_REDIRECT = os.getenv("ODTP_KEYCLOAK_REDIRECT")

ODTP_LOG_LEVEL = os.getenv("ODTP_LOG_LEVEL")
log_levels = logging.getLevelNamesMapping()
if not ODTP_LOG_LEVEL in log_levels.keys():
    ODTP_LOG_LEVEL = DEFAULT_LOG_LEVEL

RUN_LOG_LEVEL = os.getenv("RUN_LOG_LEVEL")
log_levels = logging.getLevelNamesMapping()
if not RUN_LOG_LEVEL in log_levels.keys():
    RUN_LOG_LEVEL = DEFAULT_RUN_LOG_LEVEL
