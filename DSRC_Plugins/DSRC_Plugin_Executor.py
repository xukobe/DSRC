__author__ = 'xuepeng'

from Controller_Module import DSRC_Event
from Controller_Module.DSRC_Message_Coder import MessageCoder

# Times of the MiniInterval in unit_config
SEND_INTERVALS = 10


def execute(dsrc_unit):
    msg = _generate_customized_message(dsrc_unit.unit_id, DSRC_Event.DESTINATION_ALL)
    dsrc_unit.USRP_connect.send_to_USRP(msg)


def customized_cmd(dsrc_unit, user_input):
    pass

def _generate_customized_message(source, destination):
    msg_obj = {}
    msg_obj['source'] = source
    msg_obj['destination'] = destination
    msg_obj['type'] = DSRC_Event.TYPE_CUSTOMIZED
    customized = {}
    customized["customized_action"] = "GO"
    msg_obj[DSRC_Event.TYPE_CUSTOMIZED] = customized
    msg = MessageCoder.encode(msg_obj)
    return msg


def print_sender():
    print "I am a DSRC_Plugin_Executor."