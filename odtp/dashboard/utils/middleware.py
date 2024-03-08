import jwt, logging
from jwt import PyJWKClient
from fastapi import Request, status, HTTPException, Cookie, Response
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client,app
from odtp.dashboard.utils.storage import save_to_storage, get_from_storage
from fastapi.responses import RedirectResponse, Response
import odtp.mongodb.db as db


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

def add_user( name_input, github_input, email_input):
   
    try:
        user_id = db.add_user(
            name=name_input, 
            github=github_input, 
            email=email_input,
        )
        print(f"A user with id {user_id} has been created")
    except Exception as e:
        print(f"The user could not be added in the database. An Exception occurred: {e}")
  

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, url, audience):
        super().__init__(app)
        self.url = url
        self.audience = audience
       #app.on_disconnect(self.on_logout)
                       
    
    async def dispatch(self, request:Request, call_next):
        # Get the client's IP address
        client_ip = request.client.host
        print(client_ip)
        is_id_token_cookie_present = await self.is_cookie_empty_or_exists(request, "SWISSDATACUSTODIAN_IDTOKEN")
        print(is_id_token_cookie_present)
        if not is_id_token_cookie_present:
            print("test cookie")
            if (
                request.url.path in Client.page_routes.values() 
                and request.url.path not in unrestricted_page_routes
                ):
                return RedirectResponse("http://localhost:8000/")
        print(app.storage.browser)
        #jwt_token = request.cookies.get("SWISSDATACUSTODIAN_IDTOKEN", "")
        header = request.headers.get("authorization")
        if header:
            jwt_token = header.split(" ")[1]
            print(jwt_token)
            #if jwt_token:
            try:
                decoded_jwt = jwt_decode_from_client(jwt_token, self.url, self.audience)
                self.update_user_storage(decoded_jwt)

            except Exception as e:
                logging.error(f"Error decoding JWT: {e}")
        
       
         # Call on_logout here if needed
        #await self.on_logout(request, Response, "SWISSDATACUSTODIAN_IDTOKEN")
        
        
        return await call_next(request)
        
                
    async def is_cookie_empty_or_exists(self,request, cookie_name):
        cookie_value = request.cookies.get(cookie_name, "")
        return bool(cookie_value)            
    
    def update_user_storage(self, decoded_jwt):
        user_role = decoded_jwt.get("groups", [])
        user_name = decoded_jwt.get("preferred_username", "")
        all_name = decoded_jwt.get("name", "")
        user_email = decoded_jwt.get("email", "")
        user_gitrepo = decoded_jwt.get("Github_repo", "")
        
        print(user_name, user_email, user_gitrepo)

        save_to_storage("login_user_name", {"value": user_name})
        save_to_storage("login_name", {"value": all_name})
        save_to_storage("login_user_email", {"value": user_email})
        save_to_storage("login_user_git", {"value": user_gitrepo})
        save_to_storage("authenticated", {"value": True})
        add_user(
            name_input=user_name,
            github_input=user_gitrepo,
            email_input=user_email,
            )
        if "odtp-provider" in user_role:
            logging.info("ODTP provider")
            save_to_storage("login_user_role", {"value": "odtp-provider"})
        elif "user" in user_role:
            logging.info("ODTP user")
            save_to_storage("login_user_role", {"value": "user"})
        else:
            logging.error("Error: Role unknown") 
       
            
            
    async def on_logout(self, request, response, cookie_name):
       print(app.storage.user)
       authenticated_data = get_from_storage("authenticated")

       if authenticated_data and not authenticated_data.get("value", False):
               response.delete_cookie(key=cookie_name)
               
