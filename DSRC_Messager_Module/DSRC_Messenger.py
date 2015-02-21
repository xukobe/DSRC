__author__ = 'xuepeng'

import socket
import random
import time
import threading

PACKET_LEN = 512

class SocketClient(threading.Thread):
    def __init__(self, recv_callback, sock=None):
        super(SocketClient, self).__init__()
        self.recv_callback = recv_callback
        self.running = True
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self,msg):
        if len(msg)<PACKET_LEN:
            lack_size = PACKET_LEN - len(msg)
            message = msg+'\n'*lack_size
        else:
            message = msg[0:(PACKET_LEN-1)]+"\n"
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
        print "Client is closed!"

    def _receive(self):
        read_len = PACKET_LEN
        total_len = PACKET_LEN
        msg = ''
        while self.running:
            try:
                data = self.sock.recv(read_len)
                if data == '':
                    print "socket connection broken"
                    self.running = False
                read_len = read_len - len(data)
                msg = msg + data
                if(read_len == 0):
                    self._handle_received(msg)
                    read_len = PACKET_LEN
                    msg = ''
            except Exception, e:
                print "A Client disconnected!"
                break

    def _handle_received(self,msg):
        message = msg.replace("\n", "")
        self.recv_callback(message)

    def stop_self(self):
        self.running = False
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

class SocketServer(threading.Thread):
    def __init__(self,connected_callback, port = 10123):
        super(SocketServer, self).__init__()
        self.port = port
        self.connected_callback = connected_callback
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1)

    def run(self):
        self.running = True
        while self.running:
            try:
                (client_socket, address) = self.server_socket.accept()
                self.server_socket.settimeout(2)
                self.connected_callback(client_socket)
            except socket.timeout:
                pass
        print "Server is closed!"

    def stop_self(self):
        self.running = False
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()

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
