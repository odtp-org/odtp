import jwt
from jwt import PyJWKClient
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client
from storage import save_to_storage

def jwt_decode_header(encoded:str): 
    """Decodes the header of a JWT token. (Giving data like algorithm and token type as well as signature key: alg, typ, kid.)"""
    token_header = jwt.get_unverified_header(encoded)
    return token_header

def jwt_decode_payload(encoded: str):
    """Decodes the payload of a JWT token without verifying JWT. (Giving data like issuer, groups, etc.)"""
    payload = jwt.decode(jwt=encoded, algorithms=["RS256"], options={"verify_signature": False})
    return payload

def jwt_decode_from_client(encoded: str, url:str, audience:str):
    """Decodes the payload of a JWT token using a client and verifying . (Giving data like issuer, groups, etc.)"""
    jwks_client = PyJWKClient(url)
    signing_key = jwks_client.get_signing_key_from_jwt(encoded)
    payload = jwt.decode(encoded, 
                         signing_key.key, 
                         audience=audience,
                         algorithms=["RS256", "HS256"])
    return payload
    

class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """
    async def dispatch(self, request: Request, call_next):
        #TO_DO: enhancement: move url and audience to init of class
       
        url = "https://auth.dev.swisscustodian.ch/auth/realms/odtp/protocol/openid-connect/certs"
        audience = "custodian"
        if request.url.path in Client.page_routes.values():
            #request.scope allows to see all the information about the request
            print(request.headers.keys())
            #header = request.headers["authorization"]
            header = request.headers.get("authorization")
       
            jwt_token = header.split(" ")[1]
            decoded_jwt = jwt_decode_from_client(jwt_token, url, audience)
            print(decoded_jwt)
            user_role = decoded_jwt["groups"]
            user_name = decoded_jwt["preferred_username"]
            save_to_storage("login_user_name", {"value": user_name})
            print(user_name)
            print(user_role)
            if "odtp-provider" in user_role:
                print("ODTP provider")
                save_to_storage("login_user_role", {"value": "odtp-provider"})
            elif "user" in user_role:
                print("ODTP user")
                save_to_storage("login_user_role", {"value": "user"})
            else: 
                print("Error: Role unknown")
        return await call_next(request)
    