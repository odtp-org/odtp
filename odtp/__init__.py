# odtp
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).

import logging
import importlib.metadata as importlib_metadata

__version__ = importlib_metadata.version(__name__)
logging.basicConfig(format='%(levelname)s (%(asctime)s): %(message)s (LineL %(lineno)d [%(filename)s])',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.DEBUG)
