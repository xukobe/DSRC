__author__ = 'xuepeng'

from Event_Module import DSRC_Event
import time
# Must implement

do = False
execute_time = 0
time_duration = 30

def customized_event_handler(dsrc_unit, event):
    if event.type == DSRC_Event.TYPE_CUSTOMIZED:
        current_time = time.time()
        if current_time - execute_time > 30:
            global do
            do = event.do_it


def print_receiver():
    print "I am a DSRC_Plugin_Receiver."