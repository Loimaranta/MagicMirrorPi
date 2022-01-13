import time
import tkinter
from configparser import ConfigParser
import requests
from tkinter import *
from tkinter import messagebox
from threading import Thread
import logging

# Get API-key from config
config_file = "config.ini"
config = ConfigParser()
config.read(config_file)
api_key = config['gfg']['api']
url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'

# Get weather data
def getWeather(city):
    result = requests.get(url.format(city, api_key))

    if result:
        json = result.json()
        city = "Turku"
        country = json['sys']
        temp_kelvin = json['main']['temp']
        temp_celsius = temp_kelvin - 273.15
        weather1 = json['weather'][0]['main']
        final = [city, country, temp_kelvin, temp_celsius, weather1]
        return final
    else:
        print("No weather data found")


# fetch weather data
def searchWeather():
    while True:
        city = "Turku"
        weather = getWeather(city)

        if weather:
            location_lbl['text'] = '{}, Finland'.format(weather[0])
            temperature_label['text'] = str(round(weather[3])) + " °C"
            weather_l['text'] = weather[4]

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

#App body
app = Tk()

# App attributes
app.title("Weather App")
##app.attributes("-fullscreen", True)
app.configure(bg = 'black')

# formatting constants
text_font = ('calibri', 80)
bg = 'black'
fg = 'green'





# Labels for location, temp and weather

location_lbl = Label(app, text = "Location", font = text_font, bg = bg, fg = fg)
location_lbl.pack(padx = 100, pady = 10, side = tkinter.BOTTOM, anchor = SE)

temperature_label = Label(app, text = "", font = text_font, bg = bg, fg = fg)
temperature_label.pack(padx = 100, pady = 10, side = tkinter.BOTTOM, anchor = SE)

weather_l = Label(app, text = "", font = text_font, bg = bg, fg = fg)
weather_l.pack(padx = 100, pady = 10, side = tkinter.BOTTOM, anchor = SE)

# clock label

time_lbl = Label(app, font = text_font, bg = bg, fg = fg)
time_lbl.pack(padx = 100, pady = 50, side = tkinter.TOP, anchor = NE)



weatherWorker()
clockWorker()


app.mainloop()



