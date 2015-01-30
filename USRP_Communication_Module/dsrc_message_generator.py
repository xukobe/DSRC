__author__ = 'xuepeng'

from gnuradio import gr
import threading
import pmt
import time

class message_generator(gr.basic_block, threading.Thread):
    def __init__(self, period = 100):
        threading.Thread.__init__(self)
        gr.basic_block.__init__(self,
            name="Message Generator",
            in_sig=[],
            out_sig=[])
        self.period = period
        self.message = ''
        self.running = True
        self.message_port_register_out(pmt.intern('message_stream out'))
        self.message_port_register_in(pmt.intern('message_to_send in'))
        self.set_msg_handler(pmt.intern('message_to_send in'),self.handle_msg)
        self.start()

    def run(self):
        while self.running:
            if self.message != '':
                self.message_port_pub(pmt.intern('message_stream out'), self.message)
            time.sleep((self.period/1000.0))

    def handle_msg(self,msg):
        if self.message == msg:
            pass
        else:
            self.message = msg