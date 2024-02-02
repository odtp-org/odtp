from nicegui import ui
import odtp.dashboard.utils.storage as storage


def content() -> None:
    current_execution = storage.get_active_object_from_storage("execution")
    with ui.right_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as right_drawer:
        ui_workarea(current_execution)
    ui.markdown("""
                ## Prepare Execution
                """)


@ui.refreshable
def ui_workarea(current_execution):
    ui.markdown("""
                ### Work Area
                """)
    if current_execution:
        ui.markdown("""
                    #### Execution       
                    """)
        ui.label(current_execution.get("title"))  
