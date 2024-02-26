import json
from contextlib import contextmanager

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.helpers.utils as odtp_utils

PATH_ABOUT = "/"
PATH_USERS = "/users"
PATH_DIGITAL_TWINS = "/digital-twins"
PATH_COMPONENTS = "/components"
PATH_EXECUTIONS = "/executions"
PATH_RUN = "/run"

NO_SELECTION_VALUE = "None"
NO_SELECTION_INPUT = None

def menu() -> None:
    ui.link("About", PATH_ABOUT).classes(replace="text-white")
    ui.link("Users", PATH_USERS).classes(replace="text-white")
    ui.link("Digital Twins", PATH_DIGITAL_TWINS).classes(replace="text-white")
    ui.link("Components", PATH_COMPONENTS).classes(replace="text-white")
    ui.link("Executions", PATH_EXECUTIONS).classes(replace="text-white")
    ui.link("Run", PATH_RUN).classes(replace="text-white")


@contextmanager
def frame(navtitle: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(
        primary="#009485", secondary="#009485", accent="#009485", positive="#009485"
    )
    with ui.header().classes("justify-between text-white"):
        ui.label("OTDP").classes("font-bold")
        with ui.row():
            menu()
    yield


def ui_add_first(item_name, page_link):
        ui.label(f"You need to select a {item_name} first").classes('text-lg')
        ui.button(
            f"Select {item_name}",
            on_click=lambda: ui.open(page_link),
            icon="link",
        )


def ui_no_items_yet(item_name_plural):
    ui.label(f"There are no {item_name_plural} yet. Start adding {item_name_plural}").classes('text-lg')
