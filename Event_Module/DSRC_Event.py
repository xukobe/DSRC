__author__ = 'xuepeng'


################Destination##################
DESTINATION_ALL = "all"

####################Type#####################
TYPE_MONITOR_CAR = "vi"    # v2i
TYPE_CAR_CAR = "vv"        # v2v
TYPE_CUSTOMIZED = "ctm"    # customized

###################SubType####################
SUBTYPE_SETTING = "st"           # setting
SUBTYPE_BATCH = "bt"          # batch
SUBTYPE_CMD = "cmd"
SUBTYPE_ACK = "ack"

################Monitor_Car##################
SETTINGS_NAME_STYLE = "st"               # style
SETTINGS_NAME_STYLE_FOLLOW = "f"       # follow
SETTINGS_NAME_STYLE_LEAD = "l"           # lead
SETTINGS_NAME_STYLE_FREE = "fr"          # free
SETTINGS_NAME_STYLE_CUSTOMIZED = "ctm"     # customized
SETTINGS_NAME_MINI_INTERVAL = 'mi'      # minimal interval

COMMAND_NAME_SAFE_MODE = "sm"          # safe mode
COMMAND_NAME_FULL_MODE = "fm"          # full mode
COMMAND_NAME_RESTART = "rst"       # restart
COMMAND_NAME_SHUT_DOWN = "sd"       # shutdown
COMMAND_NAME_GO = 'go'
COMMAND_NAME_GO_TO = 'gt'           # got to
COMMAND_NAME_PLUGIN = 'p'           # plugin
COMMAND_NAME_STOP = 'stp'          # stop
COMMAND_NAME_DISABLE_PLUGIN = 'dp'     # disable plugin
COMMAND_NAME_ASK_PLUGIN = 'ap'         # ask for plugin
COMMAND_NAME_RESPONSE_PLUGIN = 'rp'             # response plugin
COMMAND_NAME_FOLLOW = 'f'                 # follow
COMMAND_NAME_SET_POS = 'sp'              # set position

BATCH_FLOW_START = "st"              # start
BATCH_FLOW_JOB = "j"                 # job
BATCH_FLOW_END = "e"                 # end
BATCH_JOB_ACTION_NAME_GO = "go"
BATCH_JOB_ACTION_NAME_PAUSE = "p"    #pause

#################Car_Car#####################
ACTION_NAME_GO = "go"
ACTION_NAME_PAUSE = "p"              # pause

###############Keys###########################
KEY_SOURCE = 'sr'                  # source
KEY_DESTINATION = 'dst'             # destination

KEY_V2V = 'vv'                      # v2v
KEY_V2I = 'vi'                      # v2i

KEY_TYPE = 'tp'                     # type
KEY_SUBTYPE = 'stp'                  # subtype

KEY_ACTION = 'a'                    # action
KEY_COORDINATE = 'c'                # coordinate
KEY_NAME = 'n'                      # name
KEY_ARG1 = 'a1'                     # arg1
KEY_ARG2 = 'a2'                     # arg2
KEY_X = 'x'
KEY_Y = 'y'
KEY_RADIAN = 'r'                    # radian
KEY_POWER = 'pw'                    # power
KEY_RATE = 'rt'                     # rate
KEY_INTERVAL = 'it'                 # interval
KEY_BUMP = 'b'                      # bump
KEY_DROP = 'd'                      # drop

KEY_SEQUENCE = 'sq'                 # sequence
KEY_SETTING = 'st'                  # setting
KEY_VALUE = 'v'                     # value
KEY_CMD = 'cmd'                     # command
KEY_ARGS = 'ag'                     # args
KEY_BATCH = 'bt'                    # batch
KEY_JOB = 'j'                       # job
KEY_TIME = 'tm'                     # time

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
        self.power = None
        self.rate = None
        self.interval = None
        self.bump = None
        self.drop = None

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
            action_event = car_car_obj[KEY_ACTION]
            coor_event = car_car_obj[KEY_COORDINATE]
            action = EventAction()
            coor = EventCoordinates()
            action.set_name(action_event[KEY_NAME])
            action.set_arg1(action_event[KEY_ARG1])
            action.set_arg2(action_event[KEY_ARG2])
            coor.set_x(coor_event[KEY_X])
            coor.set_y(coor_event[KEY_Y])
            coor.set_radian(coor_event[KEY_RADIAN])
            self.set_action(action)
            self.set_coor(coor)
            self.power = self.msg_obj[KEY_POWER]
            self.rate = self.msg_obj[KEY_RATE]
            self.interval = self.msg_obj[KEY_INTERVAL]
            self.bump = self.msg_obj[KEY_BUMP]
            self.drop = self.msg_obj[KEY_DROP]


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
            monitor_car_obj = self.msg_obj[TYPE_MONITOR_CAR]
            try:
                self.seq = self.msg_obj[KEY_SEQUENCE]
            except Exception, e:
                pass
            self.sub_type = self.msg_obj[KEY_SUBTYPE]
            if self.sub_type == SUBTYPE_SETTING:
                setting_obj = monitor_car_obj[KEY_SETTING]
                self.setting = EventSetting(setting_obj[KEY_NAME], setting_obj[KEY_VALUE])
            elif self.sub_type == SUBTYPE_CMD:
                cmd_obj = monitor_car_obj[KEY_CMD]
                self.command = EventCommand(cmd_obj[KEY_NAME], cmd_obj[KEY_ARGS])
            elif self.sub_type == SUBTYPE_BATCH:
                batch_obj = monitor_car_obj[KEY_BATCH]
                job_obj = batch_obj[KEY_JOB]
                action_obj = job_obj[KEY_ACTION]
                time = job_obj[KEY_TIME]
                self.batch = EventBatch(action_obj[KEY_NAME], action_obj[KEY_ARG1], action_obj[KEY_ARG2], time)
            elif self.sub_type == SUBTYPE_ACK:
                self.seq = self.msg_obj[KEY_SEQUENCE]


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
