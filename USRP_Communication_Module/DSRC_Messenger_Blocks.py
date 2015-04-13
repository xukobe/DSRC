__author__ = 'xuepeng'

"This block uses socket to do the inter-process communication."

import string
import numpy
import pmt
import json
import TransceiverController as TC
from gnuradio import gr
from DSRC_Messager_Module.DSRC_Messenger import SocketClient
from DSRC_Messager_Module.DSRC_Messenger import SocketServer

class DsrcClient(gr.basic_block):
    "This class is client in the inter-process communication."
    def __init__(self, IP="127.0.0.1", port = 10124):
        gr.basic_block.__init__(self,
            name="Socket Client",
            in_sig=[],
            out_sig=[])
        self.IP = IP
        self.port = port
        self.message_port_register_out(pmt.intern('received out'))
        self.message_port_register_in(pmt.intern('send in'))
        self.set_msg_handler(pmt.intern('send in'),self.handle_msg)
        self.client = SocketClient(self._recv_callback)
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
        # print msg

    def handle_msg(self, msg_pmt):
        # TODO: Here I use a dirty way to handle the received string. This method need to be refined
        # print msg_pmt
        # msg = pmt.cdr(msg_pmt)
        # msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        msg = pmt.cdr(msg_pmt)
        msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        #msg_str = filter(lambda x: x in string.printable, msg_str)
        #msg_str = pmt.symbol_to_string(msg_pmt)
        # Here I just cut the string from the 24th character. the previous 24 chars are the header
        msg_cutted = msg_str[24:]
        self.send_to_client(msg_cutted)

    def send_to_client(self, msg):
        try:
            self.client.send(msg)
        except Exception,e:
            print "Connection is down! Exiting!"
            exit()

    def stop_self(self):
        self.client.stop_self()

class DsrcServer(gr.basic_block):
    def __init__(self, port=10124, controller=None):
        gr.basic_block.__init__(self,
                name="Socket Server",
                in_sig=[],
                out_sig=[])
        self.port = port
        self.controller = controller
        self.server = SocketServer(self._connected_callback,self.port)
        self.client = []
        self.message_port_register_out(pmt.intern('received out'))
        self.message_port_register_in(pmt.intern('send in'))
        self.set_msg_handler(pmt.intern('send in'),self.handle_msg)
        self.server.start()
        print "Listen to port "+str(self.port)

    def _connected_callback(self,incoming_socket):
        print "A client is connecting"
        client = SocketClient(self._recv_callback, incoming_socket)
        self.client.append(client)
        client.start()
        print "Connected"

    def _recv_callback(self,msg):
        # rev_msg = pmt.symbol_to_string(msg)
        # send_pmt = pmt.make_u8vector(len(rev_msg), ord(' '))
        # for i in range(len(rev_msg)):
        #     pmt.u8vector_set(send_pmt, i, ord(rev_msg[i]))
        # self.message_port_pub(pmt.intern('received out'), pmt.cons(pmt.PMT_NIL, send_pmt))
        try:
            json_obj = json.loads(msg)
            if json_obj[TC.TYPE_KEY] == TC.TYPE_VALUE:
                self.controller.change_setting(json_obj)
                return
        except Exception, e:
            pass

        self.message_port_pub(pmt.intern('received out'), pmt.string_to_symbol(msg))
        # print msg

    def handle_msg(self,msg_pmt):
        # print msg_pmt
        #msg_pmt_cdr = pmt.cdr(msg_pmt)
        # msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        msg = pmt.cdr(msg_pmt)
        msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        #msg_str = filter(lambda x: x in string.printable, msg_str)
        #msg_str = pmt.symbol_to_string(msg_pmt)
        msg_cutted = msg_str[24:]
        # print "Server: Handle MSG: "+msg_cutted
        # Change setting of the transceiver

        self.send_to_clients(msg_cutted)

    def send_to_clients(self, msg):
        for i in range(len(self.client)):
            try:
                self.client[i].send(msg)
            except Exception, e:
                self.client.remove(self.client[i])

    def stop_self(self):
        for i in range(len(self.client)):
            self.client[i].stop_self()
        self.server.stop_self()