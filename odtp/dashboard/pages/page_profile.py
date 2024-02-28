from nicegui import ui, app
from fastapi import Request
import odtp.dashboard.utils.storage as storage
import odtp.dashboard.utils.middleware as middleware  

    
@ui.page('/')  
def central(): 
    try: 
        user_role = storage.get_from_storage("login_user_role")["value"]
        username = storage.get_from_storage("login_user_name")["value"]
        print(user_role)
        with ui.row():
            ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />')
            ui.icon('eva-github').classes('text-5xl')
            ui.label("Account").style("font-size: 200%; font-weight: 300; color: #92202A")
        ui.label("Manage your account setting!").style("font-size: 100%; font-weight: 200; color: #92202A")
        with ui.row():
           ui.label("User Name")
           ui.label(username)
        with ui.row():
           ui.label("User Role")
           ui.label(user_role)
        with ui.row():
           ui.label("Email")
           ui.label(user_role)
        with ui.row():
           ui.label("Github Repository")
           ui.label(user_role)
    except:
        print("Error: Login not performed yet.")

url = "https://auth.dev.swisscustodian.ch/auth/realms/odtp/protocol/openid-connect/certs"
audience = "custodian"

app.add_middleware(middleware.AuthMiddleware, url=url, audience=audience)
central()

