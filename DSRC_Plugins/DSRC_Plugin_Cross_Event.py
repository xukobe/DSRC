__author__ = 'xuepeng'

from Event_Module import DSRC_Event
from Event_Module.DSRC_Event import Event

# Must implement
class CustomizedEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self.subtype = None
        self.auto_set_up = False
        self.x = None
        self.y = None
        self.r = None
        self.seq = None

    def self_parse(self):
        self.subtype = self.msg_obj.get(DSRC_Event.KEY_SUBTYPE)
        if self.subtype == 'auto_setup':
            self.auto_set_up = self.msg_obj.get("auto_setup")
            self.x = self.msg_obj['x']
            self.y = self.msg_obj['y']
            self.r = self.msg_obj['r']