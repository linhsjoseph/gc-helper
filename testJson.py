import json
USER_CREDENTIALS_FILE = "user_credentials.json"
TEMP_EVENTS_FILE = "temp_events.json"
event = {"message": {"id": "8035604115598", "text": "aasdb", "type": "text"}, "replyToken": "86653a0ac623423abd0c3ea9cd073b3a", "source": {"type": "user", "userId": "U68d47cba3c797cc1d5e660cc3e0365f1"}, "timestamp": 1527600826328, "type": "message"}
credentials = {'token': 'credentials.token',
          'refresh_token': 'credentials.refresh_token',
          'token_uri': 'credentials.token_uri',
          'client_id': 'credentials.client_id',
          'client_secret': 'credentials.client_secret',
          'scopes': 'credentials.scopes'}


'''try:
    with open(USER_CREDENTIALS_FILE,'r') as f:
        user_credentials = json.load(f)
    print(str(user_credentials))

except:
    user_credentials = dict()
    user_credentials[event['source']['userId']] = None
    with open(USER_CREDENTIALS_FILE,'w+') as f:
        data = json.dumps(user_credentials)
        print(data)
        print(type(data))
        f.write(data)


print(user_credentials)
message_body="a"
print(message_body.find("a"))'''

def check_credentials(user_id):    
    try:
        with open(USER_CREDENTIALS_FILE,'r') as f:
            user_credentials = json.loads(f.read())
            
        if(user_credentials[user_id] == None):
            return False
        else:
            return True
    except:
        user_credentials = dict()
        user_credentials[user_id] = None
        with open(USER_CREDENTIALS_FILE,'w+') as f:
            data = json.dumps(user_credentials)
            print(data)
            print(type(data))
            f.write(data)
        return False

def get_credentials(user_id):
    try:
        with open(USER_CREDENTIALS_FILE,'r') as f:
            user_credentials = json.loads(f.read())
            return user_credentials[user_id]
    except:        
        return None

def set_credentials(user_id,_credentials):
    try:
        with open(USER_CREDENTIALS_FILE,'r') as f:
            user_credentials = json.loads(f.read())
    except:
        user_credentials = dict()
    user_credentials[user_id] = _credentials
    with open(USER_CREDENTIALS_FILE,'w+') as f:
        data = json.dumps(user_credentials)
        print(data)
        print(type(data))
        f.write(data)

#print(check_credentials("U68d47cba3c797cc1d5e660cc3e0365f1"))
print(get_credentials("234"))