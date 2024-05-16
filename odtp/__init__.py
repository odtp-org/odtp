# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).

import importlib.metadata as importlib_metadata

__version__ = importlib_metadata.version(__name__)

import os
from logging import config as logging_config

here = os.path.abspath(os.path.dirname(__file__))
LOGGING_CONFIG = os.path.abspath(os.path.join(here, 'config.ini'))

logging_config.fileConfig(LOGGING_CONFIG)

#logging.basicConfig(
#    format='ODTP %(asctime)s - [%(module)s:%(levelname)s] %(lineno)d %(filename)s %(funcName)s - %(message)s',
#    datefmt='%d/%m/%Y %I:%M:%S %p',
#    level=logging.ERROR
#)

