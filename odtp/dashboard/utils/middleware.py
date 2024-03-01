import jwt
from jwt import PyJWKClient
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client
from odtp.dashboard.utils.storage import save_to_storage


unrestricted_page_routes = {'/', '/components', '/signin'}

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
    print(url)
    jwks_client = PyJWKClient(url)
    signing_key = jwks_client.get_signing_key_from_jwt(encoded)
    print(signing_key)
    payload = jwt.decode(encoded, 
                         signing_key.key, 
                         audience=audience,
                         algorithms=["RS256", "HS256"])
    return payload

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, url, audience):
        super().__init__(app)
        self.url = url
        self.audience = audience
    
    async def dispatch(self, request:Request, call_next):
        print("test1")
        print(self.url)
        print(self.audience)
        if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
            print("test2")
            print(request.headers.keys())
            header = request.headers.get("authorization")
            jwt_token = header.split(" ")[1]
            print(jwt_token)
            decoded_jwt = jwt_decode_from_client(jwt_token, self.url, self.audience)
            print(decoded_jwt)
            user_role = decoded_jwt["groups"]
            user_name = decoded_jwt["preferred_username"]
            all_name = decoded_jwt["name"]
            user_email  = decoded_jwt["email"] 
            save_to_storage("login_user_name", {"value": user_name})
            save_to_storage("login_name", {"value": all_name})
            save_to_storage("login_user_email", {"value": user_email})
            print(user_name)
            print(user_role)
            print(user_email)
            if "odtp-provider" in user_role:
                print("ODTP provider")
                save_to_storage("login_user_role", {"value": "odtp-provider"})
            elif "user" in user_role:
                print("ODTP user")
                save_to_storage("login_user_role", {"value": "user"})
            else: 
                print("Error: Role unknown")
            
        return await call_next(request)
        
    
