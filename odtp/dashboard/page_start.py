from nicegui import ui
from odtp.dashboard.ui_stepper import odtp_stepper

def content() -> None:
    ui.image('/static/odtp.png').classes('w-2/3')
    ui.markdown("""
                # OTDP GUI 
                User interface for ODTP: 
                """)
    with ui.row():
        ui.button('Documentation', on_click=lambda: ui.open('https://odtp-org.github.io/odtp-manuals/'))
    odtp_stepper(step="start")


