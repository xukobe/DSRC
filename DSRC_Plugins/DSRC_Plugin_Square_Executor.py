__author__ = 'xuepeng'

import DSRC_Plugins as Plugin
import time
from Controller_Module import DSRC_JobProcessor
from Controller_Module.DSRC_JobProcessor import Job

EXECUTE_INTERVALS = 10

DO_IT = False

SPEED = 20


def execute(dsrc_unit):
    global DO_IT
    if DO_IT:
        job1 = Job(dsrc_unit, DSRC_JobProcessor.GO, 12, SPEED, 0)
        job2 = Job(dsrc_unit, DSRC_JobProcessor.GO, 2, 0, 45)
        job3 = Job(dsrc_unit, DSRC_JobProcessor.GO, 12, SPEED, 0)
        job4 = Job(dsrc_unit, DSRC_JobProcessor.GO, 2, 0, 45)
        job5 = Job(dsrc_unit, DSRC_JobProcessor.GO, 12, SPEED, 0)
        job6 = Job(dsrc_unit, DSRC_JobProcessor.GO, 2, 0, 45)
        job7 = Job(dsrc_unit, DSRC_JobProcessor.GO, 12, SPEED, 0)
        job8 = Job(dsrc_unit, DSRC_JobProcessor.GO, 2, 0, 45)
        dsrc_unit.job_processor.add_new_job(job1)
        dsrc_unit.job_processor.add_new_job(job2)
        dsrc_unit.job_processor.add_new_job(job3)
        dsrc_unit.job_processor.add_new_job(job4)
        dsrc_unit.job_processor.add_new_job(job5)
        dsrc_unit.job_processor.add_new_job(job6)
        dsrc_unit.job_processor.add_new_job(job7)
        dsrc_unit.job_processor.add_new_job(job8)
        DO_IT = False


def customized_cmd(dsrc_unit, user_input):
    global DO_IT
    if user_input == 'square':
        DO_IT = True