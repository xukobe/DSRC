__author__ = 'xuepeng'

import time

from collections import deque
from threading import Condition, Thread
from iRobot_Module.create import Create

GO = "GO"
FAST_FORWARD = "FAST_FORWARD"
FAST_BACKWARD = "FAST_BACKWARD"
FORWARD = "FORWARD"
BACKWARD = "BACKWARD"
TURN_LEFT = "TURN LEFT"
TURN_RIGHT = "TURN RIGHT"
PAUSE = "PAUSE"

REGULAR_SPEED = 20
FAST_SPEED = 30
RADIUS_SPEED = 90

class job:
    """
    The class is used to send a single command to iRobot
    """
    def __init__(self, action, time, arg1 = None, arg2 = None):
        self.action = action
        self.time = time
        self.arg1 = arg1
        self.arg2 = arg2
        self.timeLeft = self.time
        self.finished = False
        self.currentJobStartTime = 0
        self.currentJobEndTime = 0

    def execute(self, robot, jobCondition):
        if not self.finished:
            jobCondition.acquire()
            self._do_job(robot)
            self.currentJobStartTime = time.time()
            jobCondition.wait(self.timeLeft)
            self.currentJobEndTime = time.time()
            self.timeLeft = self.timeLeft - (self.currentJobEndTime - self.currentJobStartTime)
            if self.timeLeft <= 0:
                self.finished = True
            else:
                self.finished = False
            jobCondition.release()
        else:
            pass
        # if self.action == PAUSE:
        #     self.robot.go(0,0)
        # elif self.action == FORWARD:
        #     self.robot.go(REGULAR_SPEED, 0)

    def _do_job(self,robot):
        print self.action
        # if self.action == PAUSE:
        #     robot.go(0, 0)
        # elif self.action == FORWARD:
        #     robot.go(REGULAR_SPEED, 0)
        # elif self.action == BACKWARD:
        #     robot.go(-REGULAR_SPEED, 0)
        # elif self.action == FAST_FORWARD:
        #     robot.go()
        # elif self.action == TURN_LEFT:
        #     robot.go(0, -RADIUS_SPEED)
        # elif self.action == TURN_RIGHT:
        #     robot.go(0, RADIUS_SPEED)

    def getTime(self):
        return self.time

    def isFinished(self):
        return self.finished


class jobGenerator:
    """
    The class is to generate a new job
    """
    def __init__(self):
        pass
    @staticmethod
    def generate_job(action, time):
        """
        :rtype : job
        """
        return job(action, time)

class processor(Thread):
    """
    Processor has a queue, which contain a list of jobs. These jobs will be executed one by one
    The pause and resume functionalities are implemented
    """
    def __init__(self, robot):
        Thread.__init__(self)
        self.robot = robot
        self.queue = deque()
        self.pause = True
        self.flowCondition = Condition()
        self.jobCondition = Condition()
        self.currentJob = None
        self.currentJobStartTime = 0
        self.currentJobEndTime = 0
        self.nextJob = True
        self.timeLeft = 0
        self.running = True

    def add_new_job(self, new_job):
        """
        add new job to processor
        :param new_job: The job to add
        """
        self.queue.append(new_job)

    def insert_new_job(self, new_job):
        """
        Insert a new job to left hand side of the queue
        The new job will be executed first
        :param new_job: new job to insert
        """
        self.queue.appendleft(new_job)

    def is_pause(self):
        """
        :return: the value of pause
        """
        return self.pause

    def get_number_of_jobs(self):
        """
        :return: The size of current queue
        """
        return len(self.queue)

    def run(self):
        while self.running:
            self.flowCondition.acquire()
            while self.pause:
                self.flowCondition.wait()
            self.flowCondition.release()

            if self.currentJob and self.currentJob.isFinished():
                self.currentJob = None

            if not self.currentJob:
                if len(self.queue) == 0:
                    self.pause = True
                    continue
                else:
                    self.currentJob = self.queue.popleft()

            self.currentJob.execute(self.robot, self.jobCondition)


    def pause_processor(self):
        """
        Pause the current processor and save the current state
        """
        self.pause = True
        self.jobCondition.acquire()
        self.jobCondition.notifyAll()
        self.jobCondition.release()
        # Generate a pause job and execute
        job = jobGenerator.generate_job(PAUSE,0)
        job.execute(self.robot, self.jobCondition)

    def resume_processor(self):
        """
        Resume the current job
        """
        print "Job resumed"
        self.pause = False
        self.flowCondition.acquire()
        self.flowCondition.notifyAll()
        self.flowCondition.release()

    def start_processor(self):
        """
        Start to process the job
        """
        self.start()
        self.resume_processor()

    def stop_processor(self):
        """
        Stop the current thread
        """
        self.running = False
        self.resume_processor()

def main():
    # robot = Create('/dev/ttyUSB0')
    job1 = jobGenerator.generate_job(FORWARD, 3)
    job2 = jobGenerator.generate_job(TURN_LEFT, 1)
    job3 = jobGenerator.generate_job(TURN_RIGHT, 1)
    job4 = jobGenerator.generate_job(FAST_FORWARD, 1)
    job5 = jobGenerator.generate_job(PAUSE,0)
    job6 = jobGenerator.generate_job(BACKWARD,3)
    job7 = jobGenerator.generate_job(PAUSE,0)
    proc = processor(None)
    proc.add_new_job(job1)
    proc.add_new_job(job2)
    proc.add_new_job(job3)
    proc.add_new_job(job4)
    proc.add_new_job(job5)
    proc.add_new_job(job6)
    proc.add_new_job(job7)
    proc.start_processor()
    while True:
        s = raw_input()
        if s == 'q':
            break
        elif s == 'p':
            proc.pause_processor()
        elif s == 'r':
            proc.resume_processor()
        elif s == 's':
            proc.stop_processor()
        elif s == 'ir':
            job8 = jobGenerator.generate_job(TURN_RIGHT,1)
            proc.insert_new_job(job8)


if __name__ == '__main__':
    main()