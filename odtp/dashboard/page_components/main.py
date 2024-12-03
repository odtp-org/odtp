import logging

from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.page_components.options as options
import odtp.dashboard.page_components.info as info
import odtp.dashboard.page_components.add as add
import odtp.mongodb.db as db

log = logging.getLogger(__name__)


def content() -> None:
    ui_workarea()
    ui_tabs()


@ui.refreshable
def ui_tabs():
    with ui.tabs() as tabs:
        list = ui.tab("Registered Components")
        select = ui.tab("Component options")
        add_component = ui.tab("Add Component")
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(select):
            ui_component_select()
            ui_component_show()
        with ui.tab_panel(add_component):
            ui_component_add()
        with ui.tab_panel(list):
            ui_components_list()


@ui.refreshable
def ui_components_list() -> None:
    try:
        versions = db.get_collection(
            collection=db.collection_versions,
        )
        info.ui_component_table(versions)
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
def ui_component_add():
    with ui.column().classes("w-full"):
        new_component_to_add = storage.get_active_object_from_storage(
            storage.NEW_COMPONENT
        )
        if not new_component_to_add:
            add.ui_form_component_add_step1()
        else:
            add.ui_form_component_add_step2(new_component_to_add)


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
