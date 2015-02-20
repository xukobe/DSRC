__author__ = 'xuepeng'

import threading

from DSRC_Messenger import SocketClient
from DSRC_Messenger import SocketServer


client = None

def test_server():
    tss = SocketServer(_server_callback)
    threading._start_new_thread(tss.run,())
    while True:
        msg = raw_input("Please type some words:")
        if(len(msg)<256):
            lack_size = 256 - len(msg)
            message = msg+'\n'*lack_size
        else:
            message = msg[0:255]+"\n"
        client._send(message)


def _server_callback(coming_socket):
    global client
    client_socket = coming_socket
    client = SocketClient(_recv_callback,client_socket)
    client.run()

def _recv_callback(msg):
    message = msg.replace("\n", "")
    print message

def test_client():
    client = SocketClient(_recv_callback)
    client.connect('127.0.0.1',10123)
    threading._start_new_thread(client.run,())
    while True:
        msg = raw_input("Please type some words:")
        if(len(msg)<256):
            lack_size = 256 - len(msg)
            message = msg+'\n'*lack_size
        else:
            message = msg[0:255]+"\n"
        client._send(message)

if __name__ =="__main__":
    test_client()