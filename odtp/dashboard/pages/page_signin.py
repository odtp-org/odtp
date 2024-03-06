from nicegui import Tailwind, ui
from odtp.dashboard.utils.storage import get_from_storage, save_to_storage, reset_all

def content() -> None:
    try: 
        user_role = get_from_storage("login_user_role")["value"]
        username = get_from_storage("login_user_name")["value"]
        login_name = get_from_storage("login_name")["value"]
        user_email  = get_from_storage("login_user_email")["value"]
        user_git = get_from_storage("login_user_git")["value"]
        print(user_role)
        with ui.row():
            ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />')
            ui.icon('eva-github').classes('text-5xl')
            ui.label(username).style("font-size: 200%; font-weight: 300; color: #008000")
        ui.label("Manage your account setting!").style("font-size: 100%; font-weight: 200; color: #92202A")
        with ui.row():
           ui.label("Name").tailwind.font_weight('extrabold')
           ui.label(login_name)
        with ui.row():
           ui.label("User Role").tailwind.font_weight('extrabold')
           ui.label(user_role)
        with ui.row():
           ui.label("Email").tailwind.font_weight('extrabold')
           ui.label(user_email)
        with ui.row():
           ui.label("Github Repository").tailwind.font_weight('extrabold')
           ui.label(user_git)
           
 
    except:
        print("Error: Login not performed yet.")
        
    ui_logout()    
    
    
    
def ui_logout() -> None:
   url ='https://auth.dev.swisscustodian.ch/auth/realms/odtp/protocol/openid-connect/logout?client_id=custodian&post_logout_redirect_uri=http://localhost:8000/' 
   reset_all()
   save_to_storage("authenticated", {"value": False})
   ui.button(
      "Logout", 
      on_click=lambda: ui.open(url), 
      icon="logout", 
      )

