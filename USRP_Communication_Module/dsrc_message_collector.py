__author__ = 'xuepeng'

from gnuradio import gr
import threading
import pmt
import time

class message_collector(gr.basic_block):
    def __init__(self, period = 100):
        gr.basic_block.__init__(self,
            name="Message Generator",
            in_sig=[],
            out_sig=[])
        self.period = period
        self.message = ''
        self.running = True
        self.message_port_register_in(pmt.intern('message_stream in'))
        self.message_port_register_out(pmt.intern('message_to_collect out'))
        self.set_msg_handler(pmt.intern('message_stream in'),self.handle_msg)

    def handle_msg(self,msg):
        print msg
        if self.message == msg:
            pass
        else:
            self.message = msg
            self.message_port_pub(pmt.intern('message_to_collect out'), self.message)