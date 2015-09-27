#!/bin/sh

FRONTLIGHTDEVICE=/sys/devices/system/fl_tps6116x/fl_tps6116x0/fl_intensity
FRAMEWORK=$(ps -A | grep framework)

if [ -z "$FRAMEWORK" ] ; then
	stop lab126_gui
fi

lipc-set-prop com.lab126.powerd preventScreenSaver 1
echo -n 0 > $FRONTLIGHTDEVICE
/mnt/us/weather/display-weather.sh