#!/bin/sh

if [ $# -eq 0 ]
then
    python /etc/DSRC/DSRC_Main/main.py
else
then
    if [ "$1" = "simulation" ]
        then
            python /etc/DSRC/DSRC_Main/main.py simulation
    elif [ "$1" = "stationary" ]
        then
            python /etc/DSRC/DSRC_Main/main.py stationary


