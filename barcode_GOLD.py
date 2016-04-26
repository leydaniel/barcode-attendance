#!/usr/bin/python

import sys, time
import RPi.GPIO as GPIO #import GPIO for LED's
from datetime import datetime
import requests, gspread #import gspread API to communicate with Google Sheets
sys.path.append('/usr/lib/python2.7/dist-packages')
from oauth2client.client import SignedJwtAssertionCredentials

errflag = 0 #set variable of invalid ids or errors to zero
valid = 'Student %r: Present on ' #message returned on pi for a valid sudent id
invalid = 'Invalid ID Number: %s - ' #message returned on pi for an invalid student id


def authenticate_google_docs():
    f = file('barcode_attendance-d4cfa48c3d44.p12', 'rb') #referencing the file for Ouathorization
    SIGNED_KEY = f.read() #reading the file
    f.close()
    scope = ['https://spreadsheets.google.com/feeds', 'https://docs.google.com/feeds'] #connecting to sheets.google.com
    credentials = SignedJwtAssertionCredentials('16dley@salpointe.org', SIGNED_KEY, scope) #sign in with email address

    data = {
        'refresh_token' : '4/LjtfNW4zjdf5qlIn0EkKHGskabs0gjSIeTGuzjfXxE4', #refresh token received from the oauth2token.py file, this is the string in the URL query in between the / /
        'client_id' : '411103951529-nf611s2285n12mmqrkigq3ckgkac1gmv.apps.googleusercontent.com', #client id from the .p12 file
        'client_secret' : 'uDKCenlmvo1desQfylHIUnYr', #client secret from .p12 file
        'grant_type' : 'refresh_token',
    }

    r = requests.post('https://accounts.google.com/o/oauth2/token', data = data)
    credentials.access_token = 'ya29..zAJqtxOTETQrsdBdJGXlnRiYnn1pMtxDt66N0r3JKkHKdiJChRpIDeIPQKxSI7ov1DZ_' #access token returned from the ouath2token.py program

    gc = gspread.authorize(credentials) #final step fro authorization
    return gc

gc=authenticate_google_docs()
sh=gc.open("Barcode_Attendance") #open a specific file
worksheet_list=sh.worksheets()


while True: #start of infinite loop
	barcode = raw_input('BARCODE:')
	lt = time.asctime()
	now = datetime.now()
	date = str(now.month) + "/" + str(now.day) + "/" + str(now.year) #establish date as a string
	timex = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) #establish time as a string
	if  barcode.strip() == 'stop': #stop the program with the word stop
		break 
	else:
		if len(barcode) != 6 or \ #barcode validation
		barcode[2] != '0' or \
		barcode[0:2] not in ['16','17','18','19']:
			errflag = errflag + 1 #count invalid ids
			print (invalid % errflag + lt) #return message that id is invalid
			GPIO.setmode(GPIO.BCM) 
			GPIO.setwarnings(False)
			GPIO.setup(12,GPIO.OUT) #establish pin for red LED
			GPIO.output(12,GPIO.HIGH) #turn on red LED
			time.sleep(2) #wait 2 seconds
			GPIO.output(12,GPIO.LOW) #turn off red LED
			worksheet=sh.worksheet("Invalid") #update sheet in the document "Barcode_Attendance"
			rc = worksheet.row_count #establish row count
			barc = worksheet.cell(rc, 1) #establish cell for invalid barcode
			timec = worksheet.cell(rc, 2) #establish cell for time
			print ('Updating barcode_attendance, Invalid: %s and %r.' % (barc, timec)) #show user that program is updating google sheets
			worksheet.add_rows(1) #add row on the sheet
			worksheet.update_cell(rc,1, barcode) #update cell with invalid barcode
			worksheet.update_cell(rc,2, date) #update cell with invalid date
			worksheet.update_cell(rc,3, timex) #update cell with invalid time
		else:
			print (valid % barcode + lt)
			GPIO.setmode(GPIO.BCM)
			GPIO.setwarnings(False)
			GPIO.setup(18,GPIO.OUT) #establish pin for green LED
			GPIO.output(18,GPIO.HIGH) #turn on green LED
			time.sleep(2) #wait 2 seconds
			GPIO.output(18,GPIO.LOW) #turn off green LED
			worksheet=sh.worksheet("Transactions")  #update sheet in the document "Barcode_Attendance"
			rc = worksheet.row_count
			barc = worksheet.cell(rc, 1) #establish cell for barcode
			datec = worksheet.cell(rc,2) #establish cell for date
			timec = worksheet.cell(rc, 3) #establish cell for time
			lsname = worksheet.cell(rc, 4) #establish cell for lastname
			fsname = worksheet.cell(rc, 5) #establish cell for firstname
			print ('Updating barcode_attendance, Transactions: %s, %s, %s, and %s.' % (barc, timec, lsname, fsname)) #let the user know that program is updating google sheets
			worksheet.add_rows(1) #add a row to the sheet
			firstname = '=VLOOKUP(A%s, Names, 2, FALSE)' % (rc) #formula in sheets to match id to firstname
			lastname = '=VLOOKUP(A%s, Names, 3, FALSE)' % (rc) #formula in sheets to match id to lastname
			worksheet.update_cell(rc,1, "\'"+barcode) #update cell with barcode
			worksheet.update_cell(rc,2,date) #update cell with date
			worksheet.update_cell(rc,3,timex) #update cell with time
			worksheet.update_cell(rc,4,lastname) #update cell with lastname
			worksheet.update_cell(rc,5,firstname) #update cell with firstname
