import pandas as pd
from nicegui import ui

import odtp.dashboard.utils.parse as parse
import odtp.dashboard.utils.storage as storage
import odtp.helpers.git as otdp_git
import odtp.helpers.utils as odtp_utils
import odtp.mongodb.db as db
import odtp.mongodb.utils as db_utils


def content() -> None:
    ui.markdown(
        """
        ## Manage Components
        """
    )
    with ui.right_drawer().style("background-color: #ebf1fa").props(
        "bordered width=500"
    ) as right_drawer:
        ui_workarea()
    with ui.tabs() as tabs:
        select = ui.tab("Select a component")
        add_component = ui.tab("Add a new component")
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(select):
            ui_components_select()
            ui_component_show()
            ui_version_add()
        with ui.tab_panel(add_component):
            ui_component_add()
            pass


@ui.refreshable
def ui_components_select() -> None:
    with ui.column().classes("w-full"):
        ui.markdown(
            """
            #### Select a component
            Select a component to see the versions of this component.
            """
        )
        try:
            current_component = storage.get_active_object_from_storage(
                storage.CURRENT_COMPONENT
            )
            if current_component:
                value = current_component["component_id"]
            else:
                value = None
            components = db.get_collection(db.collection_components)
            components_options = {
                str(component["_id"]): f"{component.get('componentName')}"
                for component in components
            }
            if components:
                ui.select(
                    components_options,
                    value=value,
                    on_change=lambda e: store_selected_component(str(e.value)),
                    label="component",
                    with_input=True,
                ).classes("w-full")
        except Exception as e:
            ui.notify(
                f"Component selection could not be loaded. An Exception occured: {e}",
                type="negative",
            )


@ui.refreshable
def ui_version_add():
    with ui.column().classes("w-full"):
        current_component = storage.get_active_object_from_storage(
            storage.CURRENT_COMPONENT
        )
        if not current_component:
            return
        ui.markdown(
            """
            #### Add Component Version
            """
        )
        ui_component_version_form(
            component_type=current_component.get("type"),
            component_name=current_component.get("name"),
            repo_link=current_component.get("repo_link"),
            latest_commit=current_component.get("latest_commit"),
        )


def ui_component_version_form(repo_link, component_name, component_type, latest_commit):
    current_odtp_version = odtp_utils.get_odtp_version()
    component_version_input = ui.input(
        label="Component version",
        placeholder="component version",
        validation={"version number not valid": lambda value: len(value.strip()) >= 4},
    ).classes("w-1/3")
    odtp_version_input = ui.input(
        label="Default: current ODTP version",
        placeholder="ODTP version",
        value=current_odtp_version,
    ).classes("w-1/3")
    commit_hash_input = ui.input(
        label="Default: latest commit",
        placeholder="commit",
        value=latest_commit,
    ).classes("w-2/3")
    ui.label("Default: type is inherited from component")
    component_type_input = ui.radio(
        {
            db_utils.COMPONENT_TYPE_EPHERMAL: db_utils.COMPONENT_TYPE_EPHERMAL,
            db_utils.COMPONENT_TYPE_PERSISTENT: db_utils.COMPONENT_TYPE_PERSISTENT,
        },
        value=component_type,
    )
    ports_input = ui.input(
        label="Optional: Ports as comma seperated list",
        placeholder="ports as comma seperated list",
    ).classes("w-2/3")
    ui.button(
        "Register component version",
        on_click=lambda: register_component(
            component_name=component_name,
            odtp_version=odtp_version_input.value,
            component_version=component_version_input.value,
            repo_link=repo_link,
            commit_hash=commit_hash_input.value,
            component_type=component_type_input.value,
            ports=ports_input.value,
        ),
    )


@ui.refreshable
def ui_component_add():
    with ui.column().classes("w-full"):
        new_component_to_add = storage.get_active_object_from_storage(
            storage.NEW_COMPONENT
        )
        if not new_component_to_add:
            ui.markdown(
                """
                #### Component
                """
            )
            repo_link_input = ui.input(
                label="Repository URL",
                placeholder="repo url",
                validation={
                    "repo url not valid": lambda value: len(value.strip()) >= 4
                },
            ).classes("w-2/3")
            ui.button(
                "Proceed to next step",
                on_click=lambda: store_new_component(
                    repo_link=repo_link_input.value,
                ),
            )
            ui.button(
                "Cancel Component Entry",
                on_click=lambda: cancel_component_entry(),
            )
        else:
            repo_link = new_component_to_add.get("repo_link")
            repo_info = new_component_to_add.get("repo_info")
            latest_commit = new_component_to_add.get("latest_commit")
            ui.label(repo_link)
            ui_git_info_show(repo_info=repo_info, latest_commit=latest_commit)
            component_name_input = ui.input(
                value=repo_info.get("name"),
                label="Component name",
                placeholder="component name",
                validation={
                    "File not valid": lambda value: lambda value: len(value.strip())
                    >= 4
                },
            ).classes("w-2/3")
            ui_component_version_form(
                component_type=db_utils.COMPONENT_TYPE_EPHERMAL,
                component_name=component_name_input.value,
                repo_link=repo_link,
                latest_commit=latest_commit,
            )
            ui.button(
                "Cancel Component Entry",
                on_click=lambda: cancel_component_entry(),
            )


def cancel_component_entry():
    storage.reset_storage_delete([storage.NEW_COMPONENT])
    ui_component_add.refresh()


def store_new_component(repo_link):
    storage.storage_update_add_component(
        repo_link,
    )
    ui_component_add.refresh()


@ui.refreshable
def ui_component_show():
    try:
        current_component = storage.get_active_object_from_storage(
            storage.CURRENT_COMPONENT
        )
        if not current_component:
            return
        repo_info = current_component.get("repo_info")
        latest_commit = current_component.get("latest_commit")
        ui_git_info_show(
            repo_info=repo_info,
            latest_commit=latest_commit,
            component=current_component,
        )
    except Exception as e:
        ui.notify(
            f"Component details could not be loaded. An Exception occured: {e}",
            type="negative",
        )


def ui_git_info_show(repo_info, latest_commit, component=None):
    with ui.card().classes("bg-violet-100"):
        if component:
            ui.mermaid(
                f"""
                graph TD;
                    {component.get("name")};
                """
            )
        ui.markdown(
            f"""
            ###### Git repo            
            - **link to repo**: [{repo_info.get('name')}](repo_info.get('html_url'))   
            - **description**: {repo_info.get('description')}         
            - **license**: {repo_info.get('license')}
            - **repo visibility**: {repo_info.get('visibility')}
            - **latest commit on main**: {latest_commit[:7]}
        """
        )
        if not component:
            return
        ui.markdown(
            f"""
        ###### Component properties
        - **component-type**: {component.get('type')}
        """
        )
        versions = db.get_sub_collection_items(
            collection=db.collection_components,
            sub_collection=db.collection_versions,
            item_id=component["component_id"],
            ref_name=db.collection_versions,
        )
        if versions:
            versions_for_display = []
            for version in versions:
                version_display = {
                    "version_id": str(version["_id"]),
                    "component_version": version.get("component_version"),
                    "odtp_version": version.get("odtp_version"),
                    "type": version["component"].get("type"),
                    "commit": version["commitHash"][:7],
                }
                ports = version["ports"]
                if ports and ports != "None":
                    version_display["ports"] = ",".join(ports)
                else:
                    version_display["ports"] = "NA"
                versions_for_display.append(version_display)
            df = pd.DataFrame(data=versions_for_display)
            ui.table.from_pandas(df).classes("bg-violet-100")


@ui.refreshable
def ui_workarea():
    ui.markdown(
        """
        #### Component Versions

        ODTP Components and their versions

        ##### Actions

        - list available components
        - list versions for components
        - register components and component versions
        """
    )


def store_selected_component(value):
    try:
        storage.storage_update_component(component_id=value)
    except Exception as e:
        ui.notify(
            f"Selected component could not be stored. An Exception occured: {e}",
            type="negative",
        )
    else:
        ui_workarea.refresh()
        ui_component_show.refresh()


def register_component(
    repo_link,
    component_name,
    odtp_version,
    component_version,
    commit_hash,
    component_type,
    ports,
):
    try:
        commit_hash = otdp_git.check_commit_for_repo(
            repo_url=repo_link,
            commit_hash=commit_hash,
        )
        ports = parse.parse_ports(ports)
        db_utils.check_component_ports(ports)
        component_id, version_id = db.add_component_version(
            component_name=component_name,
            repository=repo_link,
            odtp_version=odtp_version,
            component_version=component_version,
            commit_hash=commit_hash,
            type=component_type,
            ports=ports,
        )
        ui.notify(
            f"Component version {component_id} / {version_id} has been added",
            type="positive",
        )
    except Exception as e:
        ui.notify(
            f"The component and version could not be added. An Exception occured: {e}",
            type="negative",
        )
    else:
        ui_components_select.refresh()
        ui_component_show.refresh()
        ui_component_add.refresh()
        ui_version_add.refresh()
        storage.reset_storage_delete(storage.NEW_COMPONENT)
