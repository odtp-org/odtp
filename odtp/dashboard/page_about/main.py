import logging

from nicegui import ui

import odtp.dashboard.utils.storage as storage
from odtp.dashboard.page_about.homepage import ui_homepage


log = logging.getLogger(__name__)


def content() -> None:
    try:
        storage.reset_storage_keep([])
        ui_homepage()
    except Exception as e:    
        log.exception(f"User selection could not be loaded. An Exception occurred: {e}")
