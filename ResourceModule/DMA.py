import functools

from ResourceModule.DSP import *
from queue import Queue
from ResourceModule import ResourcesManager as RM 
import random

from BasebandSimulator.TaskModule.Scheduler import SchduleAlgorithm
from TaskModule import Scheduler as scheduler

def cmpTask(t1, t2):
    # 大到小
    return t1.dspPriority - t2.dspPriority

def QosPreemption(t1, t2):
    # p1 = (a * t1.graphCost + b * t1.graphPriority)/(t1.graphDDL - TaskManager.env.now + 0.001)
    # p2 = (a * t2.graphCost + b * t2.graphPriority) / (t2.graphDDL - TaskManager.env.now + 0.001)
    if scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionG.value:
        # print("QOSPreemptionG")
        p1 = (t1.graphCost + t1.graphPriority) / (t1.graphDDL - DMA.env.now + 0.001)
        p2 = (t2.graphCost + t2.graphPriority) / (t2.graphDDL - DMA.env.now + 0.001)
        return p2 - p1
    elif scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionT.value:
        if t1.graphDDL != t2.graphDDL:
            return t1.graphDDL - t2.graphDDL
        else:
            return t2.cost - t1.cost
    elif scheduler.getAlgorithm().value == SchduleAlgorithm.QOSReserve.value:
        # print("算法：%d；实际：%d"%(scheduler.getAlgorithm().value,SchduleAlgorithm.QOSPreemptionT.value))
        p1 = (t1.graphCost + t1.graphPriority) / (t1.graphDDL - DMA.env.now + 0.001)
        p2 = (t2.graphCost + t2.graphPriority) / (t2.graphDDL - DMA.env.now + 0.001)
        return p2 - p1
    else:
        # print("????????????????????")
        return -1

class DMA:
    env = None
    def __init__(self, env, clusterId):
        self.id = 0
        self.speed = 256 * 866 * 1000000
        self.taskList = []
        self.env = env
        self.clusterId = clusterId
        self.capacity = 10000
        self.offChipAccess = 0

        self.a = 0.000001
        self.b = 10

        self.curCost = 0

        self.preemptionCnt = 0
        self.sortNum = 1
        if DMA.env == None:
            DMA.env = env



    def submit(self, task):
        # if dmaTask not in self.taskList:
        self.taskList.append(task)
        for data in task.dataInsIn:
            self.curCost += data.total_size
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        self.preemptionCnt += 1
        if self.preemptionCnt == self.sortNum:
            self.preemptionCnt = 0
            self.taskList = sorted(self.taskList, key=functools.cmp_to_key(QosPreemption))
            # if 0.08 > self.env.now > 0.06:
            #     for i in range(0, len(self.taskList)):
            #         print(self.taskList[i].taskGraphId, end=" ")
            #     print("dma")


    def run(self):
        while(True):
            while len(self.taskList) > 0:
                # dmaTask = self.taskList.pop(0)
                #
                # transmitTime = 2000 * dmaTask.data.total_size / self.speed
                # yield self.env.timeout(transmitTime)
                #
                # # print("dma save " + dmaTask.data.dataName)
                # RM.getMemory(self).saveData(dmaTask.getData())

                task = self.taskList.pop(0)
                if len(RM.getTaskExeMap()) < task.batchId:
                    RM.getTaskExeMap().append({})
                if task.taskName not in RM.getTaskExeMap()[task.batchId-1]:
                    RM.getTaskExeMap()[task.batchId - 1][task.taskName] = {}
                # RM.getTaskExeMap()[task.batchId - 1][task.taskName][task.job_inst_idx][0] is the begin time and [1] is the finish time
                RM.getTaskExeMap()[task.batchId - 1][task.taskName][task.job_inst_idx] = [self.env.now]

                if task.taskName not in RM.getTaskLogMap():
                    RM.getTaskLogMap()[task.taskName] = {}
                if task.job_inst_idx in RM.getTaskLogMap()[task.taskName]:
                    RM.getTaskLogMap()[task.taskName][task.job_inst_idx].append(self.env.now)
                else:
                    RM.getTaskLogMap()[task.taskName][task.job_inst_idx] = [self.env.now]

                for data in task.getDataInsIn():
                    self.curCost -= data.total_size
                    if not RM.getMemory(self).checkData(data):
                        transmitTime = 2000 * data.total_size / self.speed
                        self.offChipAccess += data.total_size
                        yield self.env.timeout(transmitTime)
                        # print("dma save " + data.dataName)
                        RM.getMemory(self).saveData(data)

                # if task.dspId == -1:
                #     dspList = RM.getCluster(self.clusterId).getDspList()
                #     for t in self.taskList:
                #         t.dspPriority = (self.a * t.graphCost + self.b * t.graphPriority)/(t.graphDDL - self.env.now + 0.001)
                #     # assign dsp
                #     tmpTaskList = sorted(self.taskList, key=functools.cmp_to_key(cmpTask))
                #     for t in tmpTaskList:
                #         dsp = dspList[0]
                #         for d in dspList:
                #             if d.curCost < dsp.curCost:
                #                 dsp = d
                #         t.dspId = dsp.id % 4
                # RM.submitTaskToDsp(task, self.clusterId, task.dspId)

                dspList = RM.getCluster(self.clusterId).getDspList()
                dsp = dspList[0]
                for d in dspList:
                    if d.curCost < dsp.curCost:
                        dsp = d
                dspId = dsp.id % 4
                RM.submitTaskToDsp(task, self.clusterId, dspId)
                # while not RM.submitTaskToDsp(task, self.clusterId, dspId):
                #     yield self.env.timeout(0.001)

            # yield self.env.timeout(0.0002)
            yield self.env.timeout(0.002)