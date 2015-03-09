__author__ = 'xuepeng'

from Event_Module import DSRC_Event
# Must implement

def customized_event_handler(dsrc_unit, event):
    if event.type == DSRC_Event.TYPE_CUSTOMIZED:
        print "Plugin customized event received"


def print_receiver():
    print "I am a DSRC_Plugin_Receiver."