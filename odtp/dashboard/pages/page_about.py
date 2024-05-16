from nicegui import ui


def content() -> None:
    with ui.row().classes('fixed-center'):
            ui.markdown(
                """
                        # OTDP (Open Digital Twin Project)

                        [Check out our Documentation](https://odtp-org.github.io/odtp-manuals/)

                        ## Getting started:

                        - [Add and select a user](/users)
                        - [Add and select a digital twin](/digital-twins)
                        - [Check that components for your workflow are there](/components)
                        - [Setup an execution](/executions)
                        - [Run the execution](/run)
                        """
            ).style('font-size: 150%')
