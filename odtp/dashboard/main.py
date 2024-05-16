from nicegui import app, native, ui
from odtp.helpers.settings import (ODTP_DASHBOARD_PORT, ODTP_DASHBOARD_RELOAD, ODTP_KEYCLOAK_LOGOUT, ODTP_KEYCLOAK_AUDIENCE,ODTP_KEYCLOAK_URL,ODTP_AUTHENTICATION)

import odtp.dashboard.utils.ui_theme as ui_theme
from odtp.dashboard.pages.page_about import content as about_page
from odtp.dashboard.pages.page_components import content as components_page
from odtp.dashboard.pages.page_digital_twins import content as digital_twins_page
from odtp.dashboard.pages.page_executions import content as executions_page
from odtp.dashboard.pages.page_run import content as run_page
from odtp.dashboard.pages.page_user import content as user_page
from odtp.dashboard.utils.middleware import AuthMiddleware
from odtp.dashboard.utils.storage import reset_all


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
        
@ui.page("/logout")
def ui_logout() -> None:
    url = ODTP_KEYCLOAK_LOGOUT
    reset_all()
    ui.open(url) 


app.add_static_files("/static", "static")
if ODTP_AUTHENTICATION == True:
    url = ODTP_KEYCLOAK_URL
    audience = ODTP_KEYCLOAK_AUDIENCE
    app.add_middleware(AuthMiddleware, url=url, audience=audience)

ui.run(
    title="ODTP", 
    storage_secret="private key to secure the browser session cookie", 
    port=ODTP_DASHBOARD_PORT,
    reload=ODTP_DASHBOARD_RELOAD,
)
