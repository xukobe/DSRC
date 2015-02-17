__author__ = 'xuepeng'

import time

from collections import deque
from threading import Condition, Thread
from iRobot_Module.create import Create

GO = "go"
FAST_FORWARD = "fast_forward"
FAST_BACKWARD = "fast_backward"
FORWARD = "forward"
BACKWARD = "backward"
TURN_LEFT = "turn left"
TURN_RIGHT = "turn right"
PAUSE = "pause"

REGULAR_SPEED = 20
FAST_SPEED = 30
RADIUS_SPEED = 90


class JobCallback:
    def __init__(self):
        pass

    def job_paused(self, action, arg1, arg2, timeExecuted):
        raise NotImplementedError("JobCallback is not implemented yet!")

    def job_finished(self, action, arg1, arg2, timeExecuted):
        raise NotImplementedError("JobCallback is not implemented.")

class Job:
    """
    The class is used to send a single command to iRobot
    """
    def __init__(self, jobCallback, action, arg_time, arg1=None, arg2=None):
        self.jobCallback = jobCallback
        self.action = action
        self.time = arg_time
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
            if self.time == None:
                jobCondition.wait()
            else:
                jobCondition.wait(self.timeLeft)
            self.currentJobEndTime = time.time()
            time_executed = (self.currentJobEndTime - self.currentJobStartTime)
            if not self.time:
                self.timeLeft = 0
            else:
                self.timeLeft = self.timeLeft - time_executed
            if self.timeLeft <= 0:
                self.finished = True
                if self.jobCallback:
                    self.jobCallback.job_finished(self.action, self.arg1, self.arg2, time_executed)
            else:
                self.finished = False
                if self.jobCallback:
                    self.jobCallback.job_paused(self.action, self.arg1, self.arg2, time_executed)
            jobCondition.release()
        else:
            pass
        # if self.action == PAUSE:
        #     self.robot.go(0,0)
        # elif self.action == FORWARD:
        #     self.robot.go(REGULAR_SPEED, 0)

    def _do_job(self, robot):
        # print self.action + ":" + str(self.arg1) + ":" + str(self.arg2)
        if robot:
            if self.action == GO:
                robot.go(self.arg1, self.arg2)
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

class JobProcessor(Thread):
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
        self.start()

    def add_new_job(self, new_job):
        """
        add new job to processor
        :param new_job: The job to add
        """
        self.queue.append(new_job)
        if self.pause:
            self.resume_processor()

    def insert_new_job(self, new_job):
        """
        Insert a new job to left hand side of the queue
        The new job will be executed first
        :param new_job: new job to insert
        """
        self.queue.appendleft(new_job)
        if self.pause:
            self.resume_processor()

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

            if not self.currentJob or self.currentJob.isFinished():
                if len(self.queue) == 0:
                    self.pause_processor()
                    continue
                else:
                    self.currentJob = self.queue.popleft()

            self.currentJob.execute(self.robot, self.jobCondition)
        print "Job processor is stopped!"

    def cancel_current_job(self):
        if self.currentJob:
            self.currentJob.time = None
        self.jobCondition.acquire()
        self.jobCondition.notifyAll()
        self.jobCondition.release()

    def pause_processor(self, save_state=True):
        """
        Pause the current processor and save the current state
        :param save_state: Save the state of current job if true, discard current job otherwise
        """
        self.pause = True
        self.jobCondition.acquire()
        self.jobCondition.notifyAll()
        self.jobCondition.release()
        # Generate a pause job and execute
        job = Job(None, GO, 0, 0, 0)
        job.execute(self.robot, self.jobCondition)
        if not save_state:
            self.currentJob = None

    def resume_processor(self):
        """
        Resume the current job
        """
        # print "Job resumed"
        self.pause = False
        self.flowCondition.acquire()
        self.flowCondition.notifyAll()
        self.flowCondition.release()

    def start_processor(self):
        """
        Start to process the job
        """
        self.resume_processor()

    def stop_processor(self):
        """
        Stop the current thread
        """
        self.queue.clear()
        self.running = False
        self.cancel_current_job()
        self.resume_processor()

def main():
    pass
    # robot = Create('/dev/ttyUSB0')
    # job1 = JobGenerator.generate_job(FORWARD, 3)
    # job2 = JobGenerator.generate_job(TURN_LEFT, 1)
    # job3 = JobGenerator.generate_job(TURN_RIGHT, 1)
    # job4 = JobGenerator.generate_job(FAST_FORWARD, 1)
    # job5 = JobGenerator.generate_job(PAUSE,0)
    # job6 = JobGenerator.generate_job(BACKWARD,3)
    # job7 = JobGenerator.generate_job(PAUSE,0)
    # proc = JobProcessor(None)
    # proc.add_new_job(job1)
    # proc.add_new_job(job2)
    # proc.add_new_job(job3)
    # proc.add_new_job(job4)
    # proc.add_new_job(job5)
    # proc.add_new_job(job6)
    # proc.add_new_job(job7)
    # proc.start_processor()
    # while True:
    #     s = raw_input()
    #     if s == 'q':
    #         break
    #     elif s == 'p':
    #         proc.pause_processor()
    #     elif s == 'r':
    #         proc.resume_processor()
    #     elif s == 's':
    #         proc.stop_processor()
    #     elif s == 'ir':
    #         job8 = JobGenerator.generate_job(TURN_RIGHT,1)
    #         proc.insert_new_job(job8)


if __name__ == '__main__':
    main()