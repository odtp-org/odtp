from nicegui import ui

import odtp.dashboard.utils.ui_theme as ui_theme


def ui_workarea_form(current_digital_twin, current_user, workdir, components, current_execution):
    with ui.row().classes("w-full"):
        ui.markdown(
            """
            # Manage Executions
            """
        )
    if not current_user:
        ui_theme.ui_add_first(
            item_name="a user",
            page_link=ui_theme.PATH_USERS,
            action="select",
        )
        return
    if not workdir:
        ui_theme.ui_add_first(
            item_name="a working directory",
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
    if not components:
        ui_theme.ui_add_first(
            item_name="Components",
            page_link=ui_theme.PATH_COMPONENTS,
            action="add",
        )
        return
    if current_execution:
        execution_title = current_execution.get("title")
    else:
        execution_title = ui_theme.MISSING_VALUE
    with ui.grid(columns=2):
        with ui.column():
            ui.markdown(
                f"""
                #### Current Selection
                - **user**: {current_user.get("display_name")}
                - **digital twin**: {current_digital_twin.get("name")}
                - **work directory**: {workdir}
                """
            )
