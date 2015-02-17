__author__ = 'xuepeng'

import DSRC_Plugins as Plugin
from Controller_Module import DSRC_JobProcessor
from Controller_Module.DSRC_JobProcessor import Job

SEND_INTERVALS = 10

Counter = 0

Lane_sign = False


def execute(dsrc_unit):
    global Lane_sign
    if Lane_sign:
        receiver_module = Plugin.get_receiver_module()
        if receiver_module.stopSign:
            dsrc_unit.job_processor.pause_processor()
        elif receiver_module.slowSign:
            job = Job(dsrc_unit, DSRC_JobProcessor.GO, None, 15, 0)
            dsrc_unit.job_processor.add_new_job(job)
            dsrc_unit.job_processor.cancel_current_job()
        else:
            job = Job(dsrc_unit, DSRC_JobProcessor.GO, None, 30, 0)
            dsrc_unit.job_processor.add_new_job(job)
            dsrc_unit.job_processor.cancel_current_job()
    # msg = _generate_customized_message(dsrc_unit.unit_id, DSRC_Event.DESTINATION_ALL)
    # dsrc_unit.USRP_connect.send_to_USRP(msg)


def customized_cmd(dsrc_unit, user_input):
    if user_input == "auto":
        print "Auto driving!"
        global Lane_sign
        Lane_sign = True
    elif user_input == "back":
        print "Back to manual mode"
        global Lane_sign
        Lane_sign = False