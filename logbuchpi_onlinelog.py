#!/usr/bin/env python3

# import many libraries
from __future__ import print_function
import pickle
import os.path
import io
import subprocess
import urllib, json
from googleapiclient.discovery import build  
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime

# My Spreadsheet ID ... See google documentation on how to derive this
MY_SPREADSHEET_ID = '193rLLMTHkEk1ER17QpqMCCHqwGSACW-.........'


def update_sheet(sheetname, temperature, waterlevel, var1):  
    """update_sheet method:
       appends a row of a sheet in the spreadsheet with the 
       the latest temperature, pressure and humidity sensor data
    """
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'logbuchpi_googleauth.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    # Call the Sheets API, append the next row of sensor data
    # values is the array of rows we are updating, its a single row
    values = [ [ str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), temperature, waterlevel, var1 ] ]
    body = { 'values': values }
    # call the append API to perform the operation
    result = service.spreadsheets().values().append(
                spreadsheetId=MY_SPREADSHEET_ID, 
                range=sheetname + '!A1:D1',
                valueInputOption='USER_ENTERED', 
                insertDataOption='INSERT_ROWS',
                body=body).execute()                     

def main():  
    """main method:
       reads raspberry pi sensors, then
       call update_sheets method to add that sensor data to the spreadsheet
    """

    f = open("/sys/class/thermal/thermal_zone0/temp", "r")
    t = f.readline()
    tempC = float(t)/1000

    url = 'http://nichtzuhaben.at/level/index.php?l=1'
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    waterlevel = int(data[2])

    #freedisk_cmd = "df -H | grep root | awk '{ print $4 }'"
    freedisk_cmd = "df -h -BM | grep root | cut -d 'M' -f3"
    freedisk_str = int(subprocess.Popen(freedisk_cmd, shell=True, stdout=subprocess.PIPE).stdout.read().strip())
    #freedisk_str = subprocess.stdout.read()

    print ('CPU Temperature: %f °C' % tempC)
    print ('Waterlevel Linz: %i cm' % waterlevel)
    print ('Free Disk Space: %i MByte' % freedisk_str)
    update_sheet("Logbuchpi_Log", tempC, waterlevel, freedisk_str)


if __name__ == '__main__':  
    main()
