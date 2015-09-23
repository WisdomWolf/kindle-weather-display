#!/bin/sh

cd "$(dirname "$0")"

python2 weather-script.py
rsvg-convert --background-color=white -o weather-script.png weather-script-output.svg
pngcrush -c 0 -ow weather-script.png weather-script-output.png
/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload weather-script-output.png /Apps/kindle-weather/weather-script-output.png
