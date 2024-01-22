from contextlib import contextmanager

from odtp.dashboard.ui_menu import menu

from nicegui import ui


@contextmanager
def frame(navtitle: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(primary='#009485', secondary='#009485', accent='#009485', positive='#009485')
    with ui.header().classes('justify-between text-white'):
        ui.label('OTDP').classes('font-bold')
        with ui.row():
            menu()
    yield
