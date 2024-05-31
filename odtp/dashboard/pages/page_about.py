import logging

from nicegui import ui

import odtp.dashboard.utils.storage as storage
from odtp.dashboard.ui_elements.homepage import ui_homepage


logger = logging.getLogger(__name__)


def content() -> None:
    storage.reset_storage_keep([])
    logger.info("nicegui storage cleared")
    ui_homepage()
