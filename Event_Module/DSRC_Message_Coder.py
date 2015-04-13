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
        msg_obj['source'] = source
        msg_obj['destination'] = destination
        msg_obj['type'] = 'car_car'
        msg_obj_car = {}
        msg_obj_action = {}
        msg_obj_action['name'] = action_name
        msg_obj_action['arg1'] = action_arg1
        msg_obj_action['arg2'] = action_arg2
        msg_obj_coor = {}
        msg_obj_coor['x'] = coor_x
        msg_obj_coor['y'] = coor_y
        msg_obj_coor['radian'] = coor_radian
        msg_obj_car['action'] = msg_obj_action
        msg_obj_car['coor'] = msg_obj_coor
        msg_obj['car_car'] = msg_obj_car
        msg_obj['power'] = power
        msg_obj['rate'] = rate
        msg_obj['interval'] = interval
        msg_obj['bump'] = bump
        msg_obj['drop'] = drop
        return msg_obj

    @staticmethod
    def generate_setting_message(source, destination, setting_name, value):
        msg_obj = {}
        msg_obj['source'] = source
        msg_obj['destination'] = destination
        msg_obj['type'] = DSRC_Event.TYPE_MONITOR_CAR
        msg_obj['subtype'] = DSRC_Event.SUBTYPE_SETTING
        msg_obj_monitor_car = {}
        msg_obj_setting = {}
        msg_obj_setting['name'] = setting_name
        msg_obj_setting['value'] = value
        msg_obj_monitor_car['setting'] = msg_obj_setting
        msg_obj['monitor_car'] = msg_obj_monitor_car
        return msg_obj

    @staticmethod
    def generate_command_message(source, destination, cmd, args):
        msg_obj = {}
        msg_obj['source'] = source
        msg_obj['destination'] = destination
        msg_obj['type'] = DSRC_Event.TYPE_MONITOR_CAR
        msg_obj['subtype'] = DSRC_Event.SUBTYPE_CMD
        msg_obj_monitor_car = {}
        msg_obj_cmd = {}
        msg_obj_cmd['name'] = cmd
        msg_obj_cmd['args'] = args
        msg_obj_monitor_car['cmd'] = msg_obj_cmd
        msg_obj['monitor_car'] = msg_obj_monitor_car
        return msg_obj

    @staticmethod
    def generate_batch_processing(source, destination, job):
        msg_obj = {}
        msg_obj['source'] = source
        msg_obj['destination'] = destination
        msg_obj['type'] = DSRC_Event.TYPE_MONITOR_CAR
        msg_obj['subtype'] = DSRC_Event.SUBTYPE_BATCH
        msg_obj_monitor_car = {}
        msg_obj_batch = {}
        msg_obj_job = {}
        msg_obj_action = {}
        msg_obj_action['name'] = job.action.name
        msg_obj_action['arg1'] = job.action.arg1
        msg_obj_action['arg2'] = job.action.arg2
        msg_obj_job['action'] = msg_obj_action
        msg_obj_job['time'] = job.time
        msg_obj_batch['job'] = msg_obj_job
        msg_obj_monitor_car['batch'] = msg_obj_batch
        msg_obj['monitor_car'] = msg_obj_monitor_car
        return msg_obj

    @staticmethod
    def generate_monitor_car_ack(source, destination, seq):
        msg_obj = {}
        msg_obj['source'] = source
        msg_obj['destination'] = destination
        msg_obj['type'] = DSRC_Event.TYPE_MONITOR_CAR
        msg_obj['subtype'] = DSRC_Event.SUBTYPE_ACK
        msg_obj['seq'] = seq
        msg_obj['monitor_car'] = {}
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
