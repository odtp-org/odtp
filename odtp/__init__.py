# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).

import logging
import importlib.metadata as importlib_metadata
from odtp.helpers.settings import ODTP_LOG_LEVEL


__version__ = importlib_metadata.version(__name__)

logging.basicConfig(
    format='%(asctime)s - [%(module)s:%(levelname)s] %(lineno)d %(filename)s %(funcName)s - %(message)s',
    datefmt='%d/%m/%Y %I:%M:%S %p',
    level=logging.ERROR
)

valid_log_levels = logging.getLevelNamesMapping()

if ODTP_LOG_LEVEL in valid_log_levels.keys():
    logging.getLogger().setLevel(ODTP_LOG_LEVEL)
