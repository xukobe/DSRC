__author__ = 'xuepeng'

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import math
import DSRC_Event
import DSRC_JobProcessor
import time
import thread
import DSRC_Message_Coder
import DSRC_Plugins as plugin
import ConfigParser

from DSRC_Event import USRPEventHandler, EventListener, Event
from DSRC_USRP_Connector import DsrcUSRPConnector
from DSRC_JobProcessor import JobProcessor, Job, JobCallback
from iRobot_Module.create import Create
from threading import Thread, Lock


DSRC_UNIT_MODE_LEAD = 1
DSRC_UNIT_MODE_FOLLOW = 2
DSRC_UNIT_MODE_FREE = 3
DSRC_UNIT_MODE_CUSTOMIZED = 4

ROBOT_FAST_FORWARD = "fast_forward"
ROBOT_FAST_BACKWARD = "fast_backward"
ROBOT_FORWARD = "forward"
ROBOT_BACKWARD = "backward"
ROBOT_TURN_LEFT = "turn left"
ROBOT_TURN_RIGHT = "turn right"
ROBOT_PAUSE = "pause"

ROBOT_REGULAR_SPEED = 30
ROBOT_FAST_SPEED = 35
ROBOT_RADIUS_SPEED = 90

DSRC_THREAD_UPDATE_INTERVAL = 0.05


class DSRCUnit(Thread, EventListener, JobCallback):
    def __init__(self, unit_id, socket_port=10123, robot_port="/dev/ttyUSB0", unit_mode=DSRC_UNIT_MODE_FREE,
                 avoid_collision_mode=False):
        """
        :param unit_id: The ID of the car unit
        :param socket_port: The port number of the socket, which is used to connect USRP module.
        :param robot_port: The USB port for the iRobot
        :param unit_mode: The mode of the car unit
        :param avoid_collision_mode: Emergency mode.
        """
        Thread.__init__(self)
        self.running = True
        self.unit_id = unit_id
        self.socket_port = socket_port
        self.robot_port = robot_port
        self.unit_mode = unit_mode
        self.avoid_collision_mode = avoid_collision_mode

        # Handle the message from USRP, and generate event
        self.USRP_event_handler = USRPEventHandler()
        self.USRP_event_handler.set_listener(listener=self)
        # The connector between USRP and Controller module
        self.USRP_connect = DsrcUSRPConnector(self.socket_port, self.USRP_event_handler)
        # iRobot
        self.create = Create(self.robot_port)
        # self.create = None
        # A processor to process the robot job in order
        self.job_processor = JobProcessor(self.create)
        self.position_tracker = DSRCPositionTracker(self.job_processor, 0, 0, 0)
        self.car_info()
        self.bg_thread = DSRCBGThread(self.bg_run)
        self.bg_thread.start()
        self.start()

        # flag for message sending:
        self.car_car_send_flag = True
        self.customized_send_flag = False
        self.customized_time_counter = 0
        self.customized_time_intervals = 0

        # flag for

    def load_ini(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config = ConfigParser.SafeConfigParser()
        config_ini_path = ''.join([dir_path, "/unit_config.ini"])
        print config_ini_path

    def bg_run(self):
        while self.running:
            self.position_tracker.update_secondary(DSRC_THREAD_UPDATE_INTERVAL)
            # Send car_car message
            if self.car_car_send_flag:
                current_job = self.job_processor.currentJob
                if current_job:
                    action = current_job.action
                    arg1 = current_job.arg1
                    arg2 = current_job.arg2
                else:
                    action = DSRC_JobProcessor.GO
                    arg1 = 0
                    arg2 = 0
                msg = DSRC_Message_Coder.MessageCoder.generate_car_car_message(self.unit_id, DSRC_Event.DESTINATION_ALL,
                                                                               action, arg1, arg2,
                                                                               self.position_tracker.x,
                                                                               self.position_tracker.y,
                                                                               self.position_tracker.radian)
                self.USRP_connect.send_to_USRP(msg)

            # Send customized message
            if self.customized_send_flag:
                if self.customized_time_counter < self.customized_time_intervals:
                    self.customized_time_counter += 1
                else:
                    plugin.customized_msg_sender(self)
                    self.customized_time_counter = 0

            time.sleep(DSRC_THREAD_UPDATE_INTERVAL)

    def run(self):
        while self.running:
            user_input = raw_input(self.unit_id + ">")
            if user_input == "help":
                self.help_info()
            elif user_input == 'q':
                self.stop_self()
            elif user_input == "w":
                self.do_action(ROBOT_FORWARD)
            elif user_input == "s":
                self.do_action(ROBOT_BACKWARD)
            elif user_input == "a":
                self.do_action(ROBOT_TURN_LEFT)
            elif user_input == "d":
                self.do_action(ROBOT_TURN_RIGHT)
            elif user_input == "p":
                self.do_action(ROBOT_PAUSE)
            else:
                pass

    def help_info(self):
        print "Empty"

    def welcome_info(self):
        print "Welcome to DSRC System!"
        print "Don't know what to do? Type help to explore the system!"

    def car_info(self):
        print "Car Unit:" + self.unit_id

    def set_unit_mode(self, mode):
        self.unit_mode = mode

    def set_avoid_collision(self, isAvoid):
        self.avoid_collision_mode = isAvoid

    # Simple Interface for iRobot Control
    def do_action(self, simple_action):
        if simple_action == ROBOT_PAUSE:
            job = Job(self, DSRC_JobProcessor.GO, 0, 0, 0)
            self.job_processor.add_new_job(job)
        elif simple_action == ROBOT_FORWARD:
            job = Job(self, DSRC_JobProcessor.GO, 0, ROBOT_REGULAR_SPEED, 0)
            self.job_processor.add_new_job(job)
        elif simple_action == ROBOT_BACKWARD:
            job = Job(self, DSRC_JobProcessor.GO, 0, -ROBOT_REGULAR_SPEED, 0)
            self.job_processor.add_new_job(job)
        elif simple_action == ROBOT_TURN_LEFT:
            job1 = Job(self, DSRC_JobProcessor.GO, 90/ROBOT_RADIUS_SPEED, 0, ROBOT_RADIUS_SPEED)
            current_job = self.job_processor.currentJob
            job2 = Job(self, current_job.action, current_job.timeLeft, current_job.arg1, current_job.arg2)
            self.job_processor.add_new_job(job1)
            self.job_processor.add_new_job(job2)
        elif simple_action == ROBOT_TURN_RIGHT:
            job1 = Job(self, DSRC_JobProcessor.GO, 90/ROBOT_RADIUS_SPEED, 0, -ROBOT_RADIUS_SPEED)
            current_job = self.job_processor.currentJob
            job2 = Job(self, current_job.action, current_job.timeLeft, current_job.arg1, current_job.arg2)
            self.job_processor.add_new_job(job1)
            self.job_processor.add_new_job(job2)

    def usrp_event_received(self, event):
        if not event:
            return
        if event.source == self.unit_id:
            return

        if event.destination in (DSRC_Event.DESTINATION_ALL, self.unit_id):
            if self.unit_mode == DSRC_UNIT_MODE_FOLLOW:
                self._follow_mode_received(event)
            elif self.unit_mode == DSRC_UNIT_MODE_LEAD:
                self._lead_mode_received(event)
            elif self.unit_mode == DSRC_UNIT_MODE_CUSTOMIZED:
                self._customized_mode_received(event)

    def _follow_mode_received(self, event):
        if event.type == DSRC_Event.TYPE_CAR_CAR:
            action = event.action
            new_job = Job(jobCallback=self, action=action.name, arg1=action.arg1, arg2=action.arg2, time=0)
            self.job_processor.add_new_job(new_job)
        elif event.type == DSRC_Event.TYPE_MONITOR_CAR:
            print "Follow mode - Monitor_car"

    def _lead_mode_received(self, event):
        if event.type == DSRC_Event.TYPE_MONITOR_CAR:
            print "Lead mode - Monitor_car"

    def _customized_mode_received(self, event):
        plugin.customized_event_handler(self, event)

    def irobot_event_received(self, event):
        # TODO:
        print "iRobot event functionality is not yet implemented!"

    def job_finished(self, action, arg1, arg2, timeExecuted):
        if action == DSRC_JobProcessor.GO:
            self.position_tracker.update_primary(arg1, arg2, timeExecuted)

    def job_paused(self, action, arg1, arg2, timeExecuted):
        if action == DSRC_JobProcessor.GO:
            self.position_tracker.update_primary(arg1, arg2, timeExecuted)

    def stop_self(self):
        self.job_processor.stop_processor()
        # self.position_tracker.stop_self()
        self.USRP_event_handler.stop_self()
        self.USRP_connect.stop_self()
        self.running = False
        exit()


class DSRCBGThread(Thread):
    def __init__(self, bg_thread_func):
        Thread.__init__(self)
        self.running = True
        self.bg_func = bg_thread_func

    def run(self):
        self.bg_func()


# TODO: Create a position calculation looper with 0.01s interval. The position can be classified into two different types
# TODO: based on accuracy. The looper calculate the secondary position, while the job event can calculate primary position

class DSRCPositionTracker:
    def __init__(self, processor, x=0, y=0, radian=0):
        """
        :param processor: JobProcessor
        :param x: x coordinate, in cm
        :param y: y coordinate, in cm
        :param radian: the direction in which the car facing
        """
        self.processor = processor
        # secondary position
        self.x = x
        self.y = y
        self.radian = radian
        # primary position
        self._x = x
        self._y = y
        self._radian = radian
        # primary updated
        self.primary_updated = True
        # self.running = True
        self.pos_lock = thread.allocate_lock()

    def update_secondary(self, update_interval):
        job = self.processor.currentJob
        if job:
            if job.action == DSRC_JobProcessor.GO:
                with self.pos_lock:
                    self._calculate_secondary_position(job.arg1, job.arg2, update_interval)
                    if self.processor.pause:
                        self._x = self.x
                        self._y = self.y
                        self._radian = self.radian
                    self.primary_updated = False

    #TODO: test the method
    def _calculate_secondary_position(self, arg1, arg2, arg_time):
        if arg1 == 0:
            # if the velocity is 0, calculate the radians by the multiplication of angular velocity and time
            radian_per_sec = math.radians(arg2)
            radian = radian_per_sec * arg_time
            self.radian = (self.radian + radian) % (2 * math.pi)
        elif arg2 == 0:
            # if angular velocity is 0, calculate the x velocity and y velocity
            # and then the distance moved in both x and y
            x_velocity = arg1 * math.cos(self.radian)
            y_velocity = arg1 * math.sin(self.radian)
            self.x += x_velocity * arg_time
            self.y += y_velocity * arg_time
        else:
            radian_pos = {'x': self.x, 'y': self.y, 'radian': self.radian}
            new_radian_pos = DSRCPositionTracker.calculate_pos(radian_pos, arg1, arg2, arg_time)
            self.x = new_radian_pos['x']
            self.y = new_radian_pos['y']
            self.radian = new_radian_pos['radian']
        # print "Position:"+str(self.x) + ":" + str(self.y) + ":" + str(self.radian)

    @staticmethod
    def calculate_pos(radian_pos, arg1, arg2, arg_time):
        """
        :param radian_pos: radian, x and y. radian_pos['x'] is x, radian_pos['y'] is y, radian_pos['radian'] is radian
        :param arg1: velocity
        :param arg2: angular velocity
        :param arg_time: execution time
        :return: new radian_pos with the same format
        """
        radian_per_sec = math.radians(arg2)
        radius = arg1 / radian_per_sec
        radian = radian_per_sec * arg_time
        # create polar coordinate system with current point as origin and the direction of velocity as x axis
        # The distance between new point and current point is
        l = 2 * radius * math.sin(radian/2)
        # The angle is
        theta = radian/2

        # Do a coordinate transformation
        new_theta = theta + radian_pos['radian']
        #     Polar system to cartesian system
        x = l * math.cos(new_theta)
        y = l * math.sin(new_theta)
        new_x = x + radian_pos['x']
        new_y = y + radian_pos['y']
        new_radian = ((radian + radian_pos['radian']) % (2 * math.pi))
        new_radian_pos = {'x': new_x, 'y': new_y, 'radian': new_radian}
        return new_radian_pos

    # def run(self):
    #     while self.running:
    #         self._update_secondary()
    #         time.sleep(DSRC_POSITION_UPDATE_INTERVAL)

    def update_primary(self, arg1, arg2, arg_time):
        with self.pos_lock:
            if arg1 == 0:
                # if the velocity is 0, calculate the radians by the multiplication of angular velocity and time
                radian_per_sec = math.radians(arg2)
                radian = radian_per_sec * arg_time
                self._radian = self.radian = ((self._radian + radian) % (2 * math.pi))
            elif arg2 == 0:
                # if angular velocity is 0, calculate the x velocity and y velocity
                # and then the distance moved in both x and y
                x_velocity = arg1 * math.cos(self.radian)
                y_velocity = arg1 * math.sin(self.radian)
                self.x = self._x = (self._x + x_velocity * arg_time)
                self.y = self._y = (self._y + y_velocity * arg_time)
            else:
                radian_pos = {'x': self._x, 'y': self._y, 'radian': self._radian}
                new_radian_pos = DSRCPositionTracker.calculate_pos(radian_pos, arg1, arg2, arg_time)
                self._x = self.x = new_radian_pos['x']
                self._y = self.y = new_radian_pos['y']
                self._radian = self.radian = new_radian_pos['radian']
            self.primary_updated = True
        # print "Position:"+str(self.x) + ":" + str(self.y) + ":" + str(self.radian)

    # def stop_self(self):
    #     self.running = False


def test_position():
    unit = DSRCUnit("car1")
    job1 = Job(unit, DSRC_JobProcessor.GO, 8, 30, 45)
    job2 = Job(unit, DSRC_JobProcessor.GO, 1, 0, 90)
    job3 = Job(unit, DSRC_JobProcessor.GO, 1, 0, -90)
    job4 = Job(unit, DSRC_JobProcessor.GO, 1, 30, 0)
    job5 = Job(unit, DSRC_JobProcessor.GO, 0, 0, 0)
    job6 = Job(unit, DSRC_JobProcessor.GO, 3, -20, 0)
    job7 = Job(unit, DSRC_JobProcessor.GO, 0, 0, 0)
    unit.job_processor.add_new_job(job1)
    unit.job_processor.add_new_job(job2)
    unit.job_processor.add_new_job(job3)
    unit.job_processor.add_new_job(job4)
    unit.job_processor.add_new_job(job5)
    unit.job_processor.add_new_job(job6)
    unit.job_processor.add_new_job(job7)
    while True:
        s = raw_input()
        if s == 'q':
            break
        elif s == 'p':
            unit.job_processor.pause_processor()
        elif s == 'r':
            unit.job_processor.resume_processor()
        elif s == 's':
            unit.stop_self()
        elif s == 'ir':
            job8 = Job(unit, DSRC_JobProcessor.GO, 1, 0, 90)
            unit.job_processor.insert_new_job(job8)

def test_follow_mode():
    unit = DSRCUnit("car2")
    unit.set_unit_mode(DSRC_UNIT_MODE_FOLLOW)
    unit.join()

def test_lead_mode():
    unit = unit = DSRCUnit("car1")
    unit.set_unit_mode(DSRC_UNIT_MODE_LEAD)
    unit.join()

def main():
    pass

if __name__ == '__main__':
    args = sys.argv
    if args[1] == "follow":
        test_follow_mode()
    else:
        test_lead_mode()