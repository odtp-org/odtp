import jwt, logging
from jwt import PyJWKClient
from fastapi import Request, status, HTTPException, Cookie, Response
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client,app
import odtp.dashboard.utils.storage as storage
from fastapi.responses import RedirectResponse, Response
import odtp.mongodb.db as db
import odtp.helpers.settings as config
from odtp.helpers.settings import ODTP_KEYCLOAK_REDIRECT


def jwt_decode_from_client(encoded: str, url:str, audience:str):
    """Decodes the payload of a JWT token using a client and verifying . (Giving data like issuer, groups, etc.)"""
    jwks_client = PyJWKClient(url)

    signing_key = jwks_client.get_signing_key_from_jwt(encoded)
    payload = jwt.decode(encoded, 
                         signing_key.key, 
                         audience=audience,
                         algorithms=["RS256", "HS256"])
    return payload


def update_user_storage(decoded_jwt):
        user_data = decoded_jwt  
        extracted_data = {}
        default_values = {"sub": None, "preferred_username": None, "email": None, "Github_repo": None}
        for key, default_value in default_values.items():
            value = user_data.get(key, default_value)
            extracted_data[key] = value
        print(f"extracted data{extracted_data}")
        db.add_user(
            name=extracted_data.get("preferred_username", ""),  
            github=extracted_data.get("Github_repo", ""),       
            email=extracted_data.get("email", ""),              
            sub=extracted_data.get("sub", ""))
        storage.storage_update_user_sub(extracted_data)
        
                
class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, url, audience):
        super().__init__(app)
        self.url = url
        self.audience = audience
    
    
    async def dispatch(self, request:Request, call_next):  
        header = request.headers.get("authorization")   
        if not header or not header.startswith("Bearer "):
            app.storage.user['auth_user'] = 'NONE'
            return RedirectResponse(ODTP_KEYCLOAK_REDIRECT)     
        """ Get the ID token from the header."""
        if header:
            jwt_token = header.split(" ")[1] 
            print(f"jwt_token {jwt_token}")
            try:
                decoded_jwt = jwt_decode_from_client(jwt_token, self.url, self.audience)
                update_user_storage(decoded_jwt)
            except Exception as e:
                logging.error(f"Error: {e}")
                return RedirectResponse(ODTP_KEYCLOAK_REDIRECT)
        return await call_next(request)                
           
