import jwt
from jwt import PyJWKClient
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client
from storage import save_to_storage


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
    def __init__(self, app, url, audience):
        super().__init__(app)
        self.url = url
        self.audience = audience
        
    async def dispatch(self, request: Request, call_next):
       
        if request.url.path in Client.page_routes.values():
            #request.scope allows to see all the information about the request
            print(request.headers.keys())
            header = request.headers.get("authorization")
            #if " " not in header:
                #raise HTTPException(status_code=401, detail="Authorization header is missing or invalid")
       
            jwt_token = header.split(" ")[1]
            decoded_jwt = jwt_decode_from_client(jwt_token, self.url, self.audience)
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