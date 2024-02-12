import json

import pandas as pd
from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db


def content() -> None:
    with ui.right_drawer(fixed=False).style("background-color: #ebf1fa").props(
        "bordered"
    ) as right_drawer:
        ui_workarea()
    ui.markdown(
        """
                ## Manage Components
                """
    )
    with ui.tabs().classes("w-full") as tabs:
        select = ui.tab("Select a component")
        add = ui.tab("Add a new component")
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(select):
            ui_components_select()
            ui_version_select()
        with ui.tab_panel(add):
            ui_component_register()


@ui.refreshable
def ui_components_select() -> None:
    ui.markdown(
        """
                #### Select a component
                Select a component to see the versions of this component.
                """
    )
    try:
        components = db.get_collection(db.collection_components)
        components_options = {
            str(
                component["_id"]
            ): f"{component.get('componentName')}: ({component.get('repoLink')})"
            for component in components
        }
        if components:
            component_select = ui.select(
                components_options,
                on_change=lambda e: store_selected_component(str(e.value)),
                label="component",
                with_input=True,
            ).props("size=120")
    except Exception as e:
        ui.notify(
            f"Component selection could not be loaded. An Exception occured: {e}",
            type="negative",
        )


@ui.refreshable
def ui_version_select() -> None:
    try:
        current_component = storage.get_active_object_from_storage("component")
        if current_component:
            component_id = current_component.get("component_id")
            ui.markdown(
                """
                        #### Select a versions for the component
                        """
            )
            versions = db.get_sub_collection_items(
                collection=db.collection_components,
                sub_collection=db.collection_versions,
                item_id=component_id,
                ref_name=db.collection_versions,
            )
            if versions:
                version_options = {
                    str(
                        version["_id"]
                    ): f"component-version: {version['component_version']} odtp-version: {version['odtp_version']} commit: {version.get('commitHash')}"
                    for version in versions
                }
                version_select = ui.select(
                    version_options,
                    label="version",
                    with_input=True,
                ).props("size=120")
                ui.label("add or replace selection of version for component")
                with ui.row():
                    ui.button(
                        "Add",
                        on_click=lambda: add_selected_component_version(
                            component_id=component_id,
                            version_id=version_select.value,
                            replace=False,
                        ),
                    )
                    ui.button(
                        "Replace",
                        on_click=lambda: add_selected_component_version(
                            component_id=component_id,
                            version_id=version_select.value,
                            replace=True,
                        ),
                    )
    except Exception as e:
        ui.notify(
            f"Version selection could not be loaded. An Exception occured: {e}",
            type="negative",
        )


@ui.refreshable
def ui_component_register():
    with ui.column().classes("w-full"):
        ui.markdown(
            """
                    #### Component
                    """
        )
        component_name_input = ui.input(
            label="Component name",
            placeholder="component name",
            validation={
                "File not valid": lambda value: lambda value: len(value.strip()) >= 4
            },
        ).classes("w-2/3")
        repo_link_input = ui.input(
            label="Repository URL",
            placeholder="repo url",
            validation={
                "repo url not valid": lambda value: lambda value: len(value.strip())
                >= 4
            },
        ).classes("w-2/3")
        ui.markdown(
            """
                    #### Version
                    """
        )
        component_version_input = ui.input(
            label="Component version",
            placeholder="component version",
            validation={
                "version number not valid": lambda value: lambda value: len(
                    value.strip()
                )
                >= 4
            },
        ).classes("w-1/3")
        odtp_version_input = ui.input(
            label="ODTP version",
            placeholder="ODTP version",
            validation={
                "version number not valid": lambda value: lambda value: len(
                    value.strip()
                )
                >= 4
            },
        ).classes("w-1/3")
        commit_hash_input = ui.input(
            label="Commit hash",
            placeholder="commit",
            validation={
                "commit not valid": lambda value: lambda value: len(value.strip()) >= 4
            },
        ).classes("w-2/3")
        ui.button(
            "Register component",
            on_click=lambda: register_component(
                component_name=component_name_input.value,
                odtp_version=odtp_version_input.value,
                component_version=component_version_input.value,
                repo_link=repo_link_input.value,
                commit_hash=commit_hash_input.value,
            ),
        )


@ui.refreshable
def ui_workarea():
    ui.markdown(
        """
                #### Component Versions
                """
    )
    try:
        components = storage.get_active_object_from_storage("components")
        if storage.app_storage_is_set("components"):
            for component in components:
                version = component.get("version")
                if component and version:
                    component_version_output = f"""
                        **{component.get('name')}**:  
                        {version.get('odtp_version')} {version.get('component_version')} 
                        """
                    ui.markdown(component_version_output)
            if storage.get_active_object_from_storage("digital_twin"):
                ui.button(
                    "Build Executions",
                    on_click=lambda: ui.open(ui_theme.PATH_EXECUTIONS),
                )
        ui.button("Reset work area", on_click=lambda: app_storage_reset())
    except Exception as e:
        ui.notify(
            f"Workarea could not be loaded. An Exception occured: {e}", type="negative"
        )


def store_selected_component(value):
    try:
        storage.storage_update_component(component_id=value)
    except Exception as e:
        ui.notify(
            f"Selected component could not be stored. An Exception occured: {e}",
            type="negative",
        )
    finally:
        ui_workarea.refresh()
        ui_version_select.refresh()


def add_selected_component_version(component_id, version_id, replace):
    try:
        storage.storage_update_version(
            component_id=component_id, version_id=version_id, replace=replace
        )
    except Exception as e:
        ui.notify(
            f"Selected component version could not be stored. An Exception occured: {e}",
            type="negative",
        )
    finally:
        ui_workarea.refresh()
        ui_version_select.refresh()
        ui_components_select.refresh()


def register_component(
    repo_link,
    component_name,
    odtp_version,
    component_version,
    commit_hash,
):
    try:
        component_id, version_id = db.add_component_version(
            component_name=component_name,
            repository=repo_link,
            odtp_version=odtp_version,
            component_version=component_version,
            commit_hash=commit_hash,
        )
        ui.notify(f"Component version {component_id} / {version_id} has been added")
    except Exception as e:
        ui.notify(
            f"The component and version could not be added. An Exception occured: {e}",
            type="negative",
        )
    finally:
        ui_component_register.refresh()
        ui_components_select.refresh()
        ui_version_select.refresh()


def app_storage_reset():
    try:
        storage.app_storage_reset("components")
    except Exception as e:
        ui.notify(
            f"Work area could not be reset. An Exception occured: {e}", type="negative"
        )
    finally:
        ui_workarea.refresh()
