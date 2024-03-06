from nicegui import app, native, ui
import webbrowser

from odtp.dashboard.utils.storage import save_to_storage, get_from_storage
from odtp.dashboard.utils.middleware import AuthMiddleware

import odtp.dashboard.utils.ui_theme as ui_theme
from odtp.dashboard.pages.page_about import content as about_page
from odtp.dashboard.pages.page_components import content as components_page
from odtp.dashboard.pages.page_digital_twins import content as digital_twins_page
from odtp.dashboard.pages.page_executions import content as executions_page
from odtp.dashboard.pages.page_run import content as run_page
from odtp.dashboard.pages.page_user import content as user_page
from odtp.dashboard.pages.page_signin import content as signin_page


@ui.page("/")
def home() -> None:
    with ui_theme.frame("Homepage"):
        about_page()


@ui.page("/users")
def start():
    with ui_theme.frame("Users"):
        user_page()

@ui.page("/signin")
def start():
    with ui_theme.frame("Profiles"):
        signin_page()

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
url = "https://auth.dev.swisscustodian.ch/auth/realms/odtp/protocol/openid-connect/certs"
audience = "custodian"
app.add_middleware(AuthMiddleware, url=url, audience=audience) 
   
 

#controller = webbrowser.get('Firefox')
#controller.open('http://localhost:8000') 

ui.run(title="ODTP", show=False, port=5000, storage_secret="private key to secure the browser session cookie")
#"private key to secure the browser session cookie"
