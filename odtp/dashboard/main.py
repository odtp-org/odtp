from nicegui import app, native, ui
from odtp.helpers.settings import (ODTP_DASHBOARD_PORT, ODTP_DASHBOARD_RELOAD)

import odtp.dashboard.utils.ui_theme as ui_theme
from odtp.dashboard.page_about.main import content as about_page
from odtp.dashboard.pages.page_components import content as components_page
from odtp.dashboard.pages.page_digital_twins import content as digital_twins_page
from odtp.dashboard.pages.page_executions import content as executions_page
from odtp.dashboard.pages.page_run import content as run_page
from odtp.dashboard.page_users.main import content as user_page


@ui.page("/")
def home() -> None:
    with ui_theme.frame("Homepage"):
        about_page()


@ui.page("/users")
def start():
    with ui_theme.frame("Users"):
        user_page()


@ui.page("/components")
def components():
    with ui_theme.frame("Components"):
        components_page()


@ui.page("/run")
def components():
    with ui_theme.frame("Run"):
        run_page()


@ui.page("/digital-twins")
def components():
    with ui_theme.frame("Digital Twins"):
        digital_twins_page()


@ui.page("/executions")
def components():
    with ui_theme.frame("Executions"):
        executions_page()


app.add_static_files("/static", "static")

ui.run(
    title="ODTP", 
    storage_secret="private key to secure the browser session cookie", 
    port=ODTP_DASHBOARD_PORT,
    reload=ODTP_DASHBOARD_RELOAD,
)
