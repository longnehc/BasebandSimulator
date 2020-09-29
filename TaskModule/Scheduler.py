from TaskModule.TaskGraph import * 
from TaskModule.Task import *
from TaskModule.DataInstance import *
from ResourceModule import ResourcesManager as RM
from queue import Queue


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
    

def run(env):
    while True:
        while not scheduler.taskQueue.empty():
            if scheduler.algorithm == SchduleAlgorithm.RANDOM:
                print("RANDOM...")
            elif scheduler.algorithm == SchduleAlgorithm.GREEDY:
                print("Greedy...")
            elif scheduler.algorithm == SchduleAlgorithm.OFFMEM:
                print("Minimizing off-chip memory access...")
            elif scheduler.algorithm == SchduleAlgorithm.QOS:
                print("QoS guarantee...")
            elif scheduler.algorithm == SchduleAlgorithm.LB:
                print("Load balancing...")
            else:
                print("Not implemented")
            yield env.timeout(1)

