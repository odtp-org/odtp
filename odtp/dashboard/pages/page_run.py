import asyncio
import json
import os.path
import platform
import shlex
import sys

from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.storage as storage
import odtp.mongodb.db as db
from odtp.run import DockerManager


def content() -> None:
    with ui.dialog().props("full-width") as dialog, ui.card():
        result = ui.markdown()
        ui.button("Close", on_click=dialog.close)
    current_execution = storage.get_active_object_from_storage("execution")
    with ui.right_drawer().style("background-color: #ebf1fa").props(
        "bordered width=500"
    ) as right_drawer:
        ui_workarea(current_execution)
    ui.markdown(
        """
        ## Prepare and run Workflow or Component
        """
    )
    with ui.tabs().classes("w-full") as tabs:
        setup = ui.tab("Setup")
        select = ui.tab("Select")
        run = ui.tab("Run")
        results = ui.tab("Results")
    with ui.tab_panels(tabs, value=setup).classes("w-full"):
        with ui.tab_panel(setup):
            ui_settings_update()
        with ui.tab_panel(select):
            ui_select_for_run()
        with ui.tab_panel(run):
            ui_run(dialog, result)
        with ui.tab_panel(results):
            ui_results()


@ui.refreshable
def ui_workarea(current_execution):
    ui.markdown(
        """
        ### Work Area
        """
    )
    docker_settings = storage.get_active_object_from_storage("docker_settings")
    local_settings = storage.get_active_object_from_storage("local_settings")
    run_selection = storage.get_active_object_from_storage("run_selection")
    if current_execution:
        ui.markdown(
            """
            #### Execution       
            """
        )
        ui.label(current_execution.get("title"))
    with ui.row():
        with ui.row().classes("w-full items-center h-3 text-2xl"):
            ui.checkbox(value=bool(docker_settings)).disable()
            ui.label("Docker Settings")
        ui.markdown(
            f"""
            - **Image**: ``{docker_settings.get('image_name')}``
            - **Container**: ``{docker_settings.get('instance_name')}``  
            """
        )
    with ui.row():
        with ui.row().classes("w-full items-center h-3 text-2xl"):
            ui.checkbox(value=bool(local_settings)).disable()
            ui.label("Local Settings")
        ui.markdown(
            f"""
            - **Project path**: ``{helpers.get_workdir_path()}``
            - **Project folder**: ``{local_settings.get('project_path')}``
            - **Settings file**: ``{local_settings.get('env_file_path')}``
            """
        )
    with ui.row():
        with ui.row().classes("w-full items-center h-3 text-2xl"):
            ui.checkbox(value=bool(run_selection)).disable()
            ui.label("Run Selection")
        ui.markdown(
            f"""
            - **repo url**: ``{run_selection.get('repo_url')}``
            - **commit hash**: ``{run_selection.get('commit_hash')}``
            """
        )


@ui.refreshable
def ui_results():
    ui_project_directory_tree()


@ui.refreshable
def ui_project_directory_tree():
    local_settings = storage.get_active_object_from_storage("local_settings")
    project_path = local_settings.get("project_path")
    if project_path:
        with ui.column():
            ui.markdown(
                """
                #### Current Output folder
                """
            )
            folder_struture = helpers.map_output_folder(project_path=project_path)
            ui.tree(
                [
                    {
                        "id": project_path,
                        "children": [
                            {
                                "id": directory,
                                "children": [
                                    {"id": file}
                                    for file in list(folder_struture[directory])
                                ],
                            }
                            for directory in list(folder_struture.keys())
                        ],
                    },
                ],
                label_key="id",
            ).expand()


@ui.refreshable
def ui_run(dialog, result):
    docker_settings = storage.get_active_object_from_storage("docker_settings")
    local_settings = storage.get_active_object_from_storage("local_settings")
    run_selection = storage.get_active_object_from_storage("run_selection")
    columns = [
        {"name": "setting", "label": "setting", "field": "setting"},
        {"name": "category", "label": "category", "field": "category"},
        {"name": "value", "label": "value", "field": "value"},
    ]
    rows = [
        {
            "setting": "project path",
            "category": "local environment",
            "value": local_settings.get("project_path"),
        },
        {
            "setting": "env file path",
            "category": "local environment",
            "value": local_settings.get("env_file_path"),
        },
        {
            "setting": "docker image name",
            "category": "docker",
            "value": docker_settings.get("image_name"),
        },
        {
            "setting": "docker instance name",
            "category": "docker",
            "value": docker_settings.get("instance_name"),
        },
        {
            "setting": "repo url",
            "category": "git",
            "value": run_selection.get("repo_url"),
        },
    ]
    with ui.expansion("Settings for the docker commands!", icon="settings").classes(
        "w-full"
    ):
        ui.table(columns=columns, rows=rows)
    path = local_settings.get("project_path")
    env = local_settings.get("env_file_path")
    image = docker_settings.get("image_name")
    container = docker_settings.get("instance_name")
    repo = run_selection.get("repo_url")
    build_parameter = [
        f"--folder {path}",
        f"--image_name {image}",
        f"--repository {repo}",
    ]
    run_parameter = build_parameter + [
        f"--env_file {env}",
        f"--instance_name {container}",
    ]
    docker_build_command = f"odtp component prepare {' '.join(build_parameter)}"
    docker_run_command = f"odtp component run  {' '.join(run_parameter)}"
    print(docker_build_command)
    print(docker_run_command)
    ui.button(
        "Prepare", on_click=lambda: run_command(docker_build_command, dialog, result)
    ).props("no-caps")
    ui.button(
        "Run", on_click=lambda: run_command(docker_run_command, dialog, result)
    ).props("no-caps")


@ui.refreshable
def ui_settings_update():
    with ui.row().classes("w-full no-wrap"):
        with ui.column().classes("w-1/2"):
            ui.markdown(
                f"""
                Update Local Settings
                """
            )
            project_folder_name_input = ui.input(
                label="Project folder",
                placeholder="name",
                validation={
                    "Folder not valid": lambda value: helpers.check_project_folder(
                        value
                    )
                },
            ).classes("w-full")
            env_file_name_input = ui.input(
                label="Env file",
                placeholder="env file",
                validation={
                    "File not valid": lambda value: helpers.check_env_file(value)
                },
            ).classes("w-full")
            ui.button(
                "Update local settings",
                on_click=lambda: update_local_setup(
                    project_folder_name=project_folder_name_input.value,
                    env_file_name=env_file_name_input.value,
                ),
            )
        with ui.column().classes("w-1/2"):
            ui.markdown(
                f"""
                Update Docker Settings
                """
            )
            image_name_input = ui.input(
                label="Docker image name",
                placeholder="image name",
                validation={
                    "Lowercase letters: at least 4 letters long": lambda value: helpers.check_docker_image_name(
                        value
                    )
                },
            ).classes("w-full")
            instance_name_input = ui.input(
                label="Docker instance name",
                placeholder="instance name",
                validation={"Can not be empty": lambda value: len(value.strip()) >= 4},
            ).classes("w-full")
            ui.button(
                "Update Docker settings",
                on_click=lambda: update_docker_setup(
                    image_name=image_name_input.value,
                    instance_name=instance_name_input.value,
                ),
            )


@ui.refreshable
def ui_select_for_run():
    with ui.row().classes("w-full no-wrap"):
        with ui.column().classes("w-1/2"):
            ui.markdown(
                """
                ##### What to run
                """
            )
            try:
                components = db.get_collection(db.collection_components)
                executions = db.get_all_collections(db.collection_executions)
                print("-------components")
                print(components)
                print("-------executions")
                print(executions)
                """
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
                """
            except Exception as e:
                ui.notify(
                    f"Component selection could not be loaded. An Exception occured: {e}",
                    type="negative",
                )
            repo_url_input = ui.input(
                label="Repo URL",
                placeholder="repo URL",
                validation={"Folder not valid": lambda value: len(value.strip()) >= 4},
            ).classes("w-full")
            commit_hash_input = ui.input(
                label="Commit Hash: leave empty for latest commit",
                placeholder="commit hash",
            ).classes("w-full")
            ui.button(
                "Set new repo url",
                on_click=lambda: update_run_selection(
                    repo_url=repo_url_input.value, commit_hash=commit_hash_input.value
                ),
            )


def update_docker_setup(image_name, instance_name):
    storage.storage_update_docker(image_name=image_name, instance_name=instance_name)
    ui_workarea.refresh()


def update_run_selection(repo_url, commit_hash):
    if not commit_hash:
        commit_hash = None
    commit_hash = helpers.check_commit_for_repo(repo_url, commit_hash)
    storage.storage_run_selection(repo_url=repo_url, commit_hash=commit_hash)
    ui_workarea.refresh()
    ui_run.refresh()


def update_local_setup(project_folder_name, env_file_name):
    storage.storage_update_local_settings(
        project_folder_name=project_folder_name,
        env_file_name=env_file_name,
    )
    ui_workarea.refresh()
    ui_run.refresh()
    ui_project_directory_tree.refresh()


async def run_command(command: str, dialog, result) -> None:
    """Run a command in the background and display the output in the pre-created dialog."""
    dialog.open()
    result.content = "... loading"
    # NOTE replace with machine-independent Python path (#1240)
    command = command.replace("python3", sys.executable)
    process = await asyncio.create_subprocess_exec(
        *shlex.split(command, posix="win" not in sys.platform.lower()),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    # NOTE we need to read the output in chunks, otherwise the process will block
    output = ""
    while True:
        new = await process.stdout.read(4096)
        if not new:
            break
        output += new.decode()
        # NOTE the content of the markdown element is replaced every time we have new output
        result.content = f"```\n{output}\n```"
