#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Wifi Transceiver
# Generated: Sat Jan 24 15:55:14 2015
##################################################
#execfile("~/.grc_gnuradio/wifi_phy_hier.py")
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
from wifi_phy_hier import wifi_phy_hier
from DSRC_Messenger_Blocks import DsrcServer
from dsrc_message_generator import message_generator
from dsrc_message_collector import message_collector
import foo
import ieee802_11
import pmt
import time

class WifiTransceiver(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Traffic Monitor")

        ##################################################
        # Variables
        ##################################################
        self.tx_gain = tx_gain = 90
        self.samp_rate = samp_rate = 10e6
        self.rx_gain = rx_gain = 50
        self.mult = mult = 0.38
        self.lo_offset = lo_offset = 0
        self.freq = freq = 5.89e9
        self.encoding = encoding = 0

        ##################################################
        # Blocks
        ##################################################
        self.wifi_phy_hier_0 = wifi_phy_hier(
            encoding=0,
        )
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(freq - lo_offset, lo_offset), 0)
        self.uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        	"packet_len",
        )
        self.uhd_usrp_sink_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(uhd.tune_request(freq - lo_offset, lo_offset), 0)
        self.uhd_usrp_sink_0.set_gain(tx_gain, 0)
        self.ieee802_11_ofdm_parse_mac_0 = ieee802_11.ofdm_parse_mac(False, True)
        self.ieee802_11_ofdm_mac_0 = ieee802_11.ofdm_mac(([0x30, 0x30, 0x30, 0x30, 0x30, 0x30]), ([0x42, 0x42, 0x42, 0x42, 0x42, 0x42]), ([0xff, 0xff, 0xff, 0xff, 0xff, 0xff]))
        self.foo_wireshark_connector_0 = foo.wireshark_connector(127, False)
        self.foo_packet_pad2_0 = foo.packet_pad2(False, False, 0.001, 0, 10000)
        (self.foo_packet_pad2_0).set_min_output_buffer(100000)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((mult, ))
        (self.blocks_multiply_const_vxx_0).set_min_output_buffer(100000)
        #self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern("     Laptop3     "), 100)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, "/tmp/ofdm.pcap", True)
        self.blocks_file_sink_0.set_unbuffered(True)
        #Add  by Xuepeng Xu
        self.transmitter = DsrcServer()
        #self.message_generator = message_generator()
        #self.message_collector = message_collector()

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.transmitter,'received out'),(self.ieee802_11_ofdm_mac_0, 'app in'))
        #self.msg_connect((self.transmitter,'received out'), (self.blocks_message_strobe_0, 'set_msg'))
        #self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.ieee802_11_ofdm_mac_0, 'app in'))
        self.msg_connect((self.ieee802_11_ofdm_mac_0, 'app out'),(self.transmitter,'send in'))
        #self.msg_connect((self.ieee802_11_ofdm_mac_0, 'app out'),(self.message_collector, 'message_stream in'))
        #self.msg_connect((self.message_collector,'message_to_collect out'),(self.transmitter,'send in'))
        self.msg_connect((self.ieee802_11_ofdm_mac_0, 'phy out'), (self.foo_wireshark_connector_0, 'in'))    
        self.msg_connect((self.ieee802_11_ofdm_mac_0, 'phy out'), (self.wifi_phy_hier_0, 'mac_in'))    
        self.msg_connect((self.wifi_phy_hier_0, 'mac_out'), (self.foo_wireshark_connector_0, 'in'))    
        self.msg_connect((self.wifi_phy_hier_0, 'mac_out'), (self.ieee802_11_ofdm_mac_0, 'phy in'))    
        self.msg_connect((self.wifi_phy_hier_0, 'mac_out'), (self.ieee802_11_ofdm_parse_mac_0, 'in'))    
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.foo_packet_pad2_0, 0))    
        self.connect((self.foo_packet_pad2_0, 0), (self.uhd_usrp_sink_0, 0))    
        self.connect((self.foo_wireshark_connector_0, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.uhd_usrp_source_0, 0), (self.wifi_phy_hier_0, 0))    
        self.connect((self.wifi_phy_hier_0, 0), (self.blocks_multiply_const_vxx_0, 0))    


    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.uhd_usrp_sink_0.set_gain(self.tx_gain, 0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 0)

    def get_mult(self):
        return self.mult

    def set_mult(self, mult):
        self.mult = mult
        self.blocks_multiply_const_vxx_0.set_k((self.mult, ))

    def get_lo_offset(self):
        return self.lo_offset

    def set_lo_offset(self, lo_offset):
        self.lo_offset = lo_offset
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(self.freq - self.lo_offset, self.lo_offset), 0)
        self.uhd_usrp_sink_0.set_center_freq(uhd.tune_request(self.freq - self.lo_offset, self.lo_offset), 0)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(self.freq - self.lo_offset, self.lo_offset), 0)
        self.uhd_usrp_sink_0.set_center_freq(uhd.tune_request(self.freq - self.lo_offset, self.lo_offset), 0)

    def get_encoding(self):
        return self.encoding

    def set_encoding(self, encoding):
        self.encoding = encoding

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = WifiTransceiver()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.transmitter.stop_self()
    exit()
