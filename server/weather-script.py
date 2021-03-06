#!/usr/bin/python2

# Kindle Weather Display
# Matthew Petroff (http://mpetroff.net/)
# September 2012

from xml.dom import minidom
import datetime
import time
import codecs
import os
from subprocess import *
try:
    # Python 3
    from urllib.request import urlopen, URLError
except ImportError:
    # Python 2
    from urllib2 import urlopen, URLError
    
LATITUDE = 39.3286
LONGITUDE = -76.6169
LAST_HIGHS = 0
LAST_LOWS = 0
LAST_ICONS = None


def fetch_weather_data(latitude, longitude):
    weather_xml = urlopen('http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?whichClient=NDFDgenByDay&lat=' + str(latitude) + '&lon=' + str(longitude) + '&format=24+hourly&numDays=4&Unit=e').read()
    return minidom.parseString(weather_xml)

def parse_temperatures(dom):
    xml_temperatures = dom.getElementsByTagName('temperature')
    highs = [None]*4
    lows = [None]*4
    for item in xml_temperatures:
        if item.getAttribute('type') == 'maximum':
            values = item.getElementsByTagName('value')
            for i in range(len(values)):
                highs[i] = int(values[i].firstChild.nodeValue)
        if item.getAttribute('type') == 'minimum':
            values = item.getElementsByTagName('value')
            for i in range(len(values)):
                lows[i] = int(values[i].firstChild.nodeValue)
                
    return highs,lows

def parse_icons(dom):
    xml_icons = dom.getElementsByTagName('icon-link')
    icons = [None]*4
    for i in range(len(xml_icons)):
        icons[i] = xml_icons[i].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789')
        
    return icons

def parse_dates(dom):
    xml_day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
    return datetime.datetime.strptime(xml_day_one, '%Y-%m-%d')

def process_svg(highs, lows, icons, include_forecast=False):
    
    output = codecs.open('weather-script-base.svg', 'r', encoding='utf-8').read()
    # Insert icons and temperatures
    output = output.replace('ICON_TWO',icons[0])
    output = output.replace('HIGH',str(highs[0])).replace('LOW',str(lows[0]))

    output = output.replace('PI_TEMP', str(get_pi_temp())).replace('REMOTE_TEMP', str(get_remote_arduino_temp()))
    output = output.replace('REMOTE_HUM', str(get_remote_arduino_humid()))

    # Set Clock
    output = output.replace('CLOCK',time.strftime('%I:%M %p', time.localtime()).lstrip('0'))

    # Write output
    codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)
    
def run_cmd(cmd):
    process = Popen(cmd.split(), stdout=PIPE)
    output = process.communicate()[0]
    return output

def create_png(include_forecast=False):
    global LAST_HIGHS, LAST_LOWS, LAST_ICONS
    if include_forecast:
        weather_data = fetch_weather_data(LATITUDE, LONGITUDE)
        LAST_HIGHS,LAST_LOWS = highs,lows = parse_temperatures(weather_data)
        LAST_ICONS = icons = parse_icons(weather_data)
        day_one = parse_dates(weather_data)
    else:
        highs,lows,icons= LAST_HIGHS,LAST_LOWS,LAST_ICONS
        
    process_svg(highs, lows, icons, include_forecast)
    
    if os.name == 'posix':
        run_cmd("rsvg-convert --background-color=white -o weather-script.png weather-script-output.svg")
        run_cmd("pngcrush -c 0 -ow weather-script.png weather-script-output.png")
        run_cmd("cp /home/pi/kindle-weather-display/server/weather-script-output.png /var/www/images/weather-script-output.png")
    
    print("Uploading png. {0}".format(time.strftime("%c", time.localtime())))
    
def get_pi_temp():
    return 74
    
def get_remote_arduino_temp():
    try:
        tempf = float(urlopen("http://192.168.1.70/tempf").read())
        return round(tempf, 1)
    except URLError:
        return 'ERR'
    except:
        return 'N/A'
    
def get_remote_arduino_humid():
    try:
        hum = float(urlopen("http://192.168.1.70/humidity").read())
        return round(hum)
    except URLError:
        return 'ERR'
    except:
        return 'N/A'
    
def wait_for_next_minute(current=time.strftime('%M', time.localtime())):
    while True:
        if time.strftime('%M', time.localtime()) == current:
            continue
        else:
            create_png(True)
            efficient_time_update()
            break

def efficient_time_update():
    while True:
        time.sleep(56)
        this_minute = time.strftime('%M', time.localtime()) 
        if this_minute == 0:
            create_png(True)
            wait_for_next_minute()
            break
        else:
            create_png(False)

def main():    
	create_png(True)
	wait_for_next_minute()

if __name__ == "__main__":
	main()
    
