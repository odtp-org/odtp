import json
import pandas as pd
from nicegui import ui, app
import logging

import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.validators as validators
import odtp.mongodb.db as db
import odtp.mongodb.utils as db_utils
import odtp.helpers.git as odtp_git


def content() -> None:
    ui.markdown(
        """
        ## Manage Components
        """
    )
    with ui.right_drawer().classes("bg-slate-50").props(
        "bordered width=500"
    ) as right_drawer:
        ui_workarea()
    with ui.tabs() as tabs:
        list = ui.tab("Registered Components")
        select = ui.tab("Select Component")
        add_version = ui.tab("Add Version")
        add_component = ui.tab("Add Component")
    with ui.tab_panels(tabs, value=select).classes("w-full"):
        with ui.tab_panel(list):
            ui_components_list()
        with ui.tab_panel(select):
            ui_component_select()
            ui_component_show()
        with ui.tab_panel(add_version):
            ui_version_add()
        with ui.tab_panel(add_component):
            ui_component_add()


@ui.refreshable
def ui_components_list() -> None:
    """lists all registered components with versions"""
    with ui.column().classes("w-full"):
        try:
            versions = db.get_collection(
                collection=db.collection_versions,
            )
            if not versions:
                ui_theme.ui_no_items_yet("Components")
                return            
            versions_cleaned = [helpers.component_version_for_table(version)
                                for version in versions]                 
            if not versions:
                ui.label("You don't have components yet. Start adding one.")
                return
            df = pd.DataFrame(data=versions_cleaned)
            df = df.sort_values(by=["component", "version"], ascending=False)
            ui.table.from_pandas(df).classes("bg-violet-100")
        except Exception as e:
            logging.error(
                f"Components table could not be loaded. An Exception occurted: {e}"
            )


@ui.refreshable
def ui_component_select() -> None:
    with ui.column().classes("w-full"):
        try:
            current_component = storage.get_active_object_from_storage(
                storage.CURRENT_COMPONENT
            )
            components = db.get_collection(db.collection_components)
            if not components:
                ui_theme.ui_no_items_yet("Components")
                return    
            ui.markdown(
                """
                #### Select a component
                Select a component to see the versions of this component.
                """
            )      
            if current_component:
                value = current_component["component_id"]
            else:
                value = ""                                 
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
            logging.error(
                f"Component selection could not be loaded. An Exception occured: {e}"
            )


@ui.refreshable
def ui_version_add():
    ui.markdown(
        """
        #### Add Version for Component
        """
    )
    current_component = storage.get_active_object_from_storage(
        storage.CURRENT_COMPONENT
    )
    if not current_component:
        ui.label("First select the component by choosing the Component Details Tab.")
        return
    ui_form_version_add(current_component)
    ui_component_show()


def ui_form_version_add(current_component):
    repo_info = current_component["repo_info"]
    versions_in_db = db.get_sub_collection_items(
        collection=db.collection_components,
        sub_collection=db.collection_versions,
        item_id=current_component["component_id"],
        ref_name=db.collection_versions,
    )
    component_versions_in_db = [item.get("component_version") for item in versions_in_db]
    version_selector = {
        (item["name"], item["commit"]): item["name"]
        for item in repo_info.get("tagged_versions")
        if item["name"] not in component_versions_in_db
    }
    if not version_selector:
        ui.markdown(
            """
            All available versions on guthub have been already submitted to ODTP.
            """
        ).classes("text-lg")
        return  
    component_version_input = ui.select(
        options=version_selector,
        validation={f"A version selection is required":
                    lambda value: validators.validate_required_input(value)},
    ).classes("w-1/2")
    with ui.row():
        ports_inputs = []
        for i in range(3):
            port_input = ui.input(
                label="Port",
                placeholder="8052",
                validation={f"This is not a valid port":
                            lambda value: validators.validate_port_input(value)},
            ).classes("w-1/4")
            ports_inputs.append(port_input)
    with ui.row():            
        ui.button(
            "Register version",
            on_click=lambda: register_new_version(
                component_version_input=component_version_input,
                ports_inputs=ports_inputs,
                current_component=current_component
            ),
        )


def ui_form_component_add_step1():
    ui.markdown(
        """
        #### Add new Component
        """
    )
    repo_link_input = ui.input(
        label="Enter Repository URL",
        placeholder="repo url",
        validation={
            "Please provide a component repo url": lambda value: validators.validate_required_input(value),
        },
    ).classes("w-2/3")
    ui.button(
        "Proceed to next step",
        on_click=lambda: store_new_component(
            repo_link_input=repo_link_input,
        ),
    )


def ui_form_component_add_step2(new_component_to_add):
    with ui.row():
        ui_git_info_show(
            component=new_component_to_add
        )
        with ui.column().classes('w-full'):            
            repo_info=new_component_to_add.get("repo_info")
            ui.button(
                "Cancel Component Entry",
                on_click=lambda: cancel_component_entry(),
            )            
            version_selector = {
                (item["name"], item["commit"]): item["name"]
                for item in new_component_to_add.get("repo_info").get("tagged_versions")
            }
            component_type_selector = {
                db_utils.COMPONENT_TYPE_EPHERMAL: f"{db_utils.COMPONENT_TYPE_EPHERMAL}: components exits after run",
                db_utils.COMPONENT_TYPE_PERSISTENT: f"{db_utils.COMPONENT_TYPE_PERSISTENT}: component keeps running",
            }
            component_name_input = ui.input(
                value=repo_info.get("name"),
                label="Component name",
                placeholder="component name",
                validation={f"A component name is required":
                            lambda value: validators.validate_required_input(value)},
            ).classes("w-2/3")
            component_type_input = ui.select(
                label="component type",
                options=component_type_selector,
                validation={f"A component type nust be selected":
                            lambda value: validators.validate_required_input(value)},
            ).classes("w-2/3")
            component_version_input = ui.select(
                label="component version",
                options=version_selector,
                validation={f"A version selection is required":
                            lambda value: validators.validate_required_input(value)},
            ).classes("w-1/3")
            with ui.row():
                ports_inputs = []
                for i in range(3):
                    port_input = ui.input(
                        label="Port",
                        placeholder="8052",
                        validation={f"This is not a valid port":
                                    lambda value: validators.validate_port_input(value)},
                    ).classes("w-1/4")
                    ports_inputs.append(port_input)            
            ui.button(
                "Register component",
                on_click=lambda: register_new_component(
                    component_name_input=component_name_input,
                    component_version_input=component_version_input,
                    component_type_input=component_type_input,
                    ports_inputs=ports_inputs,
                    new_component=new_component_to_add,
                ),
            )


@ui.refreshable
def ui_component_add():
    with ui.column().classes("w-full"):
        new_component_to_add = storage.get_active_object_from_storage(
            storage.NEW_COMPONENT
        )
        if not new_component_to_add:
            ui_form_component_add_step1()
        else:
            ui_form_component_add_step2(new_component_to_add)


@ui.refreshable
def ui_component_show():
    try:
        current_component = storage.get_active_object_from_storage(
            storage.CURRENT_COMPONENT
        )
        if not current_component:
            return
        with ui.grid(columns=2):
            ui_git_info_show(
                component=current_component,
            )
            ui_odtp_info_show(
                component=current_component,
            )
    except Exception as e:
        logging.error(
            f"Component details could not be loaded. An Exception occured: {e}"
        )


def ui_git_info_show(component):
    repo_info = component.get("repo_info")
    with ui.card().classes("bg-gray-100"):
        ui.markdown(
            f"""
            ###### Git repo            
            - **link to repo**: [{repo_info.get('name')}]({repo_info.get('html_url')})   
            - **description**: {repo_info.get('description')}         
            - **license**: {repo_info.get('license')}
            - **repo visibility**: {repo_info.get('visibility')}
            - **latest commit on main**: {component.get("latest_commit")[:7]}
            
            Available Versions:
            """
        )
        for version_tag in repo_info.get('tagged_versions'):
            ui.markdown(
                f"""
                - **{version_tag.get("name")}**: {version_tag.get("commit")[:7]}
                """
            )

def ui_odtp_info_show(component):
    with ui.card().classes("bg-violet-100"):
        ui.markdown(
            f"""
            ###### Registered in ODTP
            - **name**: {component.get('name')}
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
                    "component_version": version.get("component_version"),
                    "commit": version["commitHash"][:7],
                }
                ports = version["ports"]
                if ports and ports != "None":
                    version_display["ports"] = ",".join(ports)
                else:
                    version_display["ports"] = "NA"
                versions_for_display.append(version_display)
            df = pd.DataFrame(data=versions_for_display)
            df = df.sort_values(by=["component_version"], ascending=False)
            ui.table.from_pandas(df).classes("bg-violet-100")


@ui.refreshable
def ui_workarea():
    ui.markdown(
        """
        #### Help

        ##### ODTP Components 

        ODTP Components are the Building blocks for Digital Twins and Executions:

        - Components are not user specific
        - Only tagged Versions of Components can be added

        Learn more at the
        [Documentation of ODTP](https://odtp-org.github.io/odtp-manuals)
        """
    )


def store_selected_component(value):
    try:
        storage.storage_update_component(component_id=value)
    except Exception as e:
        logging.error(
            f"Selected component could not be stored. An Exception occured: {e}"
        )
    else:
        ui_workarea.refresh()
        ui_component_show.refresh()
        ui_version_add.refresh()


def cancel_component_entry():
    storage.reset_storage_delete([storage.NEW_COMPONENT])
    ui_component_add.refresh()


def store_new_component(repo_link_input):
    repo_link = repo_link_input.value
    try:
        validators.validate_github_url(repo_link)    
    except Exception as e:    
        logging.error(f"new component {repo_link_input.value} could not be stored: an error {e} occurred")
        return
    try:    
        latest_commit = odtp_git.check_commit_for_repo(repo_link)
        repo_info = odtp_git.get_github_repo_info(repo_link)
        add_component = {
            "repo_link": repo_info.get("html_url"),
            "latest_commit": latest_commit,
            "repo_info": repo_info,
        }
        app.storage.user[storage.NEW_COMPONENT] = json.dumps(add_component)
    except Exception as e:
        logging.error(f"storage update for new component failed: {e}")
    else:    
        ui_component_add.refresh()


def register_new_version(
    component_version_input,
    ports_inputs,
    current_component,
):
    if not component_version_input.validate():
        ui.notify("Fill in the form correctly before you can add a new version", type="negative")
        return
    try:
        ports = [port_input.value for port_input in ports_inputs if port_input.value]    
        component_id, version_id = db.add_component_version(
            component_name=current_component.get("name"),
            repo_info=current_component.get("repo_info"),
            component_version=component_version_input.value[0],
            type=current_component.get("type"),
            ports=ports,
        )
        ui.notify(
            f"Component version {component_id} / {version_id} has been added",
            type="positive",
        )
    except Exception as e:
        ui.notify(
            f"The component and version could not be added. An Exception occurred: {e}",
            type="negative",
        )
    else:
        ui_components_list.refresh()
        ui_component_show.refresh()
        ui_component_select.refresh()
        ui_component_add.refresh()
        ui_version_add.refresh()


def register_new_component(
    component_name_input,
    component_version_input,
    component_type_input,
    ports_inputs,
    new_component,
):
    if (not component_name_input.validate() or not component_version_input.validate()
        or not component_type_input.validate()):
        ui.notify("Fill in the form correctly before you can add a new component", type="negative")
        return
    try:
        ports = ports = [port_input.value for port_input in ports_inputs if port_input.value]
        component_id, version_id = db.add_component_version(
            component_name=component_name_input.value,
            repo_info=new_component.get("repo_info"),
            component_version=component_version_input.value[0],
            type=component_type_input.value,
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
        storage.reset_storage_delete([storage.NEW_COMPONENT])
        ui_component_add.refresh()
        ui_component_select.refresh()
        ui_component_show.refresh()
        ui_version_add.refresh()
        ui_components_list.refresh()
