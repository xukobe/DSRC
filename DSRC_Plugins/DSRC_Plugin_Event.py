__author__ = 'xuepeng'

from Controller_Module.DSRC_Event import Event


class CustomizedEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self.customized_action = None

    def self_parse(self):
        self.customized_action = "GO"



def print_event():
    print "I am a DSRC_Plugin_Event"