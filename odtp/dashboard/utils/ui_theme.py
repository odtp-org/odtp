import json
from contextlib import contextmanager

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers

PATH_ABOUT = "/"
PATH_USERS = "/users"
PATH_DIGITAL_TWINS = "/digital-twins"
PATH_COMPONENTS = "/components/all"
PATH_WORKFLOWS = "/workflows/all"
PATH_EXECUTIONS = "/executions"

NO_SELECTION_VALUE = "None"
NO_SELECTION_INPUT = None
NO_SELECTION_QUERY = "all"

MISSING_VALUE = "<scan style=color:red>not set</span>"


def menu() -> None:
    ui.link("About", PATH_ABOUT).classes(replace="text-white")
    ui.link("Users", PATH_USERS).classes(replace="text-white")
    ui.link("Components", PATH_COMPONENTS).classes(replace="text-white")
    ui.link("Workflows", PATH_WORKFLOWS).classes(replace="text-white")
    ui.link("Digital Twins", PATH_DIGITAL_TWINS).classes(replace="text-white")
    ui.link("Executions", PATH_EXECUTIONS).classes(replace="text-white")


@contextmanager
def frame():
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(primary="black", secondary="black", accent="black", positive="teal")
    with ui.header().classes("justify-between text-white"):
        ui.label("OTDP").classes("font-bold")
        with ui.row():
            menu()
    yield


def ui_add_first(item_name, page_link, action="select"):
    ui.label(f"You need to {action} {item_name} first").classes("text-lg")
    ui.button(
        f"{action} {item_name}",
        on_click=lambda: ui.open(page_link),
        icon="link",
    )


def ui_no_items_yet(item_name_plural):
    ui.label(
        f"There are no {item_name_plural} yet. Start adding {item_name_plural}"
    ).classes("text-lg")


def ui_execution_display(
    execution_title,
    version_tags,
    ports,
    parameters,
):
    ui.label(f"Execution Title: {execution_title}").classes("text-lg w-full")
    table_columns = [
        {"name": "key", "label": "Parameter type / name", "field": "key"},
        {"name": "value", "label": "value", "field": "value"},
    ]
    if not version_tags:
        return
    with ui.grid(columns=2):
        with ui.column():
            ui.mermaid(helpers.get_workflow_mermaid(version_tags, init="graph TB;"))
        with ui.column():
            for k, version_tag in enumerate(version_tags):
                rows = []
                if ports and ports[k]:
                    for port_mapping in ports[k]:
                        rows.append({"key": "port-mapping", "value": port_mapping})
                if parameters and parameters:
                    for key, value in parameters[k].items():
                        rows.append(
                            {"key": key, "value": value},
                        )
                ui.table(
                    columns=table_columns, rows=rows, row_key="key", title=version_tag
                )


def new_value_selected_in_ui_select(value):
    if not value:
        return False
    if value in ["", "None"]:
        return False
    return True


def ui_version_section_content(version, label, section_key):
    section_content = version.get(section_key)
    if not section_content:
        display_section_empty(label)
    elif isinstance(section_content, dict):
        ui.label(label).classes("text-lg")
        display_section_dict(section_content)
    elif isinstance(section_content, list):
        ui.label(label).classes("text-lg")
        for list_item in section_content:
            display_section_dict(list_item)


def display_section_dict(section_dict):
    with ui.grid(columns='1fr 3fr').classes('w-full gap-0'):
        for key, value in section_dict.items():
            if value == None:
                continue
            ui.label(key).classes('bg-gray-200 border p-1')
            ui.label(str(value)).classes('border p-1')


def display_section_empty(label):
    with ui.grid(columns='1fr 3fr').classes('w-full gap-0'):
        ui.label(label).classes('p-1')
        ui.label("does not apply").classes('p-1')


def display_items_dict_with_links(display_items_list):
    with ui.grid(columns='1fr 3fr').classes('w-full gap-0'):
        for item in display_items_list:
            if not item.display_value:
                continue
            ui.label(item.key).classes('bg-gray-200 border p-1')
            if item.url:
                ui.link(item.display_value, item.url)
            else:
                ui.label(item.display_value).classes('border p-1')
