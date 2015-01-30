__author__ = 'xuepeng'

from gnuradio import gr
import threading
import pmt
import time

class message_generator(gr.basic_block):
    def __init__(self, period=100):
        #threading.Thread.__init__(self)
        gr.basic_block.__init__(self,
            name="Message Generator",
            in_sig=[],
            out_sig=[])
        self.period = period
        self.message = pmt.intern('')
        self.running = True
        self.message_port_register_out(pmt.intern('message_stream out'))
        self.message_port_register_in(pmt.intern('message_to_send in'))
        self.set_msg_handler(pmt.intern('message_to_send in'), self.handle_msg)
        #threading.Thread.start(self)

    def work(self, input_items, output_items):
        print self.message

    # def run(self):
    #     while self.running:
    #         #if pmt.equal(self.message, pmt.intern('')):
    #             #pass
    #         #else:
    #         print "sending message"
    #         self.message_port_pub(pmt.intern('message_stream out'), self.message)
    #         time.sleep(1)

    def handle_msg(self, msg):
        msgs = pmt.cdr(msg)
        msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msgs)])
        print msg_str
        print self.message
        self.message = msg
        self.message_port_pub(pmt.intern('message_stream out'), self.message)
        if pmt.eq(self.message, msg):
            print "No change"
            pass
        else:
            print "Changed"
            self.message = msg