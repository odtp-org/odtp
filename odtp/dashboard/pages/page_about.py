from nicegui import ui


def content() -> None:
    ui.markdown("""
                # OTDP (Open Digital Twin Project)
                
                ## What is a digital twin?
                """)
    ui.link('Check out the Documentation', 'https://odtp-org.github.io/odtp-manuals/')
