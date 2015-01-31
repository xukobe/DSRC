__author__ = 'xuepeng'

"This block uses socket to do the inter-process communication."

import string
import numpy
import pmt
from gnuradio import gr
from dsrc_messager import socket_client
from dsrc_messager import socket_server

class dsrc_client(gr.basic_block):
    "This class is client in the inter-process communication."
    def __init__(self, IP="127.0.0.1", port = 10123):
        gr.basic_block.__init__(self,
            name="Socket Client",
            in_sig=[],
            out_sig=[])
        self.IP = IP
        self.port = port
        self.message_port_register_out(pmt.intern('received out'))
        self.message_port_register_in(pmt.intern('send in'))
        self.set_msg_handler(pmt.intern('send in'),self.handle_msg)
        self.client = socket_client(self._recv_callback)
        print "Connecting to "+IP+":"+str(port)
        self.client.connect(IP,port)
        self.client.start()
        print "Connected"

    #Message received from socket
    def _recv_callback(self,msg):
        #encapsulate the message with pmt type
        #rev_msg = pmt.symbol_to_string(msg)
        # send_pmt = pmt.make_u8vector(len(rev_msg), ord(' '))
        # for i in range(len(rev_msg)):
        #     pmt.u8vector_set(send_pmt, i, ord(rev_msg[i]))
        # self.message_port_pub(pmt.intern('received out'), pmt.cons(pmt.PMT_NIL, send_pmt))
        self.message_port_pub(pmt.intern('received out'), pmt.string_to_symbol(msg))
        print msg

    def handle_msg(self, msg_pmt):
        print msg_pmt
        # msg = pmt.cdr(msg_pmt)
        # msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        msg_str = pmt.symbol_to_string(msg_pmt)
        self.client.send(msg_str)

    def stopself(self):
        self.client.stopself()

class dsrc_server(gr.basic_block):
    def __init__(self,port = 10123):
        gr.basic_block.__init__(self,
                name="Socket Server",
                in_sig=[],
                out_sig=[])
        self.port = port
        self.server = socket_server(self._connected_callback,self.port)
        self.client = []
        self.message_port_register_out(pmt.intern('received out'))
        self.message_port_register_in(pmt.intern('send in'))
        self.set_msg_handler(pmt.intern('send in'),self.handle_msg)
        self.server.start()
        print "Listen to port "+str(self.port)

    def _connected_callback(self,incoming_socket):
        print "A client is connecting"
        client = socket_client(self._recv_callback, incoming_socket)
        self.client.append(client)
        client.start()
        print "Connected"

    def _recv_callback(self,msg):
        rev_msg = pmt.symbol_to_string(msg)
        # send_pmt = pmt.make_u8vector(len(rev_msg), ord(' '))
        # for i in range(len(rev_msg)):
        #     pmt.u8vector_set(send_pmt, i, ord(rev_msg[i]))
        # self.message_port_pub(pmt.intern('received out'), pmt.cons(pmt.PMT_NIL, send_pmt))
        self.message_port_pub(pmt.intern('received out'), pmt.string_to_symbol(rev_msg))
        print msg

    def handle_msg(self,msg_pmt):
        print msg_pmt
        # msg = pmt.cdr(msg_pmt)
        # msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        msg_str = pmt.symbol_to_string(msg_pmt)
        print msg_str
        for i in range(len(self.client)):
            self.client[i].send(msg_str)

    def stopself(self):
        for i in range(len(self.client)):
            self.client[i].stopself()
        self.server.stopself()