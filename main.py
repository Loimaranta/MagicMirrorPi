from __future__ import print_function
import httplib2
import os

import googleapiclient.discovery as discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time
import datetime

import tkinter
from configparser import ConfigParser
import requests

from tkinter import *
from tkinter import messagebox

from threading import Thread
import logging



try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

# Get API-key from config
config_file = "config.ini"
config = ConfigParser()
config.read(config_file)
api_key = config['gfg']['api']
url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'

def calendar():
    creds = None
    calendar_ids = []

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.


    while True:


        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)

            calendar_lbl['text'] = "Upcoming events: "
            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 5 events')
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                  maxResults=5, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return

        # Prints the start and name of the next 10 events
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'])
                calendar_lbl['text'] = calendar_lbl['text'] + "\n" + event['summary']

        except HttpError as error:
            print('An error occurred: %s' % error)

        time.sleep(15)

# Get weather data from weathermap
def getWeather(city):
    result = requests.get(url.format(city, api_key))

    if result:
        json = result.json()
        city = "Turku"
        temp_kelvin = json['main']['temp']
        temp_celsius = temp_kelvin - 273.15
        weather1 = json['weather'][0]['main']
        final = [city, temp_kelvin, temp_celsius, weather1]
        return final
    else:
        print("No weather data found")

# search and format weather
def searchWeather():
    while True:
        city = "Turku"
        weather = getWeather(city)

        if weather:
            location_lbl['text'] = '{}'.format(weather[0])
            temperature_label['text'] = str(round(weather[2])) + " °C"
            weather_l['text'] = weather[3]

        else:
            messagebox.showerror('Error', "Cannot find {}".format(city))
        time.sleep(5)
        print("Weather Update")

def clock():
    time_live = time.strftime("%H:%M:%S")
    time_lbl.config(text=time_live)
    time_lbl.after(200, clock)

def weatherWorker():
    ww = Thread(target=searchWeather)
    ww.start()

def clockWorker():
    cw = Thread(target=clock)
    cw.start()

def calendarWorker():
    calw = Thread(target=calendar)
    calw.start()

#App body
app = Tk()

# App attributes
app.title("MagicMirrorPi")
#app.attributes("-fullscreen", True)
app.configure(bg = 'black')

# formatting constants
text_font = ('calibri', 40)
bg = 'black'
fg = 'green'

#scaling functions
appHeight = app.winfo_height()
appWidth = app.winfo_width()

# Frame setup
cal_frame = Frame(app, bg = bg)
clock_frame = Frame(app, bg = bg)
weather_frame = Frame(app,bg = bg)





# Labels for location, temp and weather

location_lbl = Label(weather_frame, text = "Location", font = text_font, bg = bg, fg = fg)
location_lbl.pack()

temperature_label = Label(weather_frame, text = "", font = text_font, bg = bg, fg = fg)
temperature_label.pack()

weather_l = Label(weather_frame, text = "", font = text_font, bg = bg, fg = fg)
weather_l.pack()

# clock label

time_lbl = Label(clock_frame, font = text_font, bg = bg, fg = fg)
time_lbl.place(anchor = CENTER)
time_lbl.pack()

calendar_lbl = Label(cal_frame, text = "Event list: ", font = text_font, bg = bg, fg = fg)
calendar_lbl.pack(side = RIGHT)

#Frame packing
cal_frame.pack(side = LEFT)
weather_frame.pack(side = BOTTOM, anchor = SE)
clock_frame.pack(side = TOP, anchor = NE)

weatherWorker()
clockWorker()
calendarWorker()

app.mainloop()



