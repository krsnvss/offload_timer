from requests import get, post
from datetime import datetime, timedelta
from sql import save_token, read_token
from configparser import ConfigParser

# Load configuration file
cfg = ConfigParser()
cfg.read("settings.ini")
webapi_host = cfg['mes']['host']
username = cfg['mes']['user']
userpassword = cfg['mes']["password"]


# Get new token
def get_token(_username, _password):
    host = webapi_host + '/Auth/Token'
    response = post(host, data={'username':_username,
                                   'password':_password,
                                   'grant_type':'password'})
    token = response.json()['access_token']
    token_expires = datetime.now() + timedelta(seconds=response.json()['expires_in'])
    save_token(token, token_expires)


# Write tag value
def write_tag(token, value):
    host = webapi_host + '/Data'
    timestamp = datetime.now().strftime("'%Y-%m-%dT%H:%M:%SZ'")
    mes_headers = {'Content-Type': "application/json",
                   'Accept': "application/json",
                   'Cache-Control': "no-cache",
                   'Authorization': 'Bearer '+token}
    payload = '''{"Tags": [{"Name": "Test200",
                     "DataPoints": [{"ValueString": null,
                                     "ValueLong": null,
                                     "ValueDouble": ''' + str(value) + ''',
                                     "TimeStamp": ''' + timestamp + ''',
                                     "Annotation": "",
                                     "QualityMark": {"Value": "good",
                                                     "StateNumber": null },
                                     "DigitalSetId": null,
                                     "ValueFloat": null,
                                     "ValueDateTime": null}]
                     }]
           }'''
    response = post(host, data=payload, headers=mes_headers)
    return response.status_code


# Test if MES webapi is available
def check_mes():
    host = webapi_host + '/Ping'
    response = get(host)
    return response.json()["Value"]
