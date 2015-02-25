__author__ = 'xuepeng'

from Event_Module import DSRC_Event
from Event_Module.DSRC_Event import Event


class CustomizedEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self.customized_action = None

    def self_parse(self):
        customized_obj = self.msg_obj[DSRC_Event.TYPE_CUSTOMIZED]
        self.customized_action = customized_obj["customized_action"]



def print_event():
    print "I am a DSRC_Plugin_Event"