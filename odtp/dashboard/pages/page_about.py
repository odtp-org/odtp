from nicegui import ui
import odtp.dashboard.utils.storage as storage

def content() -> None:
    
    with ui.row().classes('fixed-center'):
        # ui.label(f'Hello {user}!').classes('text-2xl')
        ui.markdown(
                """
                        # OTDP (Open Digital Twin Project)
                        
                        ## How to get started:
                        """
            )
        ui.link("Check out our Documentation", "https://odtp-org.github.io/odtp-manuals/").classes('text-lg bg-100-teal')
            