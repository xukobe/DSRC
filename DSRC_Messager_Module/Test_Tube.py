__author__ = 'xuepeng'

import threading
import socket
import sys, os
import math
import random
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import signal
from DSRC_Messenger import SocketClient
from DSRC_Messenger import SocketServer
from Event_Module import DSRC_Message_Coder


class TestTube:
    def __init__(self):
        self.mss = SocketServer(self._monitor_server_callback, port=10123)
        self.msc = None

        self.css = SocketServer(self._car_server_callback, port=10124)
        self.csc = []

        self.mss.start()
        self.css.start()

    def _monitor_server_callback(self, coming_socket):
        client_socket = coming_socket
        self.msc = SocketClient(self._monitor_recv_callback, client_socket)
        self.msc.start()

    def _monitor_recv_callback(self, msg):
        # message = msg.replace("\n", "")
        print msg
        if len(self.csc) > 0:
            for csc in self.csc:
                try:
                    csc.send(msg)
                    print "Send to Client"
                except Exception, e:
                    self.csc.remove(csc)

    def _car_server_callback(self, coming_socket):
        client_socket = coming_socket
        csc = SocketClient(self._car_recv_callback, client_socket)
        csc.start()
        self.csc.append(csc)

    def _car_recv_callback(self, msg):
        # message = msg.replace("\n", "")
        print msg
        if self.msc:
            try:
                self.msc.send(msg)
                print "Send To Monitor"
            except Exception, e:
                self.msc = None
        if len(self.csc) > 0:
            for csc in self.csc:
                try:
                    csc.send(msg)
                    print "Send to Client"
                except Exception, e:
                    self.csc.remove(csc)

    def close(self):
        if len(self.csc) > 0:
            for csc in self.csc:
                try:
                    csc.stop_self()
                except Exception, e:
                    self.csc.remove(csc)
        if self.msc:
            self.msc.stop_self()
        if self.mss:
            self.mss.stop_self()
        if self.css:
            self.css.stop_self()


close_tube = False

def signal_receiver(signum, stack):
    print "Received " + str(signum)
    global close_tube
    close_tube = True

def main(stdout_fileno):
    global close_tube
    home = os.path.expanduser("~")
    sys.stdout = sys.fdopen(stdout_fileno, 'w')
    close_tube = False
    tube = TestTube()
    time.sleep(0.1)
    file_name = home+'/.DSRC_Server_Socket'
    f = open(file_name, 'w')
    f.write("1")
    f.close()
    signal.signal(signal.SIGUSR1, signal_receiver)
    while True:
        if close_tube:
            os.remove(file_name)
            try:
                tube.close()
            except Exception, e:
                print "Bye!"
            close_tube = False
        time.sleep(0.5)

if __name__ == '__main__':
    main(sys.stdout.fileno())