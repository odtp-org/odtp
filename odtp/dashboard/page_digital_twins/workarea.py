import logging
from nicegui import ui
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.page_digital_twins.storage as storage

log = logging.getLogger("__name__")


def ui_workarea_form(current_user):
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
    current_digital_twin = storage.storage_get_current_digital_twin()
    dt_line = ""
    if current_digital_twin:
        dt_line = f"- **current digital twin**:  {current_digital_twin.get('digital_twin_name')}"
    with ui.row():
        ui.markdown(
            f"""
            #### Current Selection
            - **user**: {current_user.get("user_name")}
            - **work directory**: {current_user.get("workdir")}
            {dt_line}
            """
        )
    current_digital_twin = storage.storage_get_current_digital_twin()
    if not current_digital_twin:
        return
    with ui.row():
        ui.button(
            "Manage Executions",
            on_click=lambda: ui.open(ui_theme.PATH_EXECUTIONS),
            icon="link",
        )
