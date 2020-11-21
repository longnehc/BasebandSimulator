import functools
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

    def __init__(self, env, clusterId):
        self.dspList = []
        self.setDsp(env, 4, clusterId)
        self.FHACList = []
        self.setFHAC(env, 1, clusterId)

        self.taskList = []
        self.curCost = 0
        self.preemptionCnt = 0
        self.sortNum = 1

        self.memoryList = []
        self.setMemory(1, clusterId)

        self.dmaList = []
        self.offChipAccess = 0

        self.clusterId = clusterId

        self.speed = 256 * 866 * 1000000
        """speed is 256 * 866 * 1000000"""

        if Cluster.env == None:
            Cluster.env = env
    
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
        return True
    
    def setDsp(self, env, num, clusterId):
        for i in range(0,num):
            self.dspList.append(DSP(env, clusterId, 'DSP'))

    def setFHAC(self, env, num, clusterId):
        for i in range(num):
            self.FHACList.append(DSP(env, clusterId, 'FHAC'))

    def getDspList(self):
        return self.dspList

    def getFHACList(self):
        return self.FHACList

    def getDsp(self,index):
        return self.dspList[index]

    def setMemory(self, num, clusterId):
        for i in range(0,num):
            self.memoryList.append(MEM(clusterId))

    def getMemory(self,index):
        return self.memoryList[index]

    def getDma(self,index):
        return self.dmaList[index]

    def getDmaList(self):
        return self.dmaList

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
                        #print("=====debug from Shine: not in the inner memory, using dma to find=====")
                        transmitTime = 2000 * data.total_size / self.speed
                        self.offChipAccess += data.total_size
                        gotData,accessTime = self.getDma(0).getData(data)
                        """remember to add this to REPORTER"""
                        findTime = 0.00001
                        #yield self.env.timeout(accessTime * findTime)
                        yield self.env.timeout(transmitTime)
                        RM.getMemory(self).saveData(gotData)

                if task.knrlType == "FHAC":
                    #print("=====debug from Shine: using FHAC to run task=====")
                    FHACList = RM.getCluster(self.clusterId).getFHACList()
                    FHAC = FHACList[0]
                    """
                    for f in FHACList:
                        if f.curCost < FHAC.curCost:
                            FHAC = f
                    """
                    """
                    need to change!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    """
                    RM.submitTaskToFHAC(task, self.clusterId)
                else:
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
