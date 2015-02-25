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
    def generate_car_car_message(source, destination, action_name, action_arg1, action_arg2, coor_x, coor_y, coor_radian):
        msg_obj = {}
        msg_obj['source'] = source
        msg_obj['destination'] = destination
        msg_obj['type'] = DSRC_Event.TYPE_CAR_CAR
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
        msg = MessageCoder.encode(msg_obj)
        return msg

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
