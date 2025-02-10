import logging

from nicegui import ui
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.page_components.table as table
import odtp.dashboard.page_components.add as add
import odtp.dashboard.page_components.detail as detail

log = logging.getLogger(__name__)


def content(version_id=all):
    ui_workarea()
    if version_id == ui_theme.NO_SELECTION_QUERY:
       version_id = ui_theme.NO_SELECTION_INPUT
    ui_tabs(version_id)


@ui.refreshable
def ui_tabs(version_id):
    with ui.tabs() as tabs:
        list = ui.tab("Manage Components")
        show_version = ui.tab("Component Version Detail")
        add_component_version = ui.tab("Add Component Version")
    with ui.tab_panels(tabs, value=show_version).classes("w-full"):
        with ui.tab_panel(list):
            ui_components_list()
        with ui.tab_panel(show_version):
            ui_version_detail(version_id)
        with ui.tab_panel(add_component_version):
            ui_add_component_version()


@ui.refreshable
def ui_components_list():
    try:
        table.VersionTable()
    except Exception as e:
        log.exception(
            f"Component Version table could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_add_component_version():
    try:
        add.ComponentVersionForm()
    except Exception as e:
        log.exception(
            f"Component Version Add Form could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_version_detail(version_id):
    try:
        detail.VersionDisplay(version_id)
    except Exception as e:
        log.exception(
            f"Component Version Detail could not be loaded. An Exception occurred: {e}"
        )

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
