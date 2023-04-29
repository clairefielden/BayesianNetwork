import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates

#Finding wind speed & direction
# enter city name
city = "san+francisco+ocean+beach"
# create url
url = "https://www.google.com/search?q=" + "weather" + city
# requests instance
html = requests.get(url).content
# getting raw data
soup = BeautifulSoup(html, 'html.parser')
# get the temperature
temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
# this contains time and sky description
str = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
# format the data
data = str.split('\n')
time = data[0]
sky = data[1]
# list having all div tags having particular class name
listdiv = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
# particular list with required data
strd = listdiv[5].text
# formatting the string
pos = strd.find('Wind')
other_data = strd[pos:].split(" ")
# printing all the data
print("Temperature: ", temp)
print("Sky Description: ", sky)

wind_dir = other_data[0].split('d')
good_wind= 0
if 'W' in wind_dir[1]:
    good_wind = 1
elif 'N' in wind_dir[1] or 'S' in wind_dir[1]:
    good_wind = 0.5

print("Wind Direction: ",wind_dir[1])
print("Wind speed: ",other_data[1])
if(int(other_data[1])<=10):
    good_wind = good_wind+1
#PROBABILITY OF GOOD WIND:
print("THE PROBABILITY OF GOOD WIND IS ",good_wind,"/ 2")
wind_probability = good_wind/2;

#Station 46237 - San Francisco Bar, CA (142)
Bouy = pd.read_csv('https://www.ndbc.noaa.gov/data/realtime2/46237.spec', delim_whitespace=True)
#Bouy.head()
Bouy = Bouy.drop([0])
#to_drop =['WDIR','WSPD','GST', 'PRES','ATMP', 'DEWP','VIS', 'PTDY','TIDE']
#Bouy = Bouy.drop(to_drop, axis=1)
print(Bouy.head())

#WDIR = wind direction
wdir = 0
#WSPD = wind speed (m/s)
wspd = 0
#WVHT = wave height (m)
tides=[100,100,-1,-1]
times = [1,2,3,4]
#APD = average wave period
#SWH = swell hight
swh = 0
#SWP = swell period
swp = 0
#SWD = swell direction
swd = 0

for i in range(0,48):
    #calculate tides
    if float(Bouy.iloc[i][5])<tides[0] and Bouy.iloc[i][3] not in times:
        tides[0] = float(Bouy.iloc[i][5])
        times[0] = Bouy.iloc[i][3]
    elif float(Bouy.iloc[i][5])<tides[1] and Bouy.iloc[i][3] not in times:
        tides[1] = float(Bouy.iloc[i][5])
        times[1] = Bouy.iloc[i][3]
    elif float(Bouy.iloc[i][5]) > tides[2] and Bouy.iloc[i][3] not in times:
        tides[2] = float(Bouy.iloc[i][5])
        times[2] = Bouy.iloc[i][3]
    elif float(Bouy.iloc[i][5]) > tides[3] and Bouy.iloc[i][3] not in times:
        tides[3] = float(Bouy.iloc[i][5])
        times[3] = Bouy.iloc[i][3]

    if float(Bouy.iloc[i][6])>=1.5 and float(Bouy.iloc[i][6])<4:
        swh = swh+1
    if float(Bouy.iloc[i][7])>=10 and float(Bouy.iloc[i][7])<=20:
        swp = swp+1
    #count the number of times west appears in direction
    if 'W' in Bouy.iloc[i][10]:
        swd=swd+1

#PROBABILITY OF GOOD SWELL:
swell_score = (swh+swp+swd)/144
print("The swell score is: ")
print(swell_score)
#over the past 24 hours, if swell is more than 1.5m & less than 4m
#if swell period is between 10 and 20 seconds
#for San Fran, ideally from west
if swell_score>=0.67:
    print("GOOD SWELL")
else:
    print("BAD SWELL")

#PROBABILITY OF TIDE
high_tide_1 = (int(times[2])+int(times[3]))/2 #19:30
low_tide_1 = (int(times[0])+int(times[1]))/2 #3:30
high_tide_2 = high_tide_1-12 #7:30
low_tide_2 = low_tide_1+12 #15:30

#assume daylight hours of 5AM => 7PM
interval_high_1 = [high_tide_1-1.5, high_tide_1+1.5] #18=>21
interval_high_2 = [high_tide_2-1.5, high_tide_2+1.5] #6=>9

tide_tot = 0

if interval_high_1[1]>19:
    tide_tot_1 = 19-interval_high_1[0]
else:
    tide_tot_1 = interval_high_1[1]-interval_high_1[0]
if interval_high_2[0]<5:
    tide_tot_2 = 5-interval_high_2[0]
else:
    tide_tot_2 = interval_high_2[1]-interval_high_2[0]
tide_tot = tide_tot_1+tide_tot_2
#total of 14 possible hours
print("THE TIDE IS HIGH ",tide_tot,"/14 hours of the day")
tide_probability = tide_tot/14

#PROBABILITY OF WIND





"""
from bs4 import BeautifulSoup
import requests
import lxml
import smtplib
import os
from pysurfline import SpotForecast



params={
    "spotId":"5842041f4e65fad6a7708890",
    "days":7,
    "intervalHours":3,
    }
spot=SpotForecast(params,verbose=True)

print(spot.wave[:1])


html_text = requests.get('https://www.surf-forecast.com/breaks/Big-Bay/forecasts/latest/six_day').text

soup = BeautifulSoup(html_text, 'lxml')

jobs = soup.find_all('td', class_ ="forecast-table__cell forecast-table__cell--has-image")

jobs_string = str(jobs)

if 'alt="0"' in jobs_string or 'alt="8"' in jobs_string or 'alt="9"' in jobs_string or 'alt="10"' in jobs_string:
    print('Swell is up! Sending notification email now.')
else:
    print("Not today!")
"""