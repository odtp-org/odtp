import pandas as pd
from nicegui import ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.mongodb.db as db


def ui_component_table(versions):
    with ui.column().classes("w-full"):
        if not versions:
            ui_theme.ui_no_items_yet("Components")
            return
        versions_cleaned = [
            helpers.component_version_for_table(version) for version in versions
        ]
        if not versions:
            ui.label("You don't have components yet. Start adding one.")
            return
        df = pd.DataFrame(data=versions_cleaned)
        df = df.sort_values(by=["component", "version"], ascending=False)
        ui.table.from_pandas(df).classes("bg-violet-100")


def ui_component_display(current_component):
    with ui.grid(columns=2):
        ui_git_info_show(
            component=current_component,
        )
        ui_odtp_info_show(
            component=current_component,
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
        for version_tag in repo_info.get("tagged_versions"):
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
