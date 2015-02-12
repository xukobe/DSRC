__author__ = 'xuepeng'

from DSRC_USRP_Connector import ConnectorInterface
from DSRC_Message_Coder import MessageCoder
from Queue import Queue
from threading import Thread


################Destination##################
DESTINATION_ALL = "all"

####################Type#####################
TYPE_MONITOR_CAR = "monitor_car"
TYPE_CAR_CAR = "car_car"

################Monitor_Car##################
SETTINGS_NAME_STYLE = "style"
SETTINGS_NAME_STYLE_FOLLOW = "follow"
SETTINGS_NAME_STYLE_LEAD = "lead"
SETTINGS_NAME_STYLE_FREE = "free"

COMMAND_NAME_SAFE_MODE = "safe_mode"
COMMAND_NAME_FULL_MODE = "full_mode"
COMMAND_NAME_RESTART = "restart"
COMMAND_NAME_SHUT_DOWN = "shutdown"

BATCH_FLOW_START = "start"
BATCH_FLOW_JOB = "job"
BATCH_FLOW_END = "end"
BATCH_JOB_ACTION_NAME_GO = "go"
BATCH_JOB_ACTION_NAME_PAUSE = "pause"

#################Car_Car#####################
ACTION_NAME_GO = "go"
ACTION_NAME_PAUSE = "pause"

class EventAction:
    def __init__(self):
        self.name = None
        self.arg1 = None
        self.arg2 = None

    def set_name(self, name):
        self.name = name

    def set_arg1(self, arg1):
        self.arg1 = arg1

    def set_arg2(self, arg2):
        self.arg2 = arg2


class EventCoordinates:
    def __init__(self):
        self.x = None
        self.y = None
        self.radian = None

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_radian(self, radian):
        self.radian = radian


class EventJob:
    def __init__(self):
        self.action = None
        self.time = 0

    def set_action(self, action):
        """
        :param action: Event action
        :type action: EventAction
        """
        self.action = action

    def set_time(self, time):
        self.time = time


class Event:
    def __init__(self):
        self.source = None
        self.destination = None
        self.type = None
        self.action = None
        self.coordinates = None

    def set_source(self, source):
        self.source = source

    def set_destination(self, destination):
        self.destination = destination

    def set_type(self, type):
        self.type = type

    def set_action(self, action):
        """
        :param action: car_car action
        """
        self.action = action

    def set_coor(self, coor):
        """
        :param coor: car_car coor
        """
        self.coordinates = coor

    @staticmethod
    def parse_event(event_obj):
        """
        :rtype : Event
        :param event_obj: event object to parse
        :type event_obj: dict
        """
        event = Event()
        event.source = event_obj['source']
        event.destination = event_obj['destination']
        event.type = event_obj['type']
        if event.type == TYPE_CAR_CAR:
            car_car_obj = event_obj[TYPE_CAR_CAR]
            action_event = car_car_obj['action']
            coor_event = car_car_obj['coor']
            action = EventAction()
            coor = EventCoordinates()
            action.set_name(action_event['name'])
            action.set_arg1(action_event['arg1'])
            action.set_arg2(action_event['arg2'])
            coor.set_x(coor_event['x'])
            coor.set_y(coor_event['y'])
            coor.set_radian(coor_event['radian'])
            event.set_action(action)
            event.set_coor(coor)
        elif event.type == TYPE_MONITOR_CAR:
            pass
        return event

class EventGenerator:
    def __init__(self):
        self.listener = None

    def set_listener(self, listener):
        """
        :type listener: EventListener
        """
        self.listener = listener

class EventListener:
    def __init__(self):
        pass

    def usrp_event_received(self, event):
        raise NotImplementedError( "USRP event listener is not implemented." )

    def irobot_event_received(self,event):
        raise NotImplementedError("iRobot event listener is not implemented")

class USRPEventHandler(Thread, EventGenerator, ConnectorInterface):
    def __init__(self):
        Thread.__init__(self)
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
            event_obj = MessageCoder.decode(event_msg)
            event = Event.parse_event(event_obj)
            self.listener.usrp_event_received(event)

    def stop_self(self):
        self.event_queue.put_nowait("QUIT")
        self.running = False