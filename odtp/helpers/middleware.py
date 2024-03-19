import typer
import requests
import time
import jwt
import redis


"""
This will be replace by handle by the gateway
"""
AUTH0_DOMAIN = 'http://localhost:8180/realms/myrealm/protocol/openid-connect/auth/device'
AUTH0_CLIENT_ID = 'myclient'
ALGORITHMS = ['RS256']
CLIENT_SECRET = '95ZBagsIqS0ioTbwSwMFFwEgBXG1Fncn'

current_user = None
token_data = {'token': None, 'expiration_time': 0}

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)



def clear_redis_cache():
    """
    Clear the Redis cache by deleting the key 'token_data'.
    """
    redis_client.delete('token_data')
    print("Redis cache cleared successfully.")



# Function to update token data
def update_token_data(current_user):
    # Clear Redis cache if expiration time is less than current time
    token_data = redis_client.get('token_data')
    print(f"Welcome {token_data}!")
    if token_data:
        token_data = eval(token_data.decode('utf-8'))
        if 'expiration_time' in token_data:
            expiration_time = token_data['expiration_time']
            # Convert the struct_time objects to human-readable dates
            expiration_time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expiration_time))

            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            if expiration_time1 < current_time:
                clear_redis_cache()

    # Retrieve token data from Redis cache if available
    token_data_str = redis_client.get('token_data')
    
    if token_data_str:
        return eval(token_data_str.decode('utf-8'))

    # If token data not in cache or expired, update it and store in cache
    token_data = {
        'token': current_user['preferred_username'],
        'expiration_time': current_user['exp']
    }
    redis_client.set('token_data', str(token_data))  # Store token data in Redis cache
    return token_data


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