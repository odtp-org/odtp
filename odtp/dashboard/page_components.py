from nicegui import ui, app
from odtp.dashboard.page_users import ui_current_user


def content() -> None:
    ui.markdown("""
                # Manage Components
                """)
    ui.markdown("""
        ## Add new component
        """)
    ui_current_user()