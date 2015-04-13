__author__ = 'xuepeng'

from threading import Thread
import json
import time

TYPE_KEY = 'type'
TYPE_VALUE = 'transceiver'
SETTINGS_POWER = 'power'
SETTINGS_RATE = 'rate'

class Controller(Thread):
    def __init__(self, transceiver):
        Thread.__init__(self)
        self.transceiver = transceiver
        self.running = True

    def change_setting(self, settings):
        power = None
        rate = None
        try:
            power = settings[SETTINGS_POWER]
        except Exception, e:
            pass

        try:
            rate = settings[SETTINGS_RATE]
        except Exception, e:
            pass

        if power != None:
            self.transceiver.set_tx_gain(power)

        if rate != None:
            self.transceiver.set_encoding(rate)

    def run(self):
        while self.running:
            msg_obj = {}
            msg_obj[TYPE_KEY] = TYPE_VALUE
            msg_obj['power'] = self.transceiver.tx_gain
            msg_obj['rate'] = self.transceiver.encoding
            msg = json.dumps(msg_obj)
            self.transceiver.transmitter.send_to_clients(msg)
            time.sleep(1)

    def stop_self(self):
        self.running = False