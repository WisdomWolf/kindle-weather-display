#!/usr/bin/python2

# Kindle Weather Display
# Matthew Petroff (http://mpetroff.net/)
# September 2012

from xml.dom import minidom
import datetime
import time
import codecs
try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen

#
# Geographic location
#

latitude = 39.3286
longitude = -76.6169



#
# Download and parse weather data
#

# Fetch data (change lat and lon to desired location)
weather_xml = urlopen('http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?whichClient=NDFDgenByDay&lat=' + str(latitude) + '&lon=' + str(longitude) + '&format=24+hourly&numDays=4&Unit=e').read()
dom = minidom.parseString(weather_xml)

# Parse temperatures
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

# Parse icons
xml_icons = dom.getElementsByTagName('icon-link')
icons = [None]*4
for i in range(len(xml_icons)):
    icons[i] = xml_icons[i].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789')

# Parse dates
xml_day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
day_one = datetime.datetime.strptime(xml_day_one, '%Y-%m-%d')



#
# Preprocess SVG
#

# Open SVG to process
output = codecs.open('weather-script-base.svg', 'r', encoding='utf-8').read()

# Insert icons and temperatures
output = output.replace('ICON_TWO',icons[0])
output = output.replace('HIGH',str(highs[0])).replace('PI_TEMP','74').replace('REMOTE_TEMP','68')
output = output.replace('LOW',str(lows[0])).replace('REMOTE_HUM','100')

# Set Clock
output = output.replace('CLOCK',time.strftime('%I:%M %p', time.localtime()).lstrip('0'))

# Write output
codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)
