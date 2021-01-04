import functools

import simpy
from ResourceModule.DSP import *
from ResourceModule.MEM import *
from queue import Queue
from ResourceModule import ResourcesManager as RM 
import random
from TaskModule.Scheduler import SchduleAlgorithm
from TaskModule import Scheduler as scheduler

#貌似没啥用
def cmpTask(t1, t2):
    # 大到小
    return t1.dspPriority - t2.dspPriority

def QosPreemption(t1, t2):
    # p1 = (a * t1.graphCost + b * t1.graphPriority)/(t1.graphDDL - TaskManager.env.now + 0.001)
    # p2 = (a * t2.graphCost + b * t2.graphPriority) / (t2.graphDDL - TaskManager.env.now + 0.001)
    if scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionG.value:
        # print("QOSPreemptionG")
        p1 = (t1.graphCost + t1.graphPriority) / (t1.graphDDL - Cluster.env.now + 0.001)
        p2 = (t2.graphCost + t2.graphPriority) / (t2.graphDDL - Cluster.env.now + 0.001)
        return p2 - p1
    elif scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionT.value:
        if t1.graphDDL != t2.graphDDL:
            return t1.graphDDL - t2.graphDDL
        else:
            return t2.cost - t1.cost
    elif scheduler.getAlgorithm().value == SchduleAlgorithm.QOSReserve.value:
        # print("算法：%d；实际：%d"%(scheduler.getAlgorithm().value,SchduleAlgorithm.QOSPreemptionT.value))
        p1 = (t1.graphCost + t1.graphPriority) / (t1.graphDDL - Cluster.env.now + 0.001)
        p2 = (t2.graphCost + t2.graphPriority) / (t2.graphDDL - Cluster.env.now + 0.001)
        return p2 - p1
    else:
        # print("????????????????????")
        return -1

class Cluster:
    env = None

    def __init__(self, env, clusterId, dmaControl):
        self.dspList = []

        self.taskList = []
        self.curCost = 0
        self.preemptionCnt = 0
        self.sortNum = 1

        self.memoryList = []
        self.setMemory(1, clusterId)

        self.offChipAccess = 0

        self.clusterId = clusterId

        if Cluster.env == None:
            Cluster.env = env
        self.dmaControl = dmaControl
        if clusterId >= 0:
            self.setDsp(env, 4, clusterId)
        else:
            self.setFHAC(env, clusterId)

    def setQosDma(self, flag, QosClusterNum):
        # if flag:
        #     self.dmaControl = simpy.Resource(self.env, capacity=QosClusterNum)
        # else:
        #     self.dmaControl = simpy.Resource(self.env, capacity=len(RM.getClusterList()) - QosClusterNum)
        tmp = 1

    def finishQosDma(self):
        # self.dmaControl = simpy.Resource(self.env, capacity=len(RM.getClusterList()))
        tmp = 1

    
    def submit(self, task):
        # if dmaTask not in self.taskList:
        self.taskList.append(task)
        for data in task.dataInsIn:
            self.curCost += data.total_size
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if self.clusterId >= 0:
            self.preemptionCnt += 1
            if self.preemptionCnt == self.sortNum:
                self.preemptionCnt = 0
                self.taskList = sorted(self.taskList, key=functools.cmp_to_key(QosPreemption))
        return True
    
    def setDsp(self, env, num, clusterId):
        for i in range(0,num):
            self.dspList.append(DSP(env, clusterId, 'DSP', self.dmaControl))

    def setFHAC(self, env, clusterId):
        self.dspList.append(DSP(env, clusterId, 'FHAC', self.dmaControl))

    def getDspList(self):
        return self.dspList

    def getDsp(self,index):
        return self.dspList[index]

    def setMemory(self, num, clusterId):
        for i in range(0,num):
            self.memoryList.append(MEM(clusterId))

    def getMemory(self,index):
        return self.memoryList[index]

    def run(self):
        while(True):
            while len(self.taskList) > 0:
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
                        # print("=====debug from Shine: not in the inner memory, using dma to find=====")
                        self.offChipAccess += data.total_size
                        with self.dmaControl.request() as req:  # 寻求进入
                            yield req
                            transmitTimeToYield = 0
                            gotData,accessTime,transmitTime = RM.dmaGetData(data)
                            """remember to add this to REPORTER"""
                            transmitTimeToYield += transmitTime
                            saveToDdrTime = RM.getMemory(self).saveData(gotData, True)
                            transmitTimeToYield += saveToDdrTime
                            yield self.env.timeout(transmitTimeToYield)

                mallocSize = 0
                for data in task.getDataInsOut():
                    mallocSize += data.total_size
                transmitTimeToYield = RM.getMemory(self).malloc(mallocSize)
                yield self.env.timeout(transmitTimeToYield)

                dspList = RM.getCluster(self.clusterId).getDspList()
                dsp = dspList[0]
                if self.clusterId >= 0:
                    for d in dspList:
                        if d.curCost < dsp.curCost:
                            dsp = d
                    dspId = dsp.id % 4
                else:
                    dspId = 0
                RM.submitTaskToDsp(task, self.clusterId, dspId)
                # while not RM.submitTaskToDsp(task, self.clusterId, dspId):
                #     yield self.env.timeout(0.001)

            # yield self.env.timeout(0.0002)
            yield self.env.timeout(0.002)
