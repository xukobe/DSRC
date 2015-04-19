__author__ = 'xuepeng'

from Event_Module import DSRC_Event
from Event_Module.DSRC_Event import Event

# Must implement
class CustomizedEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self.do_it = False

    def self_parse(self):
        self.do_it = self.msg_obj["do"]



def print_event():
    print "I am a DSRC_Plugin_Event"