from nicegui import Tailwind, ui
from odtp.dashboard.utils.storage import get_from_storage, save_to_storage, reset_all

def content() -> None:
   ui.markdown(
        """
        ## Manage User Profile
        """
    )
   try: 
        user_role = get_from_storage("login_user_role")["value"]
        username = get_from_storage("login_user_name")["value"]
        login_name = get_from_storage("login_name")["value"]
        user_email  = get_from_storage("login_user_email")["value"]
        user_git = get_from_storage("login_user_git")["value"]
        print(user_role)
        with ui.row().classes("content-center"):
            ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />')
            ui.icon('eva-github').classes("text-lg")
            ui.label(username).style("font-size: 200%; font-weight: 300; color: #008000")
        with ui.row().classes("content-center"):
           ui.label("Name").classes("text-lg")
           ui.label(login_name).classes("text-lg")
        with ui.row().classes("content-center"):
           ui.label("User Role").classes("text-lg")
           ui.label(user_role).classes("text-lg")
        with ui.row().classes("content-center"):
           ui.label("Email").classes("text-lg")
           ui.label(user_email).classes("text-lg")
        with ui.row().classes("content-center"):
           ui.label("Repository Name").classes("text-lg")
           ui.label(user_git).classes("text-lg")
           
 
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
   

