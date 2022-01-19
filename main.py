from __future__ import print_function

import datetime
import os
import time
from configparser import ConfigParser
from threading import Thread
from tkinter import *
from tkinter import messagebox

import googleapiclient.discovery as discovery
import httplib2
import requests
from dateutil.parser import parse as dtparse
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

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

CLIENT_SECRET_FILE = 'credentials.json'
APPLICATION_NAME = 'MagicMirror Pi'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'credentials.json')

    store = Storage(credential_path)
    credentials = None
    try:
        credentials = store.get()
    except:
        print('something went wrong I guess')

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def calendar():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # This code is to fetch the calendar ids shared with me
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/calendarList/list
    page_token = None
    calendar_ids = []
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if not '@group.v.' in calendar_list_entry['id']:
                calendar_ids.append(calendar_list_entry['id'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    # Set starting date to now, and end date to week from now
    start_date = (datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
    end_date = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    event_list = []

    #Fill event_list with all available events from all calendars
    for calendar_id in calendar_ids:
        eventsResult = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date,
            timeMax=end_date,
            singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        for event in events:
            if ('summary') in event:
                event_list.append(event)

    event_list_sorted = sorted(event_list, key = lambda x: x['start'].get('dateTime', x['start'].get('date')))

    return event_list_sorted

def parseCalendarEvents():
    timeFormat = '%d.%m. %H:%M'
    while True:
        event_l = calendar()
        calendar_lbl['text'] = ""
        for event in event_l:
            start_time = datetime.datetime.strftime(dtparse(event['start'].get('dateTime', event['start'].get('date'))), format = timeFormat)
            calendar_lbl['text'] += start_time + " " + event['summary'] + "\n"
        time.sleep(30)

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
    calw = Thread(target=parseCalendarEvents)
    calw.start()

#App body
app = Tk()

# App attributes
app.title("MagicMirrorPi")
app.attributes("-fullscreen", True)
app.configure(bg = 'black')

# formatting constants
text_font = ('calibri', 14)
big_font = ('calibri', 40)
bg = 'black'
fg = 'green'

#scaling functions
appHeight = app.winfo_height()
appWidth = app.winfo_width()

# Frame setup. clock and weather in stat frame to allow splitting half in half
cal_frame = Frame(app, bg = bg, highlightbackground = "white", highlightthickness = 2)
stat_frame = Frame(app, bg = bg, highlightbackground = "white", highlightthickness = 2)
clock_frame = Frame(stat_frame, bg = bg, highlightbackground = "white", highlightthickness = 2)
weather_frame = Frame(stat_frame,bg = bg, highlightbackground = "white", highlightthickness = 2)





# Labels for location, temp and weather

location_lbl = Label(weather_frame, text = "Location", font = big_font, bg = bg, fg = fg)
location_lbl.pack()

temperature_label = Label(weather_frame, text = "", font = big_font, bg = bg, fg = fg)
temperature_label.pack()

weather_l = Label(weather_frame, text = "", font = big_font, bg = bg, fg = fg)
weather_l.pack()

# clock label

time_lbl = Label(clock_frame, font = big_font, bg = bg, fg = fg)
time_lbl.pack()

calendar_lbl = Label(cal_frame, text = "Event list: ", font = text_font, bg = bg, fg = fg)
calendar_lbl.pack()

#Frame packing. Calendar frame half screen, stats the other half. Stats split to that clock is on top half, weather at bottom half
cal_frame.pack_propagate(0)
stat_frame.pack_propagate(0)
clock_frame.pack_propagate(0)
weather_frame.pack_propagate(0)

cal_frame.pack(fill='both', side = 'left', expand = 'True')
stat_frame.pack(fill='both', side = 'right', expand = 'True')
clock_frame.pack(fill='both', side = 'top', expand = 'True')
weather_frame.pack(fill='both', side = 'bottom', expand = 'True')

weatherWorker()
clockWorker()
calendarWorker()

app.mainloop()



