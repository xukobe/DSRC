__author__ = 'xuepeng'

import Queue
import time

from threading import Condition, Thread


class job:
    """
    The class is used to send a single command to iRobot
    """
    def __init__(self, action, time):
        self.action = action
        self.time = time

    def execute(self):
        print self.action
        pass

    def getTime(self):
        return self.time


class jobGenerator:
    """
    The class is to generate a new job
    """
    def __init__(self):
        pass

    @staticmethod
    def generateJob(action, time):
        return job(action, time)


class processor(Thread):
    """
    Processor has a queue, which contain a list of jobs. These jobs will be executed one by one
    The pause and resume functionalities are implemented
    """
    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue.Queue()
        self.pause = True
        self.flowCondition = Condition()
        self.jobCondition = Condition()
        self.currentJob = None
        self.currentJobStartTime = 0
        self.currentJobEndTime = 0
        self.nextJob = True
        self.timeLeft = 0
        self.running = True

    def addNewJob(self, job):
        """
        add new job to processor
        :param job: The job to add
        :return:
        """
        self.queue.put(job)

    def getNumberOfJobs(self):
        """
        :return: The size of current queue
        """
        return self.queue.qsize()

    def run(self):
        while self.running:
            self.flowCondition.acquire()
            while self.pause:
                self.flowCondition.wait()
            self.flowCondition.release()

            self.jobCondition.acquire()
            if self.nextJob:
                if self.queue.empty():
                    self.jobCondition.release()
                    self.pause = True
                    continue
                else:
                    print "Strat new job"
                    self.currentJob = self.queue.get()
                    self.timeLeft = self.currentJob.getTime()
            self.currentJob.execute()
            self.currentJobStartTime = time.time()
            self.jobCondition.wait(self.timeLeft)
            self.currentJobEndTime = time.time()
            self.timeLeft = self.timeLeft - (self.currentJobEndTime - self.currentJobStartTime)
            print "Time spent:" + str(self.currentJobEndTime - self.currentJobStartTime)
            print "Job stopped, time left:" + str(self.timeLeft)
            if self.timeLeft <= 0:
                self.nextJob = True
            else:
                self.nextJob = False
            self.jobCondition.release()

    def pause_processor(self):
        """
        Pause the current processor and save the current state
        """
        self.pause = True
        self.jobCondition.acquire()
        self.jobCondition.notifyAll()
        self.jobCondition.release()
        # Generate a pause job and execute
        job = jobGenerator.generateJob('pause',0)
        job.execute()

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
    job1 = jobGenerator.generateJob("forward", 3)
    job2 = jobGenerator.generateJob("turn left",1)
    job3 = jobGenerator.generateJob("fast forward", 3)
    job4 = jobGenerator.generateJob("Pause",0)
    job5 = jobGenerator.generateJob("Backward",4)
    job6 = jobGenerator.generateJob("Stop",0)
    proc = processor()
    proc.addNewJob(job1)
    proc.addNewJob(job2)
    proc.addNewJob(job3)
    proc.addNewJob(job4)
    proc.addNewJob(job5)
    proc.addNewJob(job6)
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

if __name__ == '__main__':
    main()