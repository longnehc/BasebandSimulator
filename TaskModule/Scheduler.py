from TaskModule.TaskGraph import * 
from TaskModule.Task import *
from TaskModule.DataInstance import *
from ResourceModule import ResourcesManager as RM
from queue import Queue

import random

from BasebandSimulator.TaskModule.Task import TaskStatus


class SchduleAlgorithm(Enum):
    RANDOM = 0 
    GREEDY = 1
    OFFMEM = 2
    QOS = 3
    LB = 4

class Scheduler:

    def __init__(self):
        self.taskQueue = Queue()
        self.algorithm = SchduleAlgorithm.RANDOM
    
scheduler = Scheduler()
    
def setAlgorithm(algorthim):
    scheduler.algorithm = algorthim

def submit(task):
    scheduler.taskQueue.put(task)
    
cnt = 0
def run(env):
    global cnt
    while True:
        while not scheduler.taskQueue.empty():
            task = scheduler.taskQueue.get()
            if scheduler.algorithm == SchduleAlgorithm.RANDOM:
                print("RANDOM...")
            elif scheduler.algorithm == SchduleAlgorithm.GREEDY:
                print("Greedy...")
            elif scheduler.algorithm == SchduleAlgorithm.OFFMEM:
                # print("Minimizing off-chip memory access...")
                RM.submitTaskToDma(task, task.clusterId, 0)
            elif scheduler.algorithm == SchduleAlgorithm.QOS:
                print("QoS guarantee...")
            elif scheduler.algorithm == SchduleAlgorithm.LB:
                # print("Load balancing...")
                cnt = (cnt + 1) % 16
                if not RM.submitTaskToDma(task, cnt, 0):
                    tmp = (cnt + 1) % 16
                    while not RM.submitTaskToDma(task, tmp, 0):
                        tmp = (tmp + 1) % 16
                        if tmp == cnt:
                            # print("full")
                            yield env.timeout(0.00001)
            else:
                print("Not implemented")

            # if task.taskStatus != TaskStatus.SUMBITTED:
            #     yield env.timeout(0.002)
        yield env.timeout(0.0002)

