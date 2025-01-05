import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
code_file_dir = os.path.abspath(__file__)

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
ODTP_PASSWORD = os.getenv("ODTP_PASSWORD")

ODTP_DASHBOARD_PORT = int(os.getenv("ODTP_DASHBOARD_PORT"))
ALLOW_DOCKER_GPUS = os.getenv("ALLOW_DOCKER_GPUS")
if ALLOW_DOCKER_GPUS in ["False", "True"]:
    ALLOW_DOCKER_GPUS = eval(ALLOW_DOCKER_GPUS)
else:
    ALLOW_DOCKER_GPUS = True

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

ODTP_LOG_LEVEL = os.getenv("ODTP_LOG_LEVEL")
log_levels = logging.getLevelNamesMapping()
if not ODTP_LOG_LEVEL in log_levels.keys():
    ODTP_LOG_LEVEL = DEFAULT_LOG_LEVEL

RUN_LOG_LEVEL = os.getenv("RUN_LOG_LEVEL")
log_levels = logging.getLevelNamesMapping()
if not RUN_LOG_LEVEL in log_levels.keys():
    RUN_LOG_LEVEL = DEFAULT_RUN_LOG_LEVEL

def get_command_log_handler():
    log_file_path = os.path.join(os.path.dirname(os.path.dirname(code_file_dir)), 'odtp.log')
    command_log_handler = logging.FileHandler(log_file_path)
    FORMATTER = logging.Formatter(
        '%(asctime)s - [%(module)s:%(levelname)s] %(lineno)d %(filename)s %(funcName)s - %(message)s'
    )
    command_log_handler.setFormatter(FORMATTER)
    return command_log_handler
