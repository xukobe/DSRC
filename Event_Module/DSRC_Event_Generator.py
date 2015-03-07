__author__ = 'xuepeng'

from Queue import Queue
from threading import Thread

import DSRC_Plugins.DSRC_Plugin_Invoker as Plugin
from DSRC_Messager_Module.DSRC_USRP_Connector import ConnectorInterface
from DSRC_Event import *
from DSRC_Message_Coder import *

class USRPEventHandler(Thread, EventGenerator, ConnectorInterface):
    def __init__(self, customized_event=False):
        Thread.__init__(self)
        self.customized_event = customized_event
        self.event_queue = Queue()
        self.running = True
        self.start()

    def msg_received(self, msg):
        # print msg
        self.event_queue.put(msg)

    def run(self):
        while self.running:
            event_msg = self.event_queue.get()
            if event_msg == "QUIT":
                break
            try:
                event_obj = MessageCoder.decode(event_msg)
                event = self.parse_event(event_obj)
                self.listener.usrp_event_received(event)
            except ValueError, e:
                pass
        print "Event handler is stopped!"

    def stop_self(self):
        self.event_queue.put_nowait("QUIT")
        self.running = False

    def parse_event(self, event_obj):
        """
        :rtype : Event
        :param event_obj: event object to parse
        :type event_obj: dict
        """
        event = None

        if event_obj["type"] == TYPE_CAR_CAR:
            event = Car_CarEvent()
            event.set_origin_msg(event_obj)
            event.self_parse()
        elif event_obj["type"] == TYPE_MONITOR_CAR:
            event = Monitor_CarEvent()
            event.set_origin_msg(event_obj)
            event.self_parse()
        elif event_obj["type"] == TYPE_CUSTOMIZED:
            # if self.customized_event:
            event = Plugin.customized_generate_event()
            event.set_origin_msg(event_obj)
            event.self_parse()

        if event:
            event.source = event_obj['source']
            event.destination = event_obj['destination']
            event.type = event_obj['type']

        return event