#!/usr/bin/python

from subprocess import *
import codecs
import time
import os

last_png = 0
retries = 0

# starting redraws above threshold to ensure full refresh at start
MAX_REDRAWS = 6
redraws = MAX_REDRAWS + 1


def run_cmd(cmd):
    process = Popen(cmd.split(), stdout=PIPE)
    output = process.communicate()[0]
    return output
    
def wait_for_next_minute(current=time.strftime('%M', time.localtime())):
    check_for_update()
    while True:
        if time.strftime('%M', time.localtime()) == current:
            continue
        else:
            check_for_update()
            # adding a 10 sec delay to ensure pi has time to update file
            time.sleep(10)
            efficient_time_update()
            break

def efficient_time_update():
    while True:
        time.sleep(60)
        check_for_update()
        
def check_for_update():
    global last_png
    global retries
    run_cmd("wget -q http://192.168.1.43/images/weather-script-output.png -O weather.png")
    output = os.stat('weather.png').st_mtime
    if output == last_png and retries < 10:
        retries += 1
        time.sleep(5)
        check_for_update()
    elif retries < 10:
        retries = 0
        last_png = output
        update_screen()
    else:
        print("Aborting due to too many retries")
        os._exit(0)

def update_screen():
    global redraws
    if redraws <= MAX_REDRAWS:
        print("updating screen at {0}".format(time.strftime("%c", time.localtime())))
        run_cmd("eips -g /mnt/us/weather/weather.png")
        redraws += 1
    else:
        print("refreshing screen at {0}".format(time.strftime("%c", time.localtime())))
        run_cmd("eips -c")
        run_cmd("eips -c")
        run_cmd("eips -fg /mnt/us/weather/weather.png")
        redraws = 0
    
print("Script started at {0}".format(time.strftime("%c", time.localtime())))
wait_for_next_minute()
        