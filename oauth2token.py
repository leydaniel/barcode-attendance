#!/usr/bin/python

'''
    This script will attempt to open your webbrowser,
    perform OAuth 2 authentication and print your access token.

    It depends on two libraries: oauth2client and gflags.

    To install dependencies from PyPI:

    $ pip install python-gflags oauth2client

    Then run this script:

    $ python get_oauth2_token.py
    
    This is a combination of snippets from:
    https://developers.google.com/api-client-library/python/guide/aaa_oauth
'''
import sys
sys.path.append('/usr/lib/python2.7/dist-packages')
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from oauth2client.file import Storage


CLIENT_ID = '411103951529-nf611s2285n12mmqrkigq3ckgkac1gmv.apps.googleusercontent.com'

CLIENT_SECRET = 'uDKCenlmvo1desQfylHIUnYr'


flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                           client_secret=CLIENT_SECRET,
                           scope='https://spreadsheets.google.com/feeds https://docs.google.com/feeds',
                           redirect_uri='http://example.com/auth_return')

storage = Storage('creds.data')

credentials = run(flow, storage)

print ("access_token: %s") % credentials.access_token

