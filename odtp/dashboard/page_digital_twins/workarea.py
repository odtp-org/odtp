import logging
from nicegui import app, ui
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.ui_theme as ui_theme
log = logging.getLogger("__name__")




def ui_workarea_form(current_user, user_workdir, current_digital_twin):
    ui.markdown(
        """
        # Manage Digital Twins
        """
    )    
    if not current_user:
        ui_theme.ui_add_first(
            item_name="a user",
            page_link=ui_theme.PATH_USERS,
            action="select",
        )
        return        
    if not user_workdir:
        user_workdir_display = "-"
    else:
        user_workdir_display = user_workdir
    if not current_digital_twin:
        digital_twin_display = ui_theme.MISSING_VALUE
    else:
        digital_twin_display = current_digital_twin.get("name")
    with ui.grid(columns=2):
        with ui.column():
            ui.markdown(
                f"""
                #### Current Selection
                - **user**: {current_user.get("display_name")}
                - **digital twin**: {digital_twin_display}
                - **work directory**: {user_workdir_display}
                """
            )
        if current_digital_twin:
            with ui.column():
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
