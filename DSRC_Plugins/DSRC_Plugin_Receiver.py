__author__ = 'xuepeng'

# Must implement
def customized_event_handler(dsrc_unit, event):
    print "Plugin customized event received:" + event.customized_action


def print_receiver():
    print "I am a DSRC_Plugin_Receiver."