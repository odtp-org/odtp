import logging

from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.page_components.options as options
import odtp.dashboard.page_components.info as info
import odtp.dashboard.page_components.add as add
import odtp.dashboard.page_components.version_table as table
import odtp.dashboard.page_components.add_component_version as add_component_version
import odtp.dashboard.page_components.version_detail as version_detail
import odtp.mongodb.db as db

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
def ui_components_list() -> None:
    try:
        versions = db.get_collection(
            collection=db.collection_versions,
        )
        if not versions:
            ui.label("No components yet").classes("text-red-500")
            return
        table.VersionTable(versions)
    except Exception as e:
        log.exception(
            f"Components table could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_component_select() -> None:
    try:
        current_component = storage.get_active_object_from_storage(
            storage.CURRENT_COMPONENT
        )
        components = db.get_collection(db.collection_components)
        options.ui_select_form(
            current_component=current_component,
            components=components
        )
    except Exception as e:
        log.exception(
            f"Component selection could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_version_add():
    try:
        current_component = storage.get_active_object_from_storage(
            storage.CURRENT_COMPONENT
        )
        options.ui_form_version_add(current_component)
    except Exception as e:
        log.exception(
            f"Component selection could not be loaded. An Exception occurred: {e}"
        )


@ui.refreshable
def ui_add_component_version():
    with ui.column().classes("w-full"):
        add_component_version.ComponentForm()


@ui.refreshable
def ui_version_add():
    with ui.column().classes("w-full"):
        add_version.VersionForm()


@ui.refreshable
def ui_version_detail():
    with ui.column().classes("w-full"):
        version_detail.VersionDisplay()


@ui.refreshable
def ui_component_show():
    try:
        current_component = storage.get_active_object_from_storage(
            storage.CURRENT_COMPONENT
        )
        if not current_component:
            return
        ui_version_add()
        info.ui_component_display(current_component=current_component)
    except Exception as e:
        log.exception(
            f"Component details could not be loaded. An Exception occurred: {e}"
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
