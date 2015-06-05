__author__ = 'xuepeng'

import math
import time

import threading
import Event_Module.DSRC_Event as Event
from Controller_Module.DSRC_JobProcessor import Job
import Controller_Module.DSRC_JobProcessor as DSRC_JobProcessor


stopSign = False

slowSign = False

CarSize = 30

execute_time = 0
time_duration = 30
do = False

auto_time = 0

setup_lock = threading.Lock()

move_lock = threading.Lock()

def customized_event_handler(dsrc_unit, event):
    global stopSign
    global slowSign
    if event.type == Event.TYPE_CAR_CAR:
        x1 = dsrc_unit.position_tracker.x
        y1 =dsrc_unit.position_tracker.y
        r1 = dsrc_unit.position_tracker.radian

        coord = event.coordinates
        x2 = coord.x
        y2 = coord.y
        r2 = coord.radian
        if dsrc_unit.job_processor.currentJob:
            speed1 = dsrc_unit.job_processor.currentJob.arg1
        else:
            speed1 = 0
        speed2 = event.action.arg1
        p = calculate_collision_point(x1, y1, r1, x2, y2, r2, speed1, speed2)

        if not p:
            # print "No collision!"
            stopSign = False
            slowSign = False
        else:
            x = p[0]
            y = p[1]

            time1_f = calc_time(x1, y1, x, y, 30)
            time1_s = calc_time(x1, y1, x, y, 15)
            time2 = calc_time(x2, y2, x, y, speed2)

            # print str(x) + ":" + str(y) + ":time_f:" + str(time1_f) + ":time_s:" + str(time1_s) + ":time2:" + str(time2)

            if abs(time1_s - time2) <= 3 and time1_s <= 3:
                # print "Stop sign"
                stopSign = True
            elif abs(time1_f - time2) <= 5 and time1_f <= 5:
                # print "Slow sign"
                stopSign = False
                slowSign = True
            else:
                # print "No sign"
                stopSign = False
                slowSign = False
    elif event.type == Event.TYPE_CUSTOMIZED:
        if dsrc_unit.seq == event.seq:
            return
        else:
            if event.seq:
                dsrc_unit.seq = event.seq
                dsrc_unit.send_ack(event.seq)
        # print str(event.subtype)
        if event.subtype == 'auto_setup':
            setup_lock.acquire()
            current_time = time.time()
            global auto_time
            if current_time - auto_time > time_duration:
                # print "lane new auto setup"
                x = event.x
                y = event.y
                d = event.r
                jobs = dsrc_unit.position_tracker.jobs_to_go(x, y)
                if jobs:
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
            setup_lock.release()
        elif event.subtype == 'automove':
            move_lock.acquire()
            current_time = time.time()
            global execute_time
            if current_time - execute_time > time_duration:
                # print "lane new auto move"
                global do
                do = event.do_it
                execute_time = time.time()
                job = Job(dsrc_unit, DSRC_JobProcessor.GO, 8, 30, 0)
                dsrc_unit.job_processor.add_new_job(job)
                # print str(do)
            move_lock.release()


def calculate_collision_point(x1, y1, r1, x2, y2, r2, speed1, speed2):
    # line1 a and b
    a1 = math.tan(r1)
    b1 = y1 - a1*x1

    # line2 a and b
    a2 = math.tan(r2)
    b2 = y2 - a2*x2

    # print "a1, a2: " + str(a1) + "," + str(a2)
    # print "b1, b2: " + str(b1) + "," + str(b2)

    if abs(a1-a2) < 0.01:
        # print "a1 == a2"
        same_direction = False
        if math.pi/6*5 < ((r1 - r2) % math.pi) < math.pi/6*7:
            if speed1 * speed2 < 0:
                same_direction = False
            else:
                same_direction = True
        if same_direction:
            distance_between_lines = abs(b1-b2) * math.cos(a1)
            if distance_between_lines > CarSize:
                return None
            if distance_between_lines < CarSize and abs(speed1) <= abs(speed2):
                return None
            else:
                time_to_catch_up = calc_time(x1, y1, x2, y2, (abs(speed1)-abs(speed2)))
                x = time_to_catch_up*speed1*math.cos(r1) + x1
                y = time_to_catch_up*speed1*math.sin(r1) + y1
                return x, y, CarSize
        else:
            # print "Opposite direction"
            # Do something, there is a possibility to have a face to face collision
            return None
    else:
        # print "a1 != a2"
        x = (b2-b1)/(a1-a2)
        y = a1*x + b1
        # print str(x) + ":" + str(y)



        # This part is use to calculate if the intersection is at the front of the car or the back of the car
        dx1 = x - x1
        dy1 = y - y1
        d21 = dx1*dx1 + dy1*dy1
        if d21 == 0:
            return x, y, 0
        cos1 = math.acos(dx1/math.sqrt(d21))
        if dy1 < 0:
            cos1 = 2*math.pi - cos1

        dx2 = x - x2
        dy2 = y - y2
        d22 = dx2*dx2 + dy2*dy2
        if d22 == 0:
            return x, y, CarSize
        cos2 = math.acos(dx2/math.sqrt(d22))
        if dy2 < 0:
            cos2 = 2*math.pi - cos2

        # print "r, cos:" + str(r1) + ", " + str(cos1) + ":" + str(r2) + ", " + str(cos2)
        # check if the cars pass the collision point
        if abs(cos1 - r1) < 0.5 and abs(cos2 - r2) < 0.5:
            # both car1 and car2 have not yet passed the collision point
            # print "Case1"
            if speed1 < 0 or speed2 < 0:
                # print "Speed1 or Speed2 < 0"
                return None
            # print str(x) + "," + str(y)
            return x, y, 0
        elif abs(cos1 - r1) < 0.5 and abs(cos2 - r2) > 0.5:
            # car1 has not passed the collision point, but car2 passed
            # print "Case2"
            distance2 = math.sqrt(d22)
            if distance2 < CarSize:
                if speed1 < 0 or speed2 < 0:
                    return None
                return x, y, CarSize
            else:
                return None
        else:
            # car1 has passed the collision point
            return None


def calc_time(x1, y1, x2, y2, speed):
    distance = math.sqrt(math.pow((x1-x2), 2) + math.pow((y1-y2), 2))
    if speed == 0:
        if distance < CarSize:
            return 0
        else:
            return float('Inf')
    time = math.sqrt(math.pow((x1-x2), 2) + math.pow((y1-y2), 2))/speed
    return time