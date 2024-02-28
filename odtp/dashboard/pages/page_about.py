from nicegui import ui


def content() -> None:
    with ui.row().classes('fixed-center'):
            ui.markdown(
                """
                        # OTDP (Open Digital Twin Project)
                        
                        ## How to get started:
                        """
            )
            ui.link("Check out our Documentation", "https://odtp-org.github.io/odtp-manuals/").classes('text-lg bg-100-teal')
