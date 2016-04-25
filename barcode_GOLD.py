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

#!/usr/bin/python

import sys, time
import RPi.GPIO as GPIO
from datetime import datetime
import requests, gspread
sys.path.append('/usr/lib/python2.7/dist-packages')
from oauth2client.client import SignedJwtAssertionCredentials

errflag = 0
valid = 'Student %r: Present on '
invalid = 'Invalid ID Number: %s - '


def authenticate_google_docs():
    f = file('barcode_attendance-d4cfa48c3d44.p12', 'rb')
    SIGNED_KEY = f.read()
    f.close()
    scope = ['https://spreadsheets.google.com/feeds', 'https://docs.google.com/feeds']
    credentials = SignedJwtAssertionCredentials('16dley@salpointe.org', SIGNED_KEY, scope)

    data = {
        'refresh_token' : '4/LjtfNW4zjdf5qlIn0EkKHGskabs0gjSIeTGuzjfXxE4',
        'client_id' : '411103951529-nf611s2285n12mmqrkigq3ckgkac1gmv.apps.googleusercontent.com',
        'client_secret' : 'uDKCenlmvo1desQfylHIUnYr',
        'grant_type' : 'refresh_token',
    }

    r = requests.post('https://accounts.google.com/o/oauth2/token', data = data)
    credentials.access_token = 'ya29..zAJqtxOTETQrsdBdJGXlnRiYnn1pMtxDt66N0r3JKkHKdiJChRpIDeIPQKxSI7ov1DZ_'

    gc = gspread.authorize(credentials)
    return gc

gc=authenticate_google_docs()
sh=gc.open("Barcode_Attendance")
worksheet_list=sh.worksheets()


while True:
	barcode = raw_input('BARCODE:')
	lt = time.asctime()
	now = datetime.now()
	date = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
	timex = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
	if  barcode.strip() == 'stop':
		break 
	else:
		if len(barcode) != 6 or \
		barcode[2] != '0' or \
		barcode[0:2] not in ['16','17','18','19']:
			errflag = errflag + 1
			print (invalid % errflag + lt)
			GPIO.setmode(GPIO.BCM)
			GPIO.setwarnings(False)
			GPIO.setup(12,GPIO.OUT)
			GPIO.output(12,GPIO.HIGH)
			time.sleep(2)
			GPIO.output(12,GPIO.LOW)
			worksheet=sh.worksheet("Invalid")
			rc = worksheet.row_count
			barc = worksheet.cell(rc, 1)
			timec = worksheet.cell(rc, 2)
			print ('Updating barcode_attendance, Invalid: %s and %r.' % (barc, timec))
			worksheet.add_rows(1)
			worksheet.update_cell(rc,1, barcode)
			worksheet.update_cell(rc,2, date)
			worksheet.update_cell(rc,3, timex)
		else:
			print (valid % barcode + lt)
			GPIO.setmode(GPIO.BCM)
			GPIO.setwarnings(False)
			GPIO.setup(18,GPIO.OUT)
			GPIO.output(18,GPIO.HIGH)
			time.sleep(2)
			GPIO.output(18,GPIO.LOW)
			worksheet=sh.worksheet("Transactions")
			rc = worksheet.row_count
			barc = worksheet.cell(rc, 1)
			datec = worksheet.cell(rc,2)
			timec = worksheet.cell(rc, 3)
			lsname = worksheet.cell(rc, 4)
			fsname = worksheet.cell(rc, 5)
			print ('Updating barcode_attendance, Transactions: %s, %s, %s, and %s.' % (barc, timec, lsname, fsname))
			worksheet.add_rows(1)
			firstname = '=VLOOKUP(A%s, Names, 2, FALSE)' % (rc)
			lastname = '=VLOOKUP(A%s, Names, 3, FALSE)' % (rc)
			worksheet.update_cell(rc,1, "\'"+barcode)
			worksheet.update_cell(rc,2,date)
			worksheet.update_cell(rc,3,timex)
			worksheet.update_cell(rc,4,lastname)
			worksheet.update_cell(rc,5,firstname)
