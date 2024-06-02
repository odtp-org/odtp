from nicegui import app, ui

import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme


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
    if not project_path:
        project_path = ui_theme.MISSING_VALUE
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
                - **project directory**: {project_path}
                """
            )
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
  