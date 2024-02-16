import requests
import json 


# Get token to call keycloack api

accessTokenUrl = 'http://localhost:8180/realms/master/protocol/openid-connect/token'

print(accessTokenUrl)

#Update the admin credential for keycloack instance

username = 'admin'
password = 'password'
payload = 'client_id=admin-cli&username='+username+'&password='+password+'&grant_type=password'

print(payload)

# Headers
headers = {
    'Content-Type':'application/x-www-form-urlencoded'
    }

print('retrieving Access token from keycloack')
reponse = requests.post(accessTokenUrl, headers=headers, data=payload)
access_token = json.loads(reponse.text)['access_token']
print(access_token)

userUrl = "http://localhost:8180/admin/realms/master/users"

userPayload = {
        "firstName":"jon",
        "lastName":"Snow",
        "email":"mkm29@case.edu",
        "username":"jon.snow"
    }

print(userPayload)

data2=json.dumps(userPayload)
print(data2)

headers2 = { 
            'Authorization': 'Bearer '+access_token+'',
            'Content-Type':'application/json'
            }

print(headers2)
userResponse = requests.post(userUrl,headers=headers2, data=data2)

print(userResponse)
if (userResponse.status_code == 201) :
    print("ok")
elif (userResponse.status_code == 409) :
    print("already exists")

