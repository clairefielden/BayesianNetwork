import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from pyAgrum import pyAgrum
from pylab import *
import pyAgrum as gum
import requests
import lxml
import graphviz
import matplotlib.pyplot as plt
import os
import pyAgrum.lib.notebook as gnb
import argparse

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
# US english
LANGUAGE = "en-US,en;q=0.5"

def get_weather_data(url):
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html = session.get(url)
    # create a new soup
    soup = bs(html.text, "html.parser")
    # store all results on this dictionary
    result = {}
    # extract region
    # extract temperature now
    result['temp_now'] = soup.find("span", attrs={"id": "wob_tm"}).text
    # get the day and hour now
    result['dayhour'] = soup.find("div", attrs={"id": "wob_dts"}).text
    # get the actual weather
    result['weather_now'] = soup.find("span", attrs={"id": "wob_dc"}).text
    # get the precipitation
    result['precipitation'] = soup.find("span", attrs={"id": "wob_pp"}).text
    # get the % of humidity
    result['humidity'] = soup.find("span", attrs={"id": "wob_hm"}).text
    # extract the wind
    result['wind'] = soup.find("span", attrs={"id": "wob_ws"}).text
    city = "san+francisco"
    url = "https://www.google.com/search?q=" + "wind" + city
    # requests instance
    html = requests.get(url).content
    soup = bs(html, 'html.parser')
    listdiv = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
    # particular list with required data
    # formatting the string
    strd2 = listdiv[5].text
    w = strd2.split(";")
    #print(w)
    for x in w:
        if "mph" in x:
            dir = x.split(" ")
            #print(dir)
            result["dir"] = dir[6]
            break
    return result


#SETTING UP bn
# creates an empty BN network with a 'name' property
bn=gum.BayesNet('Surf?')
print(bn)
#create variables
swell=bn.add(gum.LabelizedVariable('swell','swell ?',2))
wind=bn.add(gum.LabelizedVariable('wind','windy ?',2))
tide=bn.add(gum.LabelizedVariable('tide','tide ?',2))
temp=bn.add(gum.LabelizedVariable('temp','temperature ?',2))
shark=bn.add(gum.LabelizedVariable('shark','shark ?',2))
wave=bn.add(gum.LabelizedVariable('wave','waves ?',2))
surf=bn.add(gum.LabelizedVariable('surf','surf ?',2))
print(bn)
# c contains 2 values and described as 'cloudy?', and it will add it to the BN.
# The value returned is the id of the node in the graphical structure (the DAG)
# pyAgrum actually distinguishes the random variable (here the labelizedVariable) from its node in the DAG
# the latter is identified through a numeric id
# Of course, pyAgrum provides functions to get the id of a node given the corresponding variable

#Add arcs
for link in [(swell,wind),(tide,wave)]:
    bn.addArc(*link)

for link in [(temp,shark)]:
    bn.addArc(*link)

for link in [(wave,surf),(wind,surf), (temp, surf), (shark, surf)]:
    bn.addArc(*link)

print("SURF METRICS FOR Station 46237 - San Francisco Bar, CA (142)")

#Finding wind speed & direction
URL = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=weather"
region = "san francisco beach"
if region:
    region = region.replace(" ", "+")
    URL += f"+{region}"
# get data
data = get_weather_data(URL)
# print data
print("Now:", data["dayhour"])
print(f"Temperature now: {data['temp_now']}°C")
print("Description:", data['weather_now'])
print("Precipitation:", data["precipitation"])
print("Humidity:", data["humidity"])
print("Wind speed:", data["wind"])
print("Wind direction:", data["dir"])

headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}

params = {
    "q": "san francisco weather",
    "hl": "en",
    "gl": "us"
}

response = requests.get('https://www.google.com/search', headers=headers, params=params).text
soup = bs(response, 'lxml')

for weather_result in soup.select('.wob_noe .wob_hw'):
    try:
        wind_speed = weather_result.select_one('.wob_t').text
        wind_direction = ' '.join(weather_result.select_one('.wob_t')['aria-label'].split(' ')[2:4])

        print(f"{wind_speed}\n{wind_direction}\n")

    except:
        pass  # or None instead

#Station 46237 - San Francisco Bar, CA (142)
Bouy = pd.read_csv('https://www.ndbc.noaa.gov/data/realtime2/46237.spec', delim_whitespace=True)
#Bouy.head()
Bouy = Bouy.drop([0])
#to_drop =['WDIR','WSPD','GST', 'PRES','ATMP', 'DEWP','VIS', 'PTDY','TIDE']
#Bouy = Bouy.drop(to_drop, axis=1)
#print(Bouy.head())

#WDIR = wind direction
wdir = 0
#WSPD = wind speed (m/s)
wspd = 0
#WVHT = wave height (m)
tides=[100,-1]
times = [1,2]
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
        #find the min
        tides[0] = float(Bouy.iloc[i][5])
        times[0] = Bouy.iloc[i][3]
    elif float(Bouy.iloc[i][5]) > tides[1] and Bouy.iloc[i][3] not in times:
        #find the max
        tides[1] = float(Bouy.iloc[i][5])
        times[1] = Bouy.iloc[i][3]

    if float(Bouy.iloc[i][6])>=1.5 and float(Bouy.iloc[i][6])<4:
        swh = swh+1
    if float(Bouy.iloc[i][7])>=10 and float(Bouy.iloc[i][7])<=20:
        swp = swp+1
    #count the number of times west appears in direction
    if 'W' in Bouy.iloc[i][10]:
        swd=swd+1

#PROBABILITY OF GOOD SWELL:
swell_score = (swh+swp+swd)/144
print("The swell score is: ", round(swell_score*100, 2), "%")
#over the past 24 hours, if swell is more than 1.5m & less than 4m
#if swell period is between 10 and 20 seconds
#for San Fran, ideally from west

#PROBABILITY OF TIDE
times.sort()
#print(times)
high_tide_1 = int(times[1])
low_tide_1 = int(times[0])
high_tide_2 = high_tide_1-6

if high_tide_2<0:
    high_tide_2 = high_tide_1+6

#assume daylight hours of 5AM => 7PM
interval_high_1 = [high_tide_1-1.5, high_tide_1+1.5] #18=>21
interval_high_2 = [high_tide_2-1.5, high_tide_2+1.5] #6=>9
#these are the intervals of the day during which it will be high tide
intervals = interval_high_1+interval_high_2
#print(intervals)
for i in intervals:
    if i<0:
        intervals[intervals.index(i)] = 12-abs(i)
    elif i>23.5:
        intervals[intervals.index(i)] = 24-i

#print(intervals)
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
good_wind = 0
index = 0
if 'W' in data["dir"]:
    good_wind = 1
elif 'N' in data["dir"] or 'S' in data["dir"]:
    good_wind = 0.5
wind_speed = data["wind"].split(" ")
if(int(wind_speed[0])<=10):
    good_wind = good_wind+1
print("THE PROBABILITY OF GOOD WIND IS ",good_wind,"/ 2")
wind_probability = good_wind/2;

swell_score_1 = double(swell_score)
swell_score_0 = double(1-swell_score_1)
#fill the cpt
bn.cpt(swell).fillWith(swell_score_0, swell_score_1)
bn.cpt(wind).fillWith(1-good_wind, good_wind)
bn.cpt(tide).fillWith(1-tide_probability, tide_probability)
bn.cpt(temp).fillWith(0.57, 0.43)
bn.cpt(shark).fillWith(0.97, 0.03)

print(bn)