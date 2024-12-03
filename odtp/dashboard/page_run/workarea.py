from nicegui import ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.page_run.helpers as rh


def ui_workarea_layout(current_user, workdir, current_execution, current_digital_twin):
    ui.markdown(
        """
        ## Prepare and Run Executions
        """
    )
    if not current_user:
        ui_theme.ui_add_first(
            item_name="user",
            page_link=ui_theme.PATH_USERS,
            action="select",
        )
        return
    if not workdir:
        ui_theme.ui_add_first(
            item_name="working directory",
            page_link=ui_theme.PATH_USERS,
            action="select",
        )
        return
    if not current_digital_twin:
        ui_theme.ui_add_first(
            item_name="a digital twin",
            page_link=ui_theme.PATH_DIGITAL_TWINS,
            action="select",
        )
        return
    if not current_execution:
        ui_theme.ui_add_first(
            item_name="an executions",
            page_link=ui_theme.PATH_EXECUTIONS,
            action="select",
        )
        return
    current_run = storage.get_active_object_from_storage(storage.EXECUTION_RUN)
    secret_files = current_run.get("secret_files")
    project_path = current_run.get("project_path")
    if not [file for file in secret_files if file]:
        secret_files = ""
    else:
        ",".join(secret_files)
    folder_status = rh.get_folder_status(
        execution_id=current_execution["execution_id"],
        project_path=project_path,
    )
    project_path_display = project_path
    if not project_path:
        project_path_display = ui_theme.MISSING_VALUE
    with ui.grid(columns=2):
        with ui.column():
            ui.markdown(
                f"""
                #### Current Selection
                - **user**: {current_user.get("display_name")}
                - **digital twin**: {current_digital_twin.get("name")}
                - **current execution**: {current_execution.get("title")}
                - **secret files**: {secret_files}
                - **work directory**: {workdir}
                - **project directory**: {project_path_display}
                """
            )
            rh.ui_display_folder_status(folder_status)
            rh.ui_display_secrets(secret_files)
        with ui.column():
            if current_execution:
                ui.markdown(
                    f"""
                    #### Actions
                    """
                )
                ui.button(
                    "Manage Executions",
                    on_click=lambda: ui.open(ui_theme.PATH_EXECUTIONS),
                    icon="link",
                )
  