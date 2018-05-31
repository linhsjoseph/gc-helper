import os
import flask
from flask import Flask, request, abort, redirect, session, jsonify, url_for
import requests
import json
import re
import time
import datetime
import pytz

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

USER_CREDENTIALS_FILE = "user_credentials.json"
TEMP_EVENTS_FILE = "temp_events.json"

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

app = Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = '-GCDFkFDMzMV2PfdwfQQxTI8'


line_bot_api = LineBotApi('mZMiO0OpVQqea16fwXcTuf4peoD+3eMwRjWSoLfG6wE/SbwYVNNBLEX6YGIwLNl/W9OoQ7ykhU6iPpwrDVocSD4P2BzZpj7IcFDFVhmFXawhFGg1jzEg3B2+Q5SiLIzws0ydAhDE6nObbozA8sKngQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d1152c329251dfa6c469f62ed744120d')

@app.route('/')
def index():
  return print_index_table()


@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)
    '''event = {
        'summary': 'Google I/O 2015',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2018-05-28T09:00:00-07:00', #in the format "yyyy-mm-dd", if this is an all-day event.
            'timeZone': 'Asia/Taipei',
        },
        'end': {
            'dateTime': '2018-05-28T17:00:00-07:00', #in the format "yyyy-mm-dd", if this is an all-day event.
            'timeZone': 'Asia/Taipei',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],
        'attendees': [
            {'email': 'lpage@example.com'},
            {'email': 'sbrin@example.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }'''
    #https://developers.google.com/calendar/v3/reference/events/insert
    event = {
        'summary': 'Google I/O 2015',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'date': '2018-05-28',
            'timeZone': 'Asia/Taipei',
        },
        'end': {
            'date': '2018-05-28',
            'timeZone': 'Asia/Taipei',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return 'Event created: %s' % (event.get('htmlLink'))
  


@app.route('/authorize')
def authorize():
    user_id = request.args.get('uid')
    print(user_id)
    flask.session['user_id'] = user_id
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback' , _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state
    print(authorization_url)
    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    user_id = flask.session['user_id']

    set_credentials(user_id,credentials)
    line_bot_api.push_message(user_id, TextSendMessage(text="已成功連結Google帳號"))
    line_bot_api.push_message(user_id, TextSendMessage(text="歡迎使用GC Helper(Beta)\n我可以幫你將活動紀錄在Google日曆上喔!\n\n範例格式:\n6/3聚餐，在一二三餐廳\n2017/6/3下午20:00聚餐\n06.03聚餐，在一二三餐廳\n6月3日聚餐，在一二三餐廳\n六月三日聚餐，在一二三餐廳\n六月三號聚餐，在一二三餐廳\n明天下午20:00聚餐"))
    return "已連結，請返回上一頁"
    #return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')

@app.route("/check_user_credentials")
def check_user_credentials():
    try:
        with open(USER_CREDENTIALS_FILE,'r') as f:
            user_credentials = json.load(f)
        return str(user_credentials)
    except:
        return 'none'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
	
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    #print("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    #print(event.source.user_id)
    if(check_credentials(event.source.user_id)):
        parse_message(event)
    else:
        reply_authorize(event)
    '''line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))'''

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
    user_credentials[user_id] = credentials_to_dict(_credentials)
    with open(USER_CREDENTIALS_FILE,'w+') as f:
        data = json.dumps(user_credentials)
        print(data)
        print(type(data))
        f.write(data)


def reply_authorize(event):
    message_text = "尚未與Google帳號連動，請利用以下連結登入Google帳號 https://gc-helper.herokuapp.com/authorize?uid="+event.source.user_id
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message_text))

def parse_message(event):
    print("parse")
    message_body = event.message.text
    print("m: "+message_body)
    temp_message = message_body
    temp_message = temp_message.replace("一","1")
    temp_message = temp_message.replace("二","2")
    temp_message = temp_message.replace("三","3")
    temp_message = temp_message.replace("四","4")
    temp_message = temp_message.replace("五","5")
    temp_message = temp_message.replace("六","6")
    temp_message = temp_message.replace("七","7")
    temp_message = temp_message.replace("八","8")
    temp_message = temp_message.replace("九","9")
    temp_message = temp_message.replace("十","1")
    print(temp_message)
    #Find Date
    dates = re.findall("\d{3,4}[ |.|\/|-]\d{1,2}[ |.|\/|-]\d{1,2}|\d{3,4}年\d{1,2}月\d{1,2}[日|號]|\d{1,2}[ |.|\/|-]\d{1,2}|\d{1,2}月\d{1,2}[日|號]|今天|明天|後天|大後天",temp_message)
    
    for i in range(len(dates)):
        dates[i] = re.sub("[ |.|\/|-|年|月]","-",dates[i])
        dates[i] = re.sub("[日|號]","",dates[i])
        if dates[i] == "今天" or dates[i] == "今日":
            dates[i] = (datetime.datetime.now() + datetime.timedelta(hours = 8)).strftime("%Y-%m-%d")
        elif dates[i] == "明天" or dates[i] == "明日":
            dates[i] = (datetime.datetime.now() + datetime.timedelta(hours = 8) + datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
        elif dates[i] == "後天":
            dates[i] = (datetime.datetime.now() + datetime.timedelta(hours = 8) + datetime.timedelta(days = 2)).strftime("%Y-%m-%d")
        elif dates[i] == "大後天":
            dates[i] = (datetime.datetime.now() + datetime.timedelta(hours = 8) + datetime.timedelta(days = 3)).strftime("%Y-%m-%d")
        if dates[i].count("-") < 2:
            dates[i] = str(time.strftime("%Y", time.localtime()))+"-"+dates[i]
    
    #Find Time
    times = re.findall("\d{1,2}[:|：]\d{1,2}|(?:am|pm|早上|中午|下午|傍晚|凌晨)\d{1,2}[:|：]\d{1,2}",temp_message)

        
    for i in range(len(times)):
        
        term_list = re.findall("am|pm|早上|中午|下午|傍晚|凌晨",times[i])
        if len(term_list) >0:
            term = term_list[0]
        else:
            term = ""
        times[i] = re.sub("am|pm|早上|中午|下午|傍晚|凌晨","",times[i])
        
        h = re.split(":|：",times[i])[0]
        m = re.split(":|：",times[i])[1]
        if term == "pm" or term == "中午" or term == "下午" or term == "傍晚":
            if 0 < int(h) and int(h) < 12:
                h=str(int(h)+12)
        
        times[i] = h+":"+m+":00"

    #Find Summary
    temp_message = re.sub("\d{1,2}[:|：]\d{1,2}|(?:am|pm|早上|中午|下午|傍晚|凌晨)\d{1,2}[:|：]\d{1,2}","",temp_message)
    temp_message = re.sub("\d{3,4}[ |.|\/|-]\d{1,2}[ |.|\/|-]\d{1,2}|\d{3,4}年\d{1,2}月\d{1,2}[日|號]|\d{1,2}[ |.|\/|-]\d{1,2}|\d{1,2}月\d{1,2}[日|號]|今天|明天|後天|大後天","",temp_message)

    message_list = re.split("[ |,|.|;|，|。|；]",temp_message)
    try:
        message_list.remove("")
    except:
        print()
    
    if len(dates)>0:
        _date = dates[0]
    else:
        _date = ""
    if len(times)>0:
        _time = times[0]
    else:
        _time = ""
    _date_Time=_date +"T"+ _time
    _description=temp_message
    if len(message_list)>0:
        _summary = message_list[0]
    else:
        _summary = ""


    print(_date_Time)
    print(_summary)
    print(_description)

    if _summary!="" and (_date_Time!="" or _date!=""):
        gc_event = {
            'summary': _summary,
            'description': _description,
            'start': {
                'date': _date,
                'timeZone': 'Asia/Taipei',
            },
            'end': {
                'date': _date,
                'timeZone': 'Asia/Taipei',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        if _time != "":
            gc_event["start"].pop("date")
            gc_event["end"].pop("date")
            gc_event["start"]["dateTime"] = _date_Time+"+08:00"
            gc_event["end"]["dateTime"] = _date_Time+"+08:00"
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text="日期:"+_date+" "+_time+"\n標題:"+_summary+"\n說明:"+_description))
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text="活動建立中..."))
        try:
            event_url = gc_create_event(event.source.user_id, gc_event)
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="建立完畢!!以下為活動連結\n"+event_url+"\n*小提醒：若Google日曆APP顯示\"找不到活動\"請於Google日曆中重新整理"))
        except:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="建立時發生錯誤!!"))
        
        #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message_body))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="抱歉!無法辨識"))

def gc_create_event(user_id,event):
    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**get_credentials(user_id))

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    
    set_credentials(user_id,credentials)
    #https://developers.google.com/calendar/v3/reference/events/insert
    

    event = service.events().insert(calendarId='primary', body=event).execute()    
    return event.get('htmlLink')

if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run()
    