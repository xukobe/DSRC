__author__ = 'xuepeng'

import math
import Controller_Module.DSRC_Event as Event

stopSign = False

slowSign = True


def customized_event_handler(dsrc_unit, event):
    if event.type == Event.TYPE_CAR_CAR:
        x1 = dsrc_unit.position_tracker.x
        y1 = dsrc_unit.position_tracker.y
        r1 = dsrc_unit.position_tracker.radian

        coord = event.coordinates
        x2 = coord.x
        y2 = coord.y
        r2 = coord.radian

        (x, y) = calculate_collision_point(x1, y1, r1, x2, y2, r2)

        speed2 = event.action.arg1
        time1_f = calc_time(x1, y1, x, y, 30)
        time1_s = calc_time(x1, y1, x, y, 15)
        time2 = calc_time(x2, y2, x, y, speed2)

        print str(x) + ":" + str(y) + ":time_f:" + str(time1_f) + ":time_s:" + str(time1_s)

        if abs(time1_s - time2) <= 1:
            print "Stop"
            stopSign = True
        elif abs(time1_f - time2) <= 1:
            print "Slow down"
            stopSign = False
            slowSign = True
        else:
            print "Fast"
            stopSign = False
            slowSign = False


def calculate_collision_point(x1, y1, r1, x2, y2, r2):
    # line1 a and b
    a1 = math.tan(r1)
    b1 = y1 - a1*x1

    # line2 a and b
    a2 = math.tan(r2)
    b2 = y2 - a2*x2

    if abs(abs(a1)-abs(a2)) < 0.001:
        return None
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