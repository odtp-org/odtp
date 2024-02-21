#!/usr/bin/env python3

from typing import Optional

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from nicegui import Client, app, ui


import httpx, requests, json
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from urllib.parse import urlparse, parse_qs

##########################################################

"""This code use fastAPI to connect to Keycloak

"""




app =  FastAPI()

keycloak_client_id = 'authcode-flow-demo'
keycloak_client_secret = 'PGuKq8eiWTGpfcgVaR9v0WLHqBTdDkO0'
username = 'admin'
password = 'password'
token_url = 'http://localhost:8180/realms/master/protocol/openid-connect/token'
user_info_url = 'http://localhost:8180/admin/realms/master/users'

@app.get('/keycloak-login')
async def keycloak_login():
    return RedirectResponse(f'http://localhost:8180/realms/master/protocol/openid-connect/auth?response_type=code&client_id={keycloak_client_id}', status_code=302)

@app.get('/keycloak-code')
async def keycloak_code(code: str):
    print(code)
    params = {
        'client_id': keycloak_client_id,
        'client_secret': keycloak_client_secret,
        'code': code,
        'username': username,
        'password': password,
        'grant_type': 'password',
        'url-redirect': 'http://localhost:8000/keycloak-code'}
    
    headers = {
    'Content-Type':'application/x-www-form-urlencoded'
    }
    
    print('retrieving Access token from keycloack')
    response = requests.post(token_url, headers=headers, data=params)
    
    # Check for successful response
    if response.status_code != 200:
        print(f"Failed to retrieve access token. Status Code: {response.status_code}")
        return None
    access_token = json.loads(response.text).get('access_token')
    
    if not access_token:
        print("Access token not found in response.")
        return None
    
    print(f"Access Token: {access_token}")
    
        # Call UserInfo endpoint to get user information
    user_info_response = httpx.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})

    if user_info_response.status_code != 200:
        raise HTTPException(status_code=user_info_response.status_code, detail=f"Failed to retrieve user information. Status Code: {user_info_response.status_code}")

    user_info = user_info_response.json()
    print(user_info)
    # Extract user IDs from user_info
    user_ids = [user['id'] for user in user_info]

    # Print the result
    print("User IDs:", user_ids)
    return user_info
    
##################################################################### 
    """This function create a new user Keycloak

"""
def add_user(access_token, user_payload, user_url):
    """
    Add a user to Keycloak.

    Parameters:
    - access_token: The access token obtained for authentication.
    - user_payload: The payload containing user information.
    - user_url: The URL to add a user in Keycloak.

    Returns:
    - The HTTP response object.
    """
    print("Adding user to Keycloak")
    
    data = json.dumps(user_payload)
    print(f"User Payload: {data}")
    
    headers = { 
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    print(f"Request Headers: {headers}")
    
    user_response = requests.post(user_url, headers=headers, data=data)
    print(f"User Response: {user_response}")
    
    return user_response  
    
#####################################################################
"""This is an example from niceGUI

Please see the `OAuth2 example at FastAPI <https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/>`_  or
use the great `Authlib package <https://docs.authlib.org/en/v0.13/client/starlette.html#using-fastapi>`_ to implement a classing real authentication system.
Here we just demonstrate the NiceGUI integration.
"""

# in reality users passwords would obviously need to be hashed
passwords = {'user1': 'pass1', 'user2': 'pass2'}

unrestricted_page_routes = {'/login'}


class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        return await call_next(request)


app.add_middleware(AuthMiddleware)


@ui.page('/')
def main_page() -> None:
    with ui.column().classes('absolute-center items-center'):
        ui.label(f'Hello {app.storage.user["username"]}!').classes('text-2xl')
        ui.button(on_click=lambda: (app.storage.user.clear(), ui.open('/login')), icon='logout').props('outline round')


@ui.page('/subpage')
def test_page() -> None:
    ui.label('This is a sub page.')


@ui.page('/login')
def login() -> Optional[RedirectResponse]:
    def try_login() -> None:  # local function to avoid passing username and password as arguments
        if passwords.get(username.value) == password.value:
            app.storage.user.update({'username': username.value, 'authenticated': True})
            ui.open(app.storage.user.get('referrer_path', '/'))  # go back to where the user wanted to go
        else:
            ui.notify('Wrong username or password', color='negative')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
    return None


ui.run(storage_secret='THIS_NEEDS_TO_BE_CHANGED')