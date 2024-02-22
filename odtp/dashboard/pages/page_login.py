#!/usr/bin/env python3

import httpx, requests, json
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware #An abstract class that allows you to write ASGI middleware against a request/response interface


from nicegui import Client, app, ui


##########################################################

"""This code use fastAPI to connect to Keycloak

"""

unrestricted_page_routes = {'/keycloak-login'}
keycloak_client_id = 'authcode-flow-demo'
keycloak_client_secret = 'PGuKq8eiWTGpfcgVaR9v0WLHqBTdDkO0'
username = 'admin'
password = 'password'
token_url = 'http://localhost:8180/realms/master/protocol/openid-connect/token'
user_info_url = 'http://localhost:8180/admin/realms/master/users'
    
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request:Request, call_next):
        if 'access_token' not in app.storage.user:
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path
                return RedirectResponse('/keycloak-login')
        return await call_next(request)
    
app.add_middleware(AuthMiddleware)

@ui.page('/')
def index():
    app.storage.user['count'] = app.storage.user.get('count', 0) + 1
    with ui.row():
        ui.label('your own page visits:')
        ui.label().bind_text_from(app.storage.user, 'count')


@ui.page('/login')
def login() -> Optional[RedirectResponse]:
    app.storage.user['authenticated'] = app.storage.user.get('authenticated', False)

    if app.storage.user.get('authenticated', False):
        return RedirectResponse(f'http://localhost:8180/realms/master/protocol/openid-connect/auth?response_type=code&client_id={keycloak_client_id}', status_code=302)
    
    def login_callback():
        keycloak_login()

    with ui.card().classes('absolute-center'):
        ui.button('Log in', on_click=login_callback)

    return None


ui.run(storage_secret='private key to secure the browser session cookie', port=8000)  

"""-----------------Redirect to Keycloak  -----------------"""

@ui.page('/keycloak-login')
def keycloak_login()-> Optional[RedirectResponse]:

    return RedirectResponse(f'http://localhost:8180/realms/master/protocol/openid-connect/auth?response_type=code&client_id={keycloak_client_id}', status_code=302)
    

"""-----------------Get Keycloak authentication code -----------------"""
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
    app.storage.user['access_token'] =  access_token
    return access_token

"""-----------------Get User Profile-----------------"""
    
@ui.page('/users/profile')
def get_current_user():
    
    access_token = app.storage.user.get('access_token')
    print(f"Access Token3: {access_token}")
     #import pdb; pdb.set_trace()
    
    # Call UserInfo endpoint to get user information
    user_info_response = httpx.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
   
    print(user_info_response)
    
    

    if user_info_response.status_code != 200:
        raise HTTPException(status_code=user_info_response.status_code, detail=f"Failed to retrieve user information. Status Code: {user_info_response.status_code}")

    user_info = user_info_response.json()
    print(user_info)
    #Extract user IDs from user_info
    user_ids = [user['id'] for user in user_info]

   
    print("User IDs:", user_ids)
    return user_info
     
    




ui.run(storage_secret='private key to secure the browser session cookie', port=8000) 
    
