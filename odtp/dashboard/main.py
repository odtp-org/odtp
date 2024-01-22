from odtp.dashboard.page_start import content as start_page
from odtp.dashboard.page_users import content as users_page
from odtp.dashboard.page_components import content as components_page
import ui_theme
from nicegui import app, ui


@ui.page('/')
def home() -> None:
    with ui_theme.frame('Homepage'):
        start_page()


@ui.page('/users')
def users():
    with ui_theme.frame('Results'):
        users_page()


@ui.page('/components')
def components():
    with ui_theme.frame('Components'):
        components_page()


app.add_static_files('/static', 'static')

ui.run(title='ODTP', storage_secret='private key to secure the browser session cookie')
