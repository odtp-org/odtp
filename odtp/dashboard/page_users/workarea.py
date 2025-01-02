from nicegui import app, ui
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.page_users.storage as storage


def workarea():
    with ui.row().classes("w-full"):
        ui.markdown(
            """
            # Manage Users
            """
        )
    current_user = storage.storage_get_current_user()
    print(current_user)
    if not current_user:
        return
    with ui.row():
        ui.markdown(
            f"""
            #### Current Selection
            - **user**: {current_user.get("user_name")}
            - **work directory**: {current_user.get("workdir")}
            """
        )
    with ui.row():
        ui.button(
            "Manage digital twins",
            on_click=lambda: ui.open(ui_theme.PATH_DIGITAL_TWINS),
            icon="link",
        )
