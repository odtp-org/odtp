from nicegui import ui


def menu() -> None:
    ui.link('About', '/').classes(replace='text-white')
    ui.link('Users', '/users').classes(replace='text-white')
    ui.link('Components', '/components').classes(replace='text-white')
    ui.link('Results', '/results').classes(replace='text-white')
