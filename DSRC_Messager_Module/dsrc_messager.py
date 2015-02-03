__author__ = 'xuepeng'

import socket
import random
import time
import threading

class socket_client(threading.Thread):
    def __init__(self, recv_callback,sock=None):
        super(socket_client, self).__init__()
        self.recv_callback = recv_callback
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self,msg):
        if(len(msg)<256):
            lack_size = 256 - len(msg)
            message = msg+'\n'*lack_size
        else:
            message = msg[0:255]+"\n"
        self._send(message)

    def _send(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def run(self):
        self._receive()

    def _receive(self):
        read_len = 256
        total_len = 256
        msg = ''
        self.running = True
        while self.running:
            data = self.sock.recv(read_len)
            if data == '':
                print "socket connection broken"
                self.running = False
            read_len = read_len - len(data)
            msg = msg + data
            if(read_len == 0):
                self._handle_received(msg)
                read_len = 256
                msg = ''

    def _handle_received(self,msg):
        message = msg.replace("\n", "")
        self.recv_callback(message)

    def stopself(self):
        self.running = False

class socket_server(threading.Thread):
    def __init__(self,connected_callback, port = 10123):
        super(socket_server, self).__init__()
        self.port = port
        self.connected_callback = connected_callback
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind(('0.0.0.0',self.port))
        self.serversocket.listen(5)
        self.serversocket.settimeout(1)

    def run(self):
        self.running = True
        while self.running:
            try:
                (clientsocket, address) = self.serversocket.accept()
                self.serversocket.settimeout(2)
                self.connected_callback(clientsocket)
            except socket.timeout:
                pass

    def stopself(self):
        self.running = False

# def main():
#     sock = trafficsocket()
#     sock.connect('127.0.0.1',10213)
#     while True:
#         #send to map
#         x = random.randint(1,500)
#         y = random.randint(1,500)
#         mapstr = "MAP,car1,"+str(x)+","+str(y)+"\n"
#         print mapstr
#         sock.traffic_send(mapstr)
#
#         #send to power chart
#         power = random.uniform(1,100)
#         powerstr = "POWER,car1,"+str(power)+"\n"
#         print powerstr
#         sock.traffic_send(powerstr)
#
#         #send to rate chart
#         rate = random.uniform(1,100)
#         ratestr = "RATE,car1,"+str(rate)+"\n"
#         print ratestr
#         sock.traffic_send(ratestr)
#
#         time.sleep(2)

#if __name__ == '__main__':
    #main()
