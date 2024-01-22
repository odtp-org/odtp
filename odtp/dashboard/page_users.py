from nicegui import ui, app
from odtp.dashboard.ui_stepper import odtp_stepper
import odtp.dashboard.utils_mongodb as utils_db
import pandas as pd



def users_select_ui() -> None:
    users = utils_db.get_user_options()
    print(users.keys())
    ui.select(
        users,
        label="user",
        on_change=lambda e: store_user_id(e.value),
        with_input=True,
        value=list(users.values())[0]
    ).props("size=80")


@ui.refreshable
def ui_current_user():
    user_id = app.storage.user['user_id']
    if user_id:
        user = utils_db.get_current_user(user_id)
        ui.label("Current user:")
        ui.label(user_id)
        ui.label(user['displayName'])


@ui.refreshable
def store_user_id(value):
    current_user_id = value
    app.storage.user['user_id'] = current_user_id
    ui_current_user.refresh()


@ui.refreshable
def user_table_ui():
    users = utils_db.get_users()
    data = pd.DataFrame(data=users)
    ui.table.from_pandas(data[['_id', 'displayName', 'updated_at', 'email', 'github']])

def digital_twin_table_ui():
    digital_twins = utils_db.get_digital_twins()
    df = pd.DataFrame(data=digital_twins)
    df_min = df[["_id"]]
    print(df_min)
    ui.table.from_pandas(df_min)

def add_user(name, github, email):
    user_id = utils_db.add_new_user(name=name, github=github, email=email)
    app.storage.user['user_id'] = user_id
    ui.notify(f"A user with id {user_id} has been created", close_button=True, type="positive")
    ui.notify(f"User id in storage is {user_id}", close_button=True, type="warning")
    user_table_ui.refresh()


def ui_add_user():
    with ui.row():
        name_input = ui.input(label='Name', placeholder='name',
                              validation={'Can not be empty': lambda value: len(value.strip()) != 0})

        github_input = ui.input(label='Github User', placeholder='github username',
                                validation={'Can not be empty': lambda value: len(value.strip()) != 0})

        email_input = ui.input(label='Email', placeholder='email',
                               validation={'Not a valid email, should contain @': lambda value: "@" in value})
        ui.button('Add new user',
                  on_click=lambda: add_user(
                      name=name_input.value, github=github_input.value, email=email_input.value))

def content() -> None:
    ui.markdown("""
# Manage Users 
""")

    ui.markdown("""
## Select your user
This is the user that you want to create digital twins for.
""")
    users_select_ui()
    ui_current_user()

    ui.markdown("""
## Add new user
if you are not registered yet: create a new user as a first step.
""")
    ui_add_user()

    ui.markdown("""
### Explore the database
""")
    with ui.expansion('Users', caption='Table of all users').classes('w-full'):
        user_table_ui()
    with ui.expansion('Your Digital Twins', caption='Table the users digital twins').classes('w-full'):
        digital_twin_table_ui()
    odtp_stepper(step="users")






