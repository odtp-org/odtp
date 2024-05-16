import json
from contextlib import contextmanager

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.helpers.utils as odtp_utils
import odtp.mongodb.db as db


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
    ui.link("Components", PATH_COMPONENTS).classes(replace="text-white")
    ui.link("Digital Twins", PATH_DIGITAL_TWINS).classes(replace="text-white")
    ui.link("Executions", PATH_EXECUTIONS).classes(replace="text-white")


@contextmanager
def frame(navtitle: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(
        primary="black", secondary="black", accent="black", positive="teal"
    )
    with ui.header().classes("justify-between text-white"):
        ui.label("OTDP").classes("font-bold")
        with ui.row():
            menu()
    yield


def ui_add_first(item_name, page_link, action="select"):
        ui.label(f"You need to {action} {item_name} first").classes('text-lg')
        ui.button(
            f"{action} {item_name}",
            on_click=lambda: ui.open(page_link),
            icon="link",
        )


def ui_no_items_yet(item_name_plural):
    ui.label(f"There are no {item_name_plural} yet. Start adding {item_name_plural}").classes('text-lg')


def ui_execution_display(
    execution_title,
    version_tags,
    ports,
    parameters,
):
    ui.label(f"Execution Title: {execution_title}").classes("text-lg w-full")
    table_columns = [
        {'name': 'key', 'label': 'Parameter type / name', 'field': 'key'},
        {'name': 'value', 'label': 'value', 'field': 'value'},
    ]    
    if not version_tags:
        return  
    with ui.grid(columns=2):
        with ui.column():    
            ui.mermaid(
                helpers.get_workflow_mermaid(version_tags, init='graph TB;')
            )
        with ui.column(): 
            for k, version_tag in enumerate(version_tags):
                rows = []
                if ports and ports[k]:    
                    for port_mapping in ports[k]:
                        rows.append({'key': 'port-mapping', 'value': port_mapping})
                if parameters and parameters:
                    for key, value in parameters[k].items():
                        rows.append({'key': key, 'value': value},)
                ui.table(columns=table_columns, rows=rows, row_key='key', title=version_tag)


def new_value_selected_in_ui_select(value):
    if not value: 
        return False
    if value in ["", "None"]:
        return False
    return True
