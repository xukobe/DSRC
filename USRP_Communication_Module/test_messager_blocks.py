__author__ = 'xuepeng'

import pmt
import sys
from gnuradio import gr
from DSRC_Messenger_Blocks import DsrcClient
from DSRC_Messenger_Blocks import DsrcServer

class test_sender(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="Sender",
            in_sig=[],
            out_sig=[])
        self.message_port_register_out(pmt.intern('out'))

    def post_message(self, msg):
        # send_pmt = pmt.make_u8vector(len(msg), ord(' '))
        # for i in range(len(msg)):
        #     pmt.u8vector_set(send_pmt, i, ord(msg[i]))
        self.message_port_pub(pmt.intern('out'), pmt.string_to_symbol(msg))


class test_receiver(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
                                name = "Receiver",
                                in_sig=[],
                                out_sig=[])
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'),self.handle_msg)

    def handle_msg(self,msg_pmt):
        # msg = pmt.cdr(msg_pmt)
        # msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        msg_str = pmt.symbol_to_string(msg_pmt)
        print msg_pmt
        print msg_str


if __name__ == "__main__":
    tb = gr.top_block()
    if len(sys.argv) < 2:
        print "Usage: test_messager_blocks client/server"
        quit()
    choice = sys.argv[1]
    sender = test_sender()
    receiver = test_receiver()
    if choice == 'server':
        transmitter = DsrcServer()
    elif choice == 'client':
        transmitter = DsrcClient()
    tb.msg_connect((sender,'out'),(transmitter,'send in'))
    tb.msg_connect((transmitter,'received out'),(receiver,'in'))
    tb.start()
    try:
        while True:
            msg = raw_input("Please type some words:")
            sender.post_message(msg)
    except KeyboardInterrupt:
        print "keyboardInterrupt!\n"
    except EOFError:
        print "\n"
    transmitter.stopself()
    print "Stopping itself!"
    tb.stop()
    tb.wait()

