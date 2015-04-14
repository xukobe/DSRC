__author__ = 'xuepeng'

from threading import Thread
import json
import time
import Event_Module.TransceiverSettings as TS

class Controller(Thread):
    def __init__(self, transceiver):
        Thread.__init__(self)
        self.transceiver = transceiver
        self.running = True

    def change_setting(self, settings):
        power = None
        rate = None
        try:
            power = settings[TS.SETTINGS_POWER]
        except Exception, e:
            pass

        try:
            rate = settings[TS.SETTINGS_RATE]
        except Exception, e:
            pass

        if power != None:
            self.transceiver.set_tx_gain(power)

        if rate != None:
            self.transceiver.set_encoding(rate)

    def run(self):
        while self.running:
            msg_obj = {}
            msg_obj[TS.TYPE_KEY] = TS.TYPE_VALUE
            msg_obj[TS.SETTINGS_POWER] = self.transceiver.tx_gain
            msg_obj[TS.SETTINGS_RATE] = self.transceiver.encoding
            msg = json.dumps(msg_obj)
            self.transceiver.transmitter.send_to_clients(msg)
            time.sleep(1)

    def stop_self(self):
        self.running = False