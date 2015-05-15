__author__ = 'xuepeng'

from Event_Module import DSRC_Event
import time
import math
from Controller_Module.DSRC_JobProcessor import Job
import Controller_Module.DSRC_JobProcessor as DSRC_JobProcessor
# Must implement

do = False
execute_time = 0
time_duration = 30

auto_time = 0


def customized_event_handler(dsrc_unit, event):
    if dsrc_unit.seq == event.seq:
        return
    else:
        if event.seq:
            dsrc_unit.seq = event.seq
            dsrc_unit.send_ack(event.seq)

    if event.type == DSRC_Event.TYPE_CUSTOMIZED:
        if event.subtype == 'snakemove':
            current_time = time.time()
            # print str(current_time)
            if current_time - execute_time > 30:
                global do
                do = event.do_it
                # print str(do)
        elif event.subtype == 'auto_setup':
            current_time = time.time()
            global auto_time
            if current_time - auto_time > 30:
                x = event.x
                y = event.y
                d = event.r
                jobs = dsrc_unit.position_tracker.jobs_to_go(x, y)
                job1_arg = jobs['job1']
                job2_arg = jobs['job2']
                current_r = dsrc_unit.position_tracker.radian/(math.pi*2)*360
                changebyjob1 = job1_arg[2] * job1_arg[1]
                d_after_change = current_r + changebyjob1
                diff = (d - d_after_change) % 360
                rotate_speed = 45
                if diff > 180:
                    diff = 360 - diff
                    rotate_speed = -45
                job3_time = abs(diff/float(rotate_speed))
                job1 = Job(dsrc_unit, DSRC_JobProcessor.GO, job1_arg[2], job1_arg[0], job1_arg[1])
                job2 = Job(dsrc_unit, DSRC_JobProcessor.GO, job2_arg[2], job2_arg[0], job2_arg[1])
                job3 = Job(dsrc_unit, DSRC_JobProcessor.GO, job3_time, 0, rotate_speed)
                dsrc_unit.job_processor.add_new_job(job1)
                dsrc_unit.job_processor.add_new_job(job2)
                dsrc_unit.job_processor.add_new_job(job3)
                auto_time = time.time()


def print_receiver():
    print "I am a DSRC_Plugin_Receiver."