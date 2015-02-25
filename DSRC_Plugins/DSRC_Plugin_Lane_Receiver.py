__author__ = 'xuepeng'

import math

import Event_Module.DSRC_Event as Event


stopSign = False

slowSign = True


def customized_event_handler(dsrc_unit, event):
    global stopSign
    global slowSign
    if event.type == Event.TYPE_CAR_CAR:
        x1 = dsrc_unit.position_tracker.x
        y1 = dsrc_unit.position_tracker.y
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
            pass
        else:
            x = p[0]
            y = p[1]

            time1_f = calc_time(x1, y1, x, y, 30)
            time1_s = calc_time(x1, y1, x, y, 15)
            time2 = calc_time(x2, y2, x, y, speed2)

            # print str(x) + ":" + str(y) + ":time_f:" + str(time1_f) + ":time_s:" + str(time1_s) + ":time2:" + str(time2)

            if abs(time1_s - time2) <= 1:
                stopSign = True
            elif abs(time1_f - time2) <= 1:
                stopSign = False
                slowSign = True
            else:
                stopSign = False
                slowSign = False


def calculate_collision_point(x1, y1, r1, x2, y2, r2, speed1, speed2):
    # line1 a and b
    a1 = math.tan(r1)
    b1 = y1 - a1*x1

    # line2 a and b
    a2 = math.tan(r2)
    b2 = y2 - a2*x2

    if abs(abs(a1)-abs(a2)) < 0.001:
        if abs(b1 - b2) < 0.5 and speed1 <= speed2:
            return None
        else:
            time_to_catch_up = calc_time(x1, y1, x2, y2, (speed1-speed2))
            x = time_to_catch_up*speed1*math.cos(r1) + x1
            y = time_to_catch_up*speed1*math.sin(r1) + y1
            return (x, y)
    else:
        x = (b2-b1)/(a1-a2)
        y = a1*x + b1
        return (x, y)


def calc_time(x1, y1, x2, y2, speed):
    distance = math.sqrt(math.pow((x1-x2), 2) + math.pow((y1-y2), 2))
    if speed == 0:
        if distance < 1:
            return 0
        else:
            return float('Inf')
    time = math.sqrt(math.pow((x1-x2), 2) + math.pow((y1-y2), 2))/speed
    return time