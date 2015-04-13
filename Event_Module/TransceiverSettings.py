__author__ = 'xuepeng'

TYPE_KEY = 'type'
TYPE_VALUE = 'transceiver'
SETTINGS_POWER = 'power'
SETTINGS_RATE = 'rate'


class TransceiverSetting:
    def __init__(self):
        pass

    @staticmethod
    def generate_power_setting_msg(power):
        msg_obj = {TYPE_KEY: TYPE_VALUE, SETTINGS_POWER: power}
        return msg_obj

    @staticmethod
    def generate_rate_setting_msg(rate):
        msg_obj = {TYPE_KEY: TYPE_VALUE, SETTINGS_RATE: rate}
        return msg_obj


class USRPEvent:
    def __init__(self, power, rate):
        self.type = TYPE_VALUE
        self.power = power
        self.rate = rate