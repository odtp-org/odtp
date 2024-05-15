import json
from contextlib import contextmanager

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.helpers.utils as odtp_utils

PATH_ABOUT = "/" 
PATH_USERS = "/users"
PATH_SIGN = "/logout"
PATH_DIGITAL_TWINS = "/digital-twins"
PATH_COMPONENTS = "/components" 
PATH_EXECUTIONS = "/executions"
PATH_RUN = "/run"

NO_SELECTION_VALUE = "None"
NO_SELECTION_INPUT = None

def menu() -> None:
    current_user = storage.get_active_object_from_storage(
        storage.AUTH_USER_SUB
    )
    user = current_user.get("name")
    print(f"current_user {user}") 
    
    ui.link("About", PATH_ABOUT).classes(replace="text-white")
    ui.link(user, PATH_USERS).classes(replace="text-white")
    ui.link("Executions", PATH_EXECUTIONS).classes(replace="text-white")
    ui.link("Run", PATH_RUN).classes(replace="text-white")
    ui.button(user, on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/logout')),icon='logout')
    

@contextmanager
def frame(navtitle: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(
        primary="black", secondary="black", accent="black", positive="black"
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
