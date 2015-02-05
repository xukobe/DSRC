__author__ = 'xuepeng'

import threading
import socket
import sys

from dsrc_messager import socket_client
from dsrc_messager import socket_server


client = None

def test_server():
    tss = socket_server(_server_callback)
    tss.start()
    #threading._start_new_thread(tss.run,())
    while True:
        msg = raw_input("Please type some words:")
        client.send(msg)


def _server_callback(coming_socket):
    global client
    client_socket = coming_socket
    client = socket_client(_recv_callback,client_socket)
    client.run()

def _recv_callback(msg):
    message = msg.replace("\n", "")
    print message

def test_client():
    client = socket_client(_recv_callback)
    client.connect('127.0.0.1',10123)
    threading._start_new_thread(client.run,())
    while True:
        msg = raw_input("Please type some words:")
        client.send(msg)

if __name__ =="__main__":
    if len(sys.argv) < 2:
        print "Usage: test_trafficsocket client/server"
        quit()
    choice = sys.argv[1]
    if choice == 'client':
        test_client()
    elif choice == 'server':
        test_server()