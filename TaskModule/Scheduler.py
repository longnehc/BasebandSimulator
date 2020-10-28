from TaskModule.TaskGraph import * 
from TaskModule.Task import *
from TaskModule.DataInstance import *
from ResourceModule import ResourcesManager as RM
from queue import Queue

import random

from TaskModule.Task import TaskStatus


class SchduleAlgorithm(Enum):
    RANDOM = 0 
    GREEDY = 1
    OFFMEM = 2
    QOSPreemptionG = 3
    QOSPreemptionT = 4
    LB = 5
    QOSReserve = 6

class Scheduler:

    def __init__(self):
        self.taskQueue = Queue()
        self.algorithm = SchduleAlgorithm.RANDOM

        self.QosReserveDdl = 0
        self.QosReserveClusterNum = 0
        self.QosReserveGraphId = []
        self.QosGraphNum = 0
    
scheduler = Scheduler()
    
def setAlgorithm(algorithm):
    scheduler.algorithm = algorithm

def submit(task):
    scheduler.taskQueue.put(task)

def getAlgorithm():
    return scheduler.algorithm

def beginQosReserve(graphId, QosReserveDdl, QosReserveClusterNum):
    scheduler.algorithm = SchduleAlgorithm.QOSReserve
    scheduler.QosReserveDdl = QosReserveDdl
    scheduler.QosReserveClusterNum = QosReserveClusterNum
    scheduler.QosReserveGraphId = graphId
    RM.clearCluster(0, QosReserveClusterNum-1)
    scheduler.QosGraphNum = len(graphId)


def qosReserveFinish():
    scheduler.QosGraphNum -= 1
    if scheduler.QosGraphNum == 0:
        scheduler.algorithm = SchduleAlgorithm.QOSPreemptionG
        print("reverse finish")
    
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
                while not RM.submitTaskToDma(task, task.clusterId, 0):
                    yield env.timeout(0.0001)

            # TODO:
            elif scheduler.algorithm == SchduleAlgorithm.QOSPreemptionG or scheduler.algorithm == SchduleAlgorithm.QOSPreemptionT:
                clusterId = 0
                curCost = 10000000.0
                clusterList = RM.getClusterList()
                for i in range(0, len(clusterList)):
                    # 11111
                    tmp = 0.0
                    for dsp in clusterList[i].getDspList():
                        # tmp += dsp.taskQueue.qsize()
                        tmp += dsp.curCost / dsp.speed
                    for dma in clusterList[i].getDmaList():
                        # tmp += len(dma.taskList)
                        tmp += dma.curCost / dma.speed
                    if tmp < curCost:
                        clusterId = i
                        curCost = tmp
                    # submit
                while not RM.submitTaskToDma(task, clusterId, 0):
                    yield env.timeout(0.001)
                # ---
                # cnt = (cnt + 1) % 16
                # if not RM.submitTaskToDma(task, cnt, 0):
                #     tmp = (cnt + 1) % 16
                #     while not RM.submitTaskToDma(task, tmp, 0):
                #         tmp = (tmp + 1) % 16
                #         if tmp == cnt:
                #             # print("full")
                #             yield env.timeout(0.001)

            elif scheduler.algorithm == SchduleAlgorithm.LB:
                # print("Load balancing...")
                # cnt = (cnt + 1) % 16
                # if not RM.submitTaskToDma(task, cnt, 0):
                #     tmp = (cnt + 1) % 16
                #     while not RM.submitTaskToDma(task, tmp, 0):
                #         tmp = (tmp + 1) % 16
                #         if tmp == cnt:
                #             # print("full")
                #             yield env.timeout(0.001)
                # new LB
                clusterId = 0
                curCost = 10000000.0
                clusterList = RM.getClusterList()
                for i in range(0, len(clusterList)):
                    # 11111
                    tmp = 0.0
                    for dsp in clusterList[i].getDspList():
                        # tmp += dsp.taskQueue.qsize()
                        tmp += dsp.curCost / dsp.speed
                    for dma in clusterList[i].getDmaList():
                        # tmp += len(dma.taskList)
                        tmp += dma.curCost / dma.speed
                    if tmp < curCost:
                        clusterId = i
                        curCost = tmp
                    # submit
                while not RM.submitTaskToDma(task, clusterId, 0):
                    yield env.timeout(0.001)

            # TODO:
            elif scheduler.algorithm == SchduleAlgorithm.QOSReserve:
                clusterList = RM.getClusterList()
                if task.taskGraphId in scheduler.QosReserveGraphId:
                    # print("graph %d quick"%task.taskGraphId)
                    clusterId = 0
                    curCost = 10000000.0
                    for i in range(0, scheduler.QosReserveClusterNum):
                        # 11111
                        tmp = 0.0
                        for dsp in clusterList[i].getDspList():
                            # tmp += dsp.taskQueue.qsize()
                            tmp += dsp.curCost / dsp.speed
                        for dma in clusterList[i].getDmaList():
                            # tmp += len(dma.taskList)
                            tmp += dma.curCost / dma.speed
                        if tmp < curCost:
                            clusterId = i
                            curCost = tmp
                        # 22222
                        # if len(clusterList[i].getDma(0).taskList) < len(clusterList[clusterId].getDma(0).taskList):
                        #     clusterId = i
                        # submit
                    # print(clusterId)
                    while not RM.submitTaskToDma(task, clusterId, 0):
                        yield env.timeout(0.001)
                else:
                    clusterId = scheduler.QosReserveClusterNum
                    for i in range(scheduler.QosReserveClusterNum, len(clusterList)):
                        if len(clusterList[i].dmaList[0].taskList) < len(clusterList[clusterId].dmaList[0].taskList):
                            clusterId = i
                        # submit
                    while not RM.submitTaskToDma(task, clusterId, 0):
                        yield env.timeout(0.001)
                if env.now > scheduler.QosReserveDdl:
                    scheduler.algorithm = SchduleAlgorithm.QOSPreemptionG
                    print("reverse finish")

            else:
                print("Not implemented")

            # if task.taskStatus != TaskStatus.SUMBITTED:
            #     yield env.timeout(0.002)
        yield env.timeout(0.0002)

