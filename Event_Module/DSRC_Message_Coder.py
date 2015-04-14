__author__ = 'xuepeng'

import json
from Event_Module import DSRC_Event

class MessageCoder:
    def __init__(self):
        pass

    @staticmethod
    def decode(msg_str):
        json_obj = json.loads(msg_str)
        return json_obj

    @staticmethod
    def encode( msg_obj):
        msg = json.dumps(msg_obj)
        return msg


    @staticmethod
    def generate_car_car_message(source, destination, action_name, action_arg1, action_arg2, coor_x, coor_y, coor_radian, power, rate, interval, bump, drop):
        msg_obj = {}
        msg_obj[DSRC_Event.KEY_SOURCE] = source
        msg_obj[DSRC_Event.KEY_DESTINATION] = destination
        msg_obj[DSRC_Event.KEY_TYPE] = DSRC_Event.TYPE_CAR_CAR
        msg_obj_car = {}
        msg_obj_action = {}
        msg_obj_action[DSRC_Event.KEY_NAME] = action_name
        msg_obj_action[DSRC_Event.KEY_ARG1] = action_arg1
        msg_obj_action[DSRC_Event.KEY_ARG2] = action_arg2
        msg_obj_coor = {}
        msg_obj_coor[DSRC_Event.KEY_X] = coor_x
        msg_obj_coor[DSRC_Event.KEY_Y] = coor_y
        msg_obj_coor[DSRC_Event.KEY_RADIAN] = coor_radian
        msg_obj_car[DSRC_Event.KEY_ACTION] = msg_obj_action
        msg_obj_car[DSRC_Event.KEY_COORDINATE] = msg_obj_coor
        msg_obj[DSRC_Event.KEY_V2V] = msg_obj_car
        msg_obj[DSRC_Event.KEY_POWER] = power
        msg_obj[DSRC_Event.KEY_RATE] = rate
        msg_obj[DSRC_Event.KEY_INTERVAL] = interval
        msg_obj[DSRC_Event.KEY_BUMP] = bump
        msg_obj[DSRC_Event.KEY_DROP] = drop
        # msg = MessageCoder.encode(msg_obj)
        return msg_obj

    @staticmethod
    def generate_setting_message(source, destination, setting_name, value):
        msg_obj = {}
        msg_obj[DSRC_Event.KEY_SOURCE] = source
        msg_obj[DSRC_Event.KEY_DESTINATION] = destination
        msg_obj[DSRC_Event.KEY_TYPE] = DSRC_Event.TYPE_MONITOR_CAR
        msg_obj[DSRC_Event.KEY_SUBTYPE] = DSRC_Event.SUBTYPE_SETTING
        msg_obj_monitor_car = {}
        msg_obj_setting = {}
        msg_obj_setting[DSRC_Event.KEY_NAME] = setting_name
        msg_obj_setting[DSRC_Event.KEY_VALUE] = value
        msg_obj_monitor_car[DSRC_Event.KEY_SETTING] = msg_obj_setting
        msg_obj[DSRC_Event.KEY_V2I] = msg_obj_monitor_car
        # msg = MessageCoder.encode(msg_obj)
        return msg_obj

    @staticmethod
    def generate_command_message(source, destination, cmd, args):
        msg_obj = {}
        msg_obj[DSRC_Event.KEY_SOURCE] = source
        msg_obj[DSRC_Event.KEY_DESTINATION] = destination
        msg_obj[DSRC_Event.KEY_TYPE] = DSRC_Event.TYPE_MONITOR_CAR
        msg_obj[DSRC_Event.KEY_SUBTYPE] = DSRC_Event.SUBTYPE_CMD
        msg_obj_monitor_car = {}
        msg_obj_cmd = {}
        msg_obj_cmd[DSRC_Event.KEY_NAME] = cmd
        msg_obj_cmd[DSRC_Event.KEY_ARGS] = args
        msg_obj_monitor_car[DSRC_Event.KEY_CMD] = msg_obj_cmd
        msg_obj[DSRC_Event.KEY_V2I] = msg_obj_monitor_car
        # msg = MessageCoder.encode(msg_obj)
        return msg_obj

    @staticmethod
    def generate_batch_processing(source, destination, job):
        msg_obj = {}
        msg_obj[DSRC_Event.KEY_SOURCE] = source
        msg_obj[DSRC_Event.KEY_DESTINATION] = destination
        msg_obj[DSRC_Event.KEY_TYPE] = DSRC_Event.TYPE_MONITOR_CAR
        msg_obj[DSRC_Event.KEY_SUBTYPE] = DSRC_Event.SUBTYPE_BATCH
        msg_obj_monitor_car = {}
        msg_obj_batch = {}
        msg_obj_job = {}
        msg_obj_action = {}
        msg_obj_action[DSRC_Event.KEY_NAME] = job.action.name
        msg_obj_action[DSRC_Event.KEY_ARG1] = job.action.arg1
        msg_obj_action[DSRC_Event.KEY_ARG2] = job.action.arg2
        msg_obj_job[DSRC_Event.KEY_ACTION] = msg_obj_action
        msg_obj_job[DSRC_Event.KEY_TIME] = job.time
        msg_obj_batch[DSRC_Event.KEY_JOB] = msg_obj_job
        msg_obj_monitor_car[DSRC_Event.KEY_BATCH] = msg_obj_batch
        msg_obj[DSRC_Event.KEY_V2I] = msg_obj_monitor_car
        # msg = MessageCoder.encode(msg_obj)
        return msg_obj

    @staticmethod
    def generate_monitor_car_ack(source, destination, seq):
        msg_obj = {}
        msg_obj[DSRC_Event.KEY_SOURCE] = source
        msg_obj[DSRC_Event.KEY_DESTINATION] = destination
        msg_obj[DSRC_Event.KEY_TYPE] = DSRC_Event.TYPE_MONITOR_CAR
        msg_obj[DSRC_Event.KEY_SUBTYPE] = DSRC_Event.SUBTYPE_ACK
        msg_obj[DSRC_Event.KEY_SEQUENCE] = seq
        msg_obj[DSRC_Event.KEY_V2I] = {}
        return msg_obj

def main():
    obj = {}
    obj['a'] = 'b'
    a = {'a': 'b'}
    obj['obj'] = a
    msg_str = MessageCoder.encode(obj)
    print msg_str

    str = "{\"a\": \"b\", \"obj\": {\"a\": \"b\"}}"
    msg_obj = MessageCoder.decode(str)
    print msg_obj['a']
    print msg_obj['obj']
    print msg_obj

if __name__ == '__main__':
    main()
