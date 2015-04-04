__author__ = 'xuepeng'

import DSRC_Plugins as Plugin
from Controller_Module import DSRC_JobProcessor
from Controller_Module.DSRC_JobProcessor import Job

SEND_INTERVALS = 1

Counter = 0

Lane_sign = False


def execute(dsrc_unit):
    receiver_module = Plugin.get_receiver_module()
    if receiver_module.stopSign:
        # print "Stop"
        dsrc_unit.job_processor.pause_processor()
    elif receiver_module.slowSign:
        # print "Slow down"
        if dsrc_unit.job_processor.currentJob:
            arg1 = dsrc_unit.job_processor.currentJob.arg1
            if arg1 > 15:
                arg2 = dsrc_unit.job_processor.currentJob.arg2
                time = dsrc_unit.job_processor.currentJob.get_current_left_time()
                new_time = arg1 * time / 15
                print "Slow New time:" + str(new_time)
                job = Job(dsrc_unit, DSRC_JobProcessor.GO, new_time, 15, arg2)
                dsrc_unit.job_processor.insert_new_job(job)
                dsrc_unit.job_processor.cancel_current_job()
    else:
        # print "Normal"

        if dsrc_unit.job_processor.pause:
            dsrc_unit.job_processor.resume_processor()
        else:
            if dsrc_unit.job_processor.currentJob:
                arg1 = dsrc_unit.job_processor.currentJob.arg1
                if 0 < arg1 < 30:
                    arg2 = dsrc_unit.job_processor.currentJob.arg2
                    time = dsrc_unit.job_processor.currentJob.get_current_left_time()
                    new_time = arg1 * time / 30
                    print "Normal New time:" + str(new_time)
                    job = Job(dsrc_unit, DSRC_JobProcessor.GO, new_time, 30, arg2)
                    dsrc_unit.job_processor.insert_new_job(job)
                    dsrc_unit.job_processor.cancel_current_job()
        # if dsrc_unit.job_processor.pause:
        #     arg1 = dsrc_unit.job_processor.currentJob.arg1
        #     arg2 = dsrc_unit.job_processor.currentJob.arg2
        #     time = dsrc_unit.job_processor.currentJob.timeLeft
        #     if arg1 < 30:
        #         new_time = arg1 * time / 30
        #         job = Job(dsrc_unit, DSRC_JobProcessor.GO, new_time, 15, arg2)
        #         dsrc_unit.job_processor.insert_new_job(job)
        #         dsrc_unit.job_processor.cancel_current_job()
        #     dsrc_unit.job_processor.resume_processor()
    # msg = _generate_customized_message(dsrc_unit.unit_id, DSRC_Event.DESTINATION_ALL)
    # dsrc_unit.USRP_connect.send_to_USRP(msg)


def customized_cmd(dsrc_unit, user_input):
    global Lane_sign
    if user_input == "auto":
        print "Auto driving!"
        Lane_sign = True
    elif user_input == "back":
        print "Back to manual mode"
        Lane_sign = False
    elif user_input == 'plugin':
        print "I am lane executor!"