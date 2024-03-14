import typer
import requests
import time
import jwt

AUTH0_DOMAIN = 'http://localhost:8180/realms/myrealm/protocol/openid-connect/auth/device'
AUTH0_CLIENT_ID = 'myclient'
ALGORITHMS = ['RS256']
CLIENT_SECRET = '95ZBagsIqS0ioTbwSwMFFwEgBXG1Fncn'

current_user = None

def jwt_decode_header(encoded:str): 
    """Decodes the header of a JWT token. (Giving data like algorithm and token type as well as signature key: alg, typ, kid.)"""
    token_header = jwt.get_unverified_header(encoded)
    return token_header

def jwt_decode_payload(encoded: str):
    """Decodes the payload of a JWT token without verifying JWT. (Giving data like issuer, groups, etc.)"""
    payload = jwt.decode(jwt=encoded, algorithms=["RS256"], options={"verify_signature": False})
    return payload

# def jwt_decode_from_client(encoded: str, url:str, audience:str):
#     """Decodes the payload of a JWT token using a client and verifying . (Giving data like issuer, groups, etc.)"""
#     print(url)
#     jwks_client = PyJWKClient(url)
#     signing_key = jwks_client.get_signing_key_from_jwt(encoded)
#     print(signing_key)
#     payload = jwt.decode(encoded, 
#                          signing_key.key, 
#                          audience=audience,
#                          algorithms=["RS256", "HS256"])
#     return payload


def login():
    """
    Runs the device authorization flow and stores the user object in memory
    """
    device_code_payload = {
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'openid profile'
    }
    device_code_response = requests.post('http://localhost:8180/realms/myrealm/protocol/openid-connect/auth/device', data=device_code_payload)
    print(f"Device code {device_code_response}")
    if device_code_response.status_code != 200:
        print('Error generating the device code')
        raise typer.Exit(code=1)

    print('Device code successful')
    device_code_data = device_code_response.json()
    print('1. On your computer or mobile device navigate to: ', device_code_data['verification_uri_complete'])
    print('2. Enter the following code: ', device_code_data['user_code'])

    token_payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code_data['device_code'],
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': CLIENT_SECRET
        
    }
    print(f"token_payload {token_payload}")
    
    authenticated = False
    while not authenticated:
        print('Checking if the user completed the flow...')
        token_response = requests.post('http://localhost:8180/realms/myrealm/protocol/openid-connect/token', data=token_payload) 
        print(f"token_response {token_response}")
        try:
            token_data = token_response.json()
            print(f"token_data {token_data}")
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            print(f"Response content: {token_response.text}")
       
        if token_response.status_code == 200:
            print('Authenticated!')
            print('- Id Token: {}...'.format(token_data['id_token'][:10]))
            
            global current_user
            current_user = jwt.decode(token_data['id_token'], algorithms=ALGORITHMS, options={"verify_signature": False})
            print(f"current_user {current_user}")
            authenticated = True
            return current_user 
        elif token_data['error'] not in ('authorization_pending', 'slow_down'):
            print(token_data['error_description'])
            raise typer.Exit(code=1)
        else:
            time.sleep(device_code_data['interval'])