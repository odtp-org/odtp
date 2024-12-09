import logging

from nicegui import app, ui

import odtp.dashboard.page_components.table as table
import odtp.dashboard.page_components.add as add
import odtp.dashboard.page_components.detail as detail

log = logging.getLogger(__name__)


def content() -> None:
    ui_workarea()
    ui_tabs()


@ui.refreshable
def ui_tabs():
    with ui.tabs() as tabs:
        list = ui.tab("Manage Components")
        show_version = ui.tab("Version Detail")
        add_component_version = ui.tab("Add Component Version")
    with ui.tab_panels(tabs, value=list).classes("w-full"):
        with ui.tab_panel(list):
            ui_components_list()
        with ui.tab_panel(show_version):
            ui_version_detail()
        with ui.tab_panel(add_component_version):
            ui_add_component_version()


@ui.refreshable
def ui_components_list():
    table.VersionTable()


@ui.refreshable
def ui_add_component_version():
    with ui.column().classes("w-full"):
        add.ComponentVersionForm()


@ui.refreshable
def ui_version_detail():
    with ui.column().classes("w-full"):
        #detail.VersionDisplay()
        pass


@ui.refreshable
def ui_workarea():
    ui.markdown(
        """
        ## Manage Components
        ODTP Components are the Building blocks for Digital Twins and Executions:

        - Components are not user specific
        - Only tagged Versions of Components can be added

        Learn more at the
        [Documentation of ODTP](https://odtp-org.github.io/odtp-manuals)
        """
    )
