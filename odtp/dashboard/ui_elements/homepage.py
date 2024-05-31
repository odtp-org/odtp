from nicegui import ui


def ui_homepage():   
    with ui.row():
        ui.markdown(
            """
            # OTDP (Open Digital Twin Project)

            ## Getting Started
            """
        )
    with ui.row():
        ui.button(
            "Check out the Documentation",
            on_click=lambda: ui.open("https://odtp-org.github.io/odtp-manuals/"),
            icon="link",
        ).props("flat").classes("place-items-start")
    with ui.grid(columns=2).classes("w-full"):
        with ui.column().classes("w-full"):
            ui.markdown(
                """
                ### Digital Twins
                """
            ).classes("w-full")
            with ui.grid(columns=1):
                ui.button(
                    "Add / Select User",
                    on_click=lambda: ui.open("/users"),
                    icon="link",
                ).props("flat").classes("place-items-start")
                ui.button(
                    "Add / Select Digital Twins",
                    on_click=lambda: ui.open("/digital-twins"),
                    icon="link",
                ).props("flat").classes("place-items-start")
                ui.button(
                    "Build / Run Executions",
                    on_click=lambda: ui.open("/executions"),
                    icon="link",
                ).props("flat").classes("place-items-start")
            ui.mermaid(
                """
                graph TB;
                    CA0[Component A]
                    CB0[Component B]
                    CC0[Component C]             
                    subgraph WT[Execution of a Digital Twin]
                        direction LR
                        CA0 --> CB0
                        CB0 --> CC0
                    end          
                """
            ).classes("w-full")
        with ui.column().classes("w-full"):
            ui.markdown(
                """
                ### Components
                """
            ).classes("w-full")
            with ui.grid(columns=1):
                ui.button(
                    "Add / View Components",
                    on_click=lambda: ui.open("/components"),
                    icon="link",
                ).props("flat").classes("place-items-start")
            ui.mermaid(
                """
                graph TB;
                    CA0[Component A]
                    CB0[Component B]
                    CC0[Component C]             
                """
            ).classes("w-full")