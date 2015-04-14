__author__ = 'xuepeng'

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import math
from Event_Module import DSRC_Event, DSRC_Message_Coder
from Event_Module.DSRC_Message_Coder import MessageCoder
import DSRC_JobProcessor
import time
import thread
import DSRC_Plugins.DSRC_Plugin_Invoker as Plugin
import ConfigParser
import curses

from iRobot_Module.create import Create
from iRobot_Module.create_sensors import SensorCallback, CreateSensorDetector
import iRobot_Module.create_sensors as Create_Sensor
from Event_Module.DSRC_Event import EventListener
from Event_Module.DSRC_Event_Generator import USRPEventHandler
from DSRC_Messager_Module.DSRC_USRP_Connector import DsrcUSRPConnector
from DSRC_JobProcessor import JobProcessor, Job, JobCallback
from threading import Thread

from Event_Module.TransceiverSettings import TransceiverSetting
import Event_Module.TransceiverSettings as TS

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


class DSRCUnit(Thread, EventListener, JobCallback, SensorCallback):
    def __init__(self, unit_id, IP="127.0.0.1", socket_port=10124, robot_port="/dev/ttyUSB0",
                 unit_mode=DSRC_UNIT_MODE_FREE,
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
        self.IP = IP
        self.robot_port = robot_port
        self.unit_mode = unit_mode
        self.avoid_collision_mode = avoid_collision_mode

        # flag for plugin:
        self.flag_plugin_customized_event = False
        self.flag_plugin_customized_executor = False
        self.flag_plugin_customized_receiver = False

        # flag for message sending:
        self.flag_msg_car_car_send = True
        self.flag_msg_customized_send = False
        self.customized_time_counter = 0
        self.customized_time_intervals = 0
        self.dsrc_thread_update_interval = 0.05

        # for follow mode:
        self.target = None

        # USRP properties
        self.power = 90
        self.rate = 0

        try:
            self.load_ini()
            self.load_plugin()
        except Exception, e:
            print e

        self.car_info()

        # Handle the message from USRP, and generate event
        self.USRP_event_handler = USRPEventHandler(self.flag_plugin_customized_event)
        self.USRP_event_handler.set_listener(listener=self)
        # The connector between USRP and Controller module
        self.USRP_connect = DsrcUSRPConnector(self.IP, self.socket_port, self.USRP_event_handler)
        # iRobot
        # self.create = Create(self.robot_port)
        if self.robot_port != "None":
            self.create = Create(self.robot_port)
        else:
            self.create = None
        # A processor to process the robot job in order
        self.job_processor = JobProcessor(self.create)

        self.sensor_detector = CreateSensorDetector(create=self.create, callback=self)
        self.sensor_detector.start()

        self.position_tracker = DSRCPositionTracker(self.job_processor, 0, 0, 0)
        self.bg_thread = DSRCBGThread(self.bg_run)
        self.bg_thread.start()
        self.start()

    def load_ini(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config = ConfigParser.SafeConfigParser()
        config_ini_path = ''.join([dir_path, "/unit_config.ini"])
        config.read(config_ini_path)

        # CarInfo Section
        self.unit_id = config.get("CarInfo", "CarID")

        # Unit Setting
        self.dsrc_thread_update_interval = config.getfloat("UnitSetting", "MiniInterval")

        # Plugin Section
        self.flag_plugin_customized_event = config.getboolean("Plugin", "CustomizedEvent")
        self.flag_plugin_customized_executor = config.getboolean("Plugin", "CustomizedExecutor")
        self.flag_plugin_customized_receiver = config.getboolean("Plugin", "CustomizedReceiver")
        if self.flag_msg_customized_send:
            executor_module = Plugin.get_executor_module()
            if executor_module.SEND_INTERVALS:
                self.customized_time_intervals = executor_module.SEND_INTERVALS

        # Message Section
        self.flag_msg_car_car_send = config.getboolean("Message", "SendCarCar")
        self.flag_msg_customized_send = config.getboolean("Message", "SendCustomized")

        # Mode Section
        self.unit_mode = config.getint("Mode", "InitialMode")

        # Socket Section
        self.socket_port = config.getint("Socket", "PortNumber")

        # iRobot Section
        self.robot_port = config.get("iRobot", "Port")

        print config_ini_path

    def load_plugin(self):
        Plugin.load_plugin()

    def car_info(self):
        print "###################################################################"
        print "Car Unit:" + self.unit_id
        print "Listen to port:" + str(self.socket_port)
        print "iRobot port:" + self.robot_port
        print "Customized Event:" + str(self.flag_plugin_customized_event)
        print "Customized Executor:" + str(self.flag_plugin_customized_executor)
        print "Customized Receiver:" + str(self.flag_plugin_customized_receiver)
        print "Sending car_car message:" + str(self.flag_msg_car_car_send)
        print "Sending customized message:" + str(self.flag_msg_customized_send)
        if Plugin.plugin_name:
            print "Plugin:" + str(Plugin.plugin_name)
        print "Mode:" + str(self.unit_mode)
        if self.unit_mode == DSRC_UNIT_MODE_FOLLOW:
            print "Follow target:" + str(self.target)
        print "###################################################################"


    def bg_run(self):
        while self.running:
            self.position_tracker.update_secondary(self.dsrc_thread_update_interval)
            # Send car_car message
            if self.flag_msg_car_car_send:
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
                                                                               self.position_tracker.radian,
                                                                               self.power,
                                                                               self.rate,
                                                                               self.dsrc_thread_update_interval,
                                                                               self.sensor_detector.bump,
                                                                               self.sensor_detector.drop)
                self.send_to_USRP(msg)
                # self.USRP_connect.send_to_USRP(msg)

            # Send customized message
            if self.flag_plugin_customized_executor:
                if self.customized_time_counter < self.customized_time_intervals:
                    self.customized_time_counter += 1
                else:
                    Plugin.customized_execute(self)
                    self.customized_time_counter = 0

            time.sleep(self.dsrc_thread_update_interval)

    def run(self):
        while self.running:
            user_input = raw_input(self.unit_id + ">")
            if user_input == "help":
                self.help_info()
            elif user_input == 'quit':
                self.stop_self()
            elif user_input == "control":
                self.keyboard_control()
            elif user_input == "position":
                self.position_info()
            elif user_input == "safe mode":
                self.create.toSafeMode()
            elif user_input == "full mode":
                self.create.toFullMode()
            elif user_input == "reconnect":
                self.create.reconnect(self.robot_port)
            elif user_input == "setpos":
                self.setpos()
            elif user_input == 'set plugin':
                self.set_plugin()
            elif user_input == 'enable executor':
                self.set_executor(True)
            elif user_input == 'enable receiver':
                self.set_receiver(True)
            elif user_input == 'disable executor':
                self.set_executor(False)
            elif user_input == 'disable executor':
                self.set_receiver(False)
            elif user_input == 'info':
                self.car_info()
            elif user_input == "setPower":
                self.setPower()
            elif user_input == "setRate":
                self.setRate()
            else:
                Plugin.customized_cmd(self, user_input)
        print "User interaction thread is stopped!"

    def setpos(self):
        x_str = raw_input("X:")
        try:
            x = float(x_str)
        except ValueError, e:
            print "Cannot convert " + x_str + " into a number."
            return
        y_str = raw_input("Y:")
        try:
            y = float(y_str)
        except ValueError, e:
            print "Cannot convert " + y_str + " into a number."
            return
        radian_str = raw_input("Radian:")
        try:
            radian = float(radian_str)
        except ValueError, e:
            print "Cannot convert " + radian_str + " into a number."
            return
        self.position_tracker.set_pos(x, y, radian)

    # Free style control
    def keyboard_control(self):
        screen = curses.initscr()
        screen.keypad(True)
        screen.clear()
        instruction = "'w' or up_arrow to go forward\n" \
                      "'s' or down_arrow to go backward\n" \
                      "'a' or left_arrow to turn left\n" \
                      "'d' or right_arrow to turn right\n" \
                      "'p' or space to pause\n" \
                      "'q' or esc to quit"
        screen.addstr(instruction)
        curses.noecho()
        while True:
            c = screen.getch()
            if c == ord("w") or c == curses.KEY_UP:
                self.do_action(ROBOT_FORWARD)
            elif c == ord("s") or c == curses.KEY_DOWN:
                self.do_action(ROBOT_BACKWARD)
            elif c == ord("a") or c == curses.KEY_LEFT:
                self.do_action(ROBOT_TURN_LEFT)
            elif c == ord("d") or c == curses.KEY_RIGHT:
                self.do_action(ROBOT_TURN_RIGHT)
            elif c == ord("p") or c == ord(" "):
                self.do_action(ROBOT_PAUSE)
            elif c == ord("q") or c == curses.KEY_EXIT:
                break
            else:
                pass
            time.sleep(0.01)

        curses.endwin()

    def position_info(self):
        print "X: " + str(self.position_tracker.x)
        print "Y: " + str(self.position_tracker.y)
        print "Direction: " + str((self.position_tracker.radian/math.pi)*180)

    def help_info(self):
        print "Empty"

    def welcome_info(self):
        print "Welcome to DSRC System!"
        print "Don't know what to do? Type help to explore the system!"

    def set_unit_mode(self, mode):
        self.unit_mode = mode

    def set_plugin(self):
        plugin_name = raw_input("Plugin Name:")
        Plugin.set_plugin(plugin_name)

    def set_executor(self, b):
        self.flag_plugin_customized_executor = b

    def set_receiver(self, b):
        self.flag_plugin_customized_receiver = b

    def set_avoid_collision(self, isAvoid):
        self.avoid_collision_mode = isAvoid

    def setPower(self):
        power_str = raw_input("Power:")
        try:
            power = int(power_str)
        except ValueError, e:
            print "Cannot convert " + power_str + " into a number."
            return
        msg = TransceiverSetting.generate_power_setting_msg(power)
        self.send_to_USRP(msg)

    def setRate(self):
        rate_str = raw_input("Rate:")
        try:
            rate = int(rate_str)
        except ValueError, e:
            print "Cannot convert " + rate_str + " into a number."
            return
        msg = TransceiverSetting.generate_power_setting_msg(rate)
        self.send_to_USRP(msg)

    # Simple Interface for iRobot Control
    def do_action(self, simple_action):
        if simple_action == ROBOT_PAUSE:
            job = Job(self, DSRC_JobProcessor.GO, 0, 0, 0)
            self.job_processor.add_new_job(job)
        elif simple_action == ROBOT_FORWARD:
            job = Job(self, DSRC_JobProcessor.GO, None, ROBOT_REGULAR_SPEED, 0)
            self.job_processor.add_new_job(job)
        elif simple_action == ROBOT_BACKWARD:
            job = Job(self, DSRC_JobProcessor.GO, None, -ROBOT_REGULAR_SPEED, 0)
            self.job_processor.add_new_job(job)
        elif simple_action == ROBOT_TURN_LEFT:
            job1 = Job(self, DSRC_JobProcessor.GO, 90/ROBOT_RADIUS_SPEED, 0, ROBOT_RADIUS_SPEED)
            current_job = self.job_processor.currentJob
            if current_job:
                job2 = Job(self, current_job.action, current_job.timeLeft, current_job.arg1, current_job.arg2)
            else:
                job2 = Job(self, DSRC_JobProcessor.GO, 0, 0, 0)
            self.job_processor.add_new_job(job1)
            self.job_processor.add_new_job(job2)
        elif simple_action == ROBOT_TURN_RIGHT:
            job1 = Job(self, DSRC_JobProcessor.GO, 90/ROBOT_RADIUS_SPEED, 0, -ROBOT_RADIUS_SPEED)
            current_job = self.job_processor.currentJob
            if current_job:
                job2 = Job(self, current_job.action, current_job.timeLeft, current_job.arg1, current_job.arg2)
            else:
                job2 = Job(self, DSRC_JobProcessor.GO, 0, 0, 0)
            self.job_processor.add_new_job(job1)
            self.job_processor.add_new_job(job2)
        self.job_processor.cancel_current_job()

    def do_accurate_action(self, arg1, arg2):
        job = Job(self, DSRC_JobProcessor.GO, None, arg1, arg2)
        self.job_processor.add_new_job(job)
        self.job_processor.cancel_current_job()

    def send_to_USRP(self, msg_obj):
        msg = MessageCoder.encode(msg_obj)
        self.USRP_connect.send_to_USRP(msg)

    def sensor_event_handler(self, events):
        if Create_Sensor.EVENT_WHEEL_DROP in events:
            self.job_processor.pause_processor()
            #send wheel drop to monitor

        if Create_Sensor.EVENT_BUMP in events:
            self.job_processor.pause_processor()
            #send bump to monitor


    def usrp_event_received(self, event):
        if not event:
            return

        if event.type == TS.TYPE_VALUE:
            self.power = event.power
            self.rate = event.rate
            return

        if event.source == self.unit_id:
            return

        if event.destination in (DSRC_Event.DESTINATION_ALL, self.unit_id):
            if event.type == DSRC_Event.TYPE_MONITOR_CAR:
                self.send_ack(event.seq)
                if event.sub_type == DSRC_Event.SUBTYPE_SETTING:
                    if event.setting.name == DSRC_Event.SETTINGS_NAME_MINI_INTERVAL:
                        self.dsrc_thread_update_interval = event.setting.value
                    elif event.setting.name == DSRC_Event.SETTINGS_NAME_STYLE:
                        value = event.setting.value
                        if value == DSRC_Event.SETTINGS_NAME_STYLE_LEAD:
                            self.unit_mode = DSRC_UNIT_MODE_LEAD
                        elif value == DSRC_Event.SETTINGS_NAME_STYLE_FOLLOW:
                            self.unit_mode = DSRC_UNIT_MODE_FOLLOW
                        elif value == DSRC_Event.SETTINGS_NAME_STYLE_FREE:
                            self.unit_mode = DSRC_UNIT_MODE_FREE
                        elif value == DSRC_Event.SETTINGS_NAME_STYLE_CUSTOMIZED:
                            self.unit_mode = DSRC_UNIT_MODE_CUSTOMIZED
                elif event.sub_type == DSRC_Event.SUBTYPE_CMD:
                    if event.command.name == DSRC_Event.COMMAND_NAME_SAFE_MODE:
                        if self.create:
                            self.create.toSafeMode()
                    elif event.command.name == DSRC_Event.COMMAND_NAME_FULL_MODE:
                        if self.create:
                            self.create.toSafeMode()
                    elif event.command.name == DSRC_Event.COMMAND_NAME_STOP:
                        self.job_processor.clear_all_jobs()
                    elif event.command.name == DSRC_Event.COMMAND_NAME_GO:
                        args = event.command.args
                        self.do_accurate_action(args[0], args[1])
                    elif event.command.name == DSRC_Event.COMMAND_NAME_GO_TO:
                        args = event.command.args
                        self.job_processor.clear_all_jobs()
                        jobs = self.position_tracker.jobs_to_go(args[0], args[1])
                        job1_args = jobs['job1']
                        job2_args = jobs['job2']
                        job1 = Job(self, DSRC_JobProcessor.GO, job1_args[2], job1_args[0], job1_args[1])
                        job2 = Job(self, DSRC_JobProcessor.GO, job2_args[2], job2_args[0], job2_args[1])
                        self.job_processor.add_new_job(job1)
                        self.job_processor.add_new_job(job2)
                    elif event.command.name == DSRC_Event.COMMAND_NAME_PLUGIN:
                        args = event.command.args
                        plugin_name = args[0]
                        Plugin.set_plugin(plugin_name)
                        self.set_executor(True)
                        self.set_receiver(True)
                    elif event.command.name == DSRC_Event.COMMAND_NAME_DISABLE_PLUGIN:
                        self.set_executor(False)
                        self.set_receiver(False)
                    elif event.command.name == DSRC_Event.COMMAND_NAME_ASK_PLUGIN:
                        for plugin_key in Plugin.plugins:
                            self.send_plugin_to_monitor(plugin_key)
                            time.sleep(0.05)
                    elif event.command.name == DSRC_Event.COMMAND_NAME_FOLLOW:
                        args = event.command.args
                        target = args[0]
                        self.target = target
                    elif event.command.name == DSRC_Event.COMMAND_NAME_SET_POS:
                        args = event.command.args
                        x = args[0]
                        y = args[1]
                        radian = args[2]
                        self.position_tracker.set_pos(x, y, radian)

                elif event.sub_type == DSRC_Event.SUBTYPE_BATCH:
                    event_job = event.batch.job
                    job = Job(self, event_job.action.name, event_job.time, event_job.action.arg1, event_job.action.arg2)
                    self.job_processor.add_new_job(job)
            else:
                if self.unit_mode == DSRC_UNIT_MODE_FOLLOW:
                    self._follow_mode_received(event)
                elif self.unit_mode == DSRC_UNIT_MODE_LEAD:
                    self._lead_mode_received(event)
                elif self.unit_mode == DSRC_UNIT_MODE_CUSTOMIZED:
                    self._customized_mode_received(event)

    def send_ack(self, seq):
        msg = MessageCoder.generate_monitor_car_ack(self.unit_id,
                                                    'monitor',
                                                    (seq+1))
        self.send_to_USRP(msg)

    def send_plugin_to_monitor(self, plugin):
        args = [plugin]
        msg = MessageCoder.generate_command_message(self.unit_id,
                                                    'monitor',
                                                    DSRC_Event.COMMAND_NAME_RESPONSE_PLUGIN,
                                                    args)
        self.send_to_USRP(msg)

    def _follow_mode_received(self, event):
        if event.type == DSRC_Event.TYPE_CAR_CAR:
            print "Follow: " + str(event.source) + ":" + str(self.target)
            if self.target:
                print self.target + " is not None."
                if event.source == self.target:
                    print "event source == self.target"
                    action = event.action
                    print str(action.name) + ":" + str(action.arg1) + str(action.arg2)
                    new_job = Job(jobCallback=self, action=action.name, arg1=action.arg1, arg2=action.arg2, arg_time=None)
                    self.job_processor.add_new_job(new_job)
                    self.job_processor.cancel_current_job()

    def _lead_mode_received(self, event):
        if event.type == DSRC_Event.TYPE_MONITOR_CAR:
            print "Lead mode - Monitor_car"

    def _customized_mode_received(self, event):
        if self.flag_plugin_customized_receiver:
            # print "Customized mode receiver invoked"
            Plugin.customized_event_handler(self, event)

    def irobot_event_received(self, event):
        # TODO:
        print "iRobot event functionality is not yet implemented!"

    # job callback
    def job_finished(self, action, arg1, arg2, timeExecuted):
        if action == DSRC_JobProcessor.GO:
            self.position_tracker.update_primary(arg1, arg2, timeExecuted)

    # job callback
    def job_paused(self, action, arg1, arg2, timeExecuted):
        if action == DSRC_JobProcessor.GO:
            self.position_tracker.update_primary(arg1, arg2, timeExecuted)

    def stop_self(self):
        self.job_processor.stop_processor()
        self.USRP_event_handler.stop_self()
        self.USRP_connect.stop_self()
        self.sensor_detector.stop_self()
        self.running = False
        exit()


class DSRCBGThread(Thread):
    def __init__(self, bg_thread_func):
        Thread.__init__(self)
        self.running = True
        self.bg_func = bg_thread_func

    def run(self):
        self.bg_func()
        print "Background thread is stopped!"


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
        if not self.processor.pause:
            if job:
                if job.action == DSRC_JobProcessor.GO:
                    with self.pos_lock:
                        self._calculate_secondary_position(job.arg1, job.arg2, update_interval)
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

    def set_pos(self, x, y, radian):
        with self.pos_lock:
            self.x = self._x = x
            self.y = self._y = y
            self.radian = self._radian =radian

    def jobs_to_go(self, x, y):
        dx = x - self.x
        dy = y - self.y
        d2 = dx*dx + dy*dy
        if d2:
            radian = math.asin(float(dy)/math.sqrt(d2))
            if dx < 0:
                radian = math.pi - radian
            radian = radian % ( 2 * math.pi)
            d_radian = radian - self.radian
            if d_radian >= 0:
                if d_radian > math.pi:
                    d_radian = (2 * math.pi) - d_radian
                    a_speed = -45
                    a_time = d_radian / (math.pi/4)
                else:
                    a_speed = 45
                    a_time = d_radian / (math.pi/4)
            else:
                if d_radian < -math.pi:
                    d_radian = (2 * math.pi) + d_radian
                    a_speed = 45
                    a_time = d_radian / (math.pi/4)
                else:
                    a_speed = -45
                    a_time = abs(d_radian) / (math.pi/4)
            job_rotate = [0, a_speed, a_time]
            distance = math.sqrt(d2)
            d_time = distance / ROBOT_REGULAR_SPEED
            job_go = [ROBOT_REGULAR_SPEED, 0, d_time]
            jobs = {'job1': job_rotate, 'job2': job_go}
            return jobs
        return None

    # def stop_self(self):
    #     self.running = False

# class MonitorCarEventHandler:
#     def __init__(self, dsrc_unit, sender):
#         self.unit = dsrc_unit
#         self.sender = sender
#         self.queue_size = 10
#         self.queue = []
#
#     def handle_event(self, event):
#         seq = event.seq
#         self._send_ack(seq+1)
#         # if seq in self.queue:
#
#     def _send_ack(self, seq):
#         msg = MessageCoder.generate_monitor_car_ack(self.unit.unit_id,
#                                                     'monitor',
#                                                     seq)
#         self.USRP_connect.send_to_USRP(msg)


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
    # unit.set_unit_mode(DSRC_UNIT_MODE_FOLLOW)
    unit.join()


def test_lead_mode():
    unit = DSRCUnit("car1")
    # unit.set_unit_mode(DSRC_UNIT_MODE_LEAD)
    unit.join()


def main():
    pass

if __name__ == '__main__':
    test_follow_mode()
