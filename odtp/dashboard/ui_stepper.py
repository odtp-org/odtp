from nicegui import ui


def odtp_stepper(step):
    with ui.stepper().props('horizontal').classes('w-full') as stepper:
        with ui.step('start'):
            with ui.stepper_navigation():
                with ui.column():
                    ui.label("Start by selecting or adding a user")
                    ui.button('Next: add users', on_click=lambda: ui.open('/users'))
        with ui.step('users'):
            with ui.stepper_navigation():
                ui.button('Next: add components', on_click=lambda: ui.open('/components'))
        with ui.step('components'):
            ui.label('Add your component')
            with ui.stepper_navigation():
                ui.button('Next', on_click=stepper.next)
                ui.button('Back', on_click=stepper.previous).props('flat')
        with ui.step('run'):
            ui.label('Run Component')
            with ui.stepper_navigation():
                ui.button('Done', on_click=stepper.next)
                ui.button('Back', on_click=stepper.previous).props('flat')
        with ui.step('logs'):
            ui.label('Check the logs')
            with ui.stepper_navigation():
                ui.button('Done', on_click=lambda: ui.notify('Yay!', type='positive'))
                ui.button('Back', on_click=stepper.previous).props('flat')
        stepper.set_value(step)