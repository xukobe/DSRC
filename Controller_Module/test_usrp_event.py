__author__ = 'xuepeng'

import os
import sys
import math

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from DSRC_Plugins import DSRC_Plugin_Invoker as Plugin

Plugin.load_plugin()


from DSRC_USRP_Connector import DsrcUSRPConnector
from DSRC_Event import USRPEventHandler
from DSRC_Messager_Module.dsrc_messager import SocketClient
from DSRC_Message_Coder import MessageCoder
import DSRC_Event
import threading
import json
import time

def main():
    detector = USRPEventHandler()
    connector = DsrcUSRPConnector(port=10123, callbackInterface=detector)

def _recv_callback(msg):
    message = msg.replace("\n", "")
    print message


class TestClient:
    def __init__(self):
        self.client = SocketClient(_recv_callback)
        self.client.connect('127.0.0.1',10123)
        threading._start_new_thread(self.client.run,())
        self.selection = 1
        self.job1 = create_car_car_type_package(DSRC_Event.ACTION_NAME_GO, 30, 45, 111, 111, 3.14)
        self.job2 = create_car_car_type_package(DSRC_Event.ACTION_NAME_GO, 30, 0, 222, 222, 3.24)
        self.job3 = create_car_car_type_package(DSRC_Event.ACTION_NAME_GO, 0, 45, 333, 333, 3.34)
        self.job4 = create_car_car_type_package(DSRC_Event.ACTION_NAME_GO, 0, 0, 444, 444, 3.44)
        print self.job1
        print self.job2
        print self.job3
        print self.job4
        # threading._start_new_thread(self.sending_thread, ())

    def sending_thread(self):
        while True:
            msg = ""
            if self.selection == 1:
                msg = json.dumps(self.job1)
            elif self.selection == 2:
                msg = json.dumps(self.job2)
            elif self.selection == 3:
                msg = json.dumps(self.job3)
            elif self.selection == 4:
                msg = json.dumps(self.job4)
            self.client.send(msg)
            time.sleep(0.5)


def follow_mode():

    test_client = TestClient()

    while True:
        select = raw_input("Please type your selection:")
        selection = int(select)
        test_client.selection = selection

def create_car_car_type_package(name, arg1, arg2, x, y, radian):
    job = {}
    job['source'] = 'car2'
    job['destination'] = 'all'
    job['type'] = 'car_car'
    job_car = {}
    job_action = {}
    job_action['name'] = name
    job_action['arg1'] = arg1
    job_action['arg2'] = arg2
    job_coor = {}
    job_coor['x'] = x
    job_coor['y'] = y
    job_coor['radian'] = radian
    job_car['action'] = job_action
    job_car['coor'] = job_coor
    job['car_car'] = job_car
    return job

def generate_car_car_message(msg_obj):
    msg = MessageCoder.encode(msg_obj)
    return msg

def generate_customized_message(source, destination):
    msg_obj = {}
    msg_obj['source'] = source
    msg_obj['destination'] = destination
    msg_obj['type'] = DSRC_Event.TYPE_CUSTOMIZED
    customized = {}
    customized["customized_action"] = "GO"
    msg_obj[DSRC_Event.TYPE_CUSTOMIZED] = customized
    msg = MessageCoder.encode(msg_obj)
    return msg


def send_customized_message(client):
    while True:
        msg = generate_customized_message("car2", "all")
        client.send(msg)
        time.sleep(0.5)

def send_car_car_message(client):
    while True:
        msg_obj = create_car_car_type_package('go', 0, 0, 90, 0, math.pi/2)
        msg = generate_car_car_message(msg_obj)
        print msg
        client.send(msg)
        time.sleep(0.2)


def main():
    client = SocketClient(_recv_callback)
    client.connect('127.0.0.1', 10123)
    threading._start_new_thread(send_car_car_message, (client,))
    raw_input("Press any key to quit!")
    exit()


if __name__ == '__main__':
    main()
    # follow_mode()