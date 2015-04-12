__author__ = 'xuepeng'


################Destination##################
DESTINATION_ALL = "all"

####################Type#####################
TYPE_MONITOR_CAR = "monitor_car"
TYPE_CAR_CAR = "car_car"
TYPE_CUSTOMIZED = "customized"

###################SubType####################
SUBTYPE_SETTING = "setting"
SUBTYPE_BATCH = "batch"
SUBTYPE_CMD = "cmd"
SUBTYPE_ACK = "ack"

################Monitor_Car##################
SETTINGS_NAME_STYLE = "style"
SETTINGS_NAME_STYLE_FOLLOW = "follow"
SETTINGS_NAME_STYLE_LEAD = "lead"
SETTINGS_NAME_STYLE_FREE = "free"
SETTINGS_NAME_STYLE_CUSTOMIZED = "customized"
SETTINGS_NAME_MINI_INTERVAL = 'mini_interval'

COMMAND_NAME_SAFE_MODE = "safe_mode"
COMMAND_NAME_FULL_MODE = "full_mode"
COMMAND_NAME_RESTART = "restart"
COMMAND_NAME_SHUT_DOWN = "shutdown"
COMMAND_NAME_GO = 'go'
COMMAND_NAME_GO_TO = 'go_to'
COMMAND_NAME_PLUGIN = 'plugin'
COMMAND_NAME_STOP = 'stop'
COMMAND_NAME_DISABLE_PLUGIN = 'disable_plugin'
COMMAND_NAME_ASK_PLUGIN = 'ask_plugin'
COMMAND_NAME_RESPONSE_PLUGIN = 'response_plugin'
COMMAND_NAME_FOLLOW = 'follow'
COMMAND_NAME_SET_POS = 'set_pos'

BATCH_FLOW_START = "start"
BATCH_FLOW_JOB = "job"
BATCH_FLOW_END = "end"
BATCH_JOB_ACTION_NAME_GO = "go"
BATCH_JOB_ACTION_NAME_PAUSE = "pause"

#################Car_Car#####################
ACTION_NAME_GO = "go"
ACTION_NAME_PAUSE = "pause"

class EventAction:
    def __init__(self, name=None, arg1=None, arg2=None):
        self.name = name
        self.arg1 = arg1
        self.arg2 = arg2

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
    def __init__(self, name=None, arg1=None, arg2=None, time=0):
        self.action = EventAction(name, arg1, arg2)
        self.time = time

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
        self.msg_obj = None

    def set_origin_msg(self, msg_obj):
        self.msg_obj = msg_obj

    def set_source(self, source):
        self.source = source

    def set_destination(self, destination):
        self.destination = destination

    def set_type(self, type):
        self.type = type

    def self_parse(self):
        raise "Not implemented!"


class Car_CarEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self.action = None
        self.coordinates = None

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

    def self_parse(self):
        if self.msg_obj:
            car_car_obj = self.msg_obj[TYPE_CAR_CAR]
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
            self.set_action(action)
            self.set_coor(coor)


class EventSetting:
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value


class EventCommand:
    def __init__(self, name=None, args=None):
        self.name = name
        self.args = args


class EventBatch:
    def __init__(self, name=None, arg1=None, arg2=None, time=None):
        self.job = EventJob(name, arg1, arg2, time)


class Monitor_CarEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self.seq = None
        self.sub_type = None
        self.setting = None
        self.command = None
        self.batch = None

    def self_parse(self):
        if self.msg_obj:
            # print self.msg_obj
            monitor_car_obj = self.msg_obj[TYPE_MONITOR_CAR]
            self.seq = self.msg_obj['seq']
            self.sub_type = self.msg_obj['subtype']
            if self.sub_type == SUBTYPE_SETTING:
                setting_obj = monitor_car_obj['setting']
                self.setting = EventSetting(setting_obj['name'], setting_obj['value'])
            elif self.sub_type == SUBTYPE_CMD:
                cmd_obj = monitor_car_obj['cmd']
                self.command = EventCommand(cmd_obj['name'], cmd_obj['args'])
            elif self.sub_type == SUBTYPE_BATCH:
                batch_obj = monitor_car_obj['batch']
                job_obj = batch_obj['job']
                action_obj = job_obj['action']
                time = job_obj['time']
                self.batch = EventBatch(action_obj['name'], action_obj['arg1'], action_obj['arg2'], time)
            elif self.sub_type == SUBTYPE_ACK:
                self.seq = self.msg_obj['seq']


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
