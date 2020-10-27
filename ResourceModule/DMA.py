import functools

from ResourceModule.DSP import *
from queue import Queue
from ResourceModule import ResourcesManager as RM 
import random

def cmpTask(t1, t2):
    # 大到小
    return t1.dspPriority - t2.dspPriority


class DMA:
    def __init__(self, env, clusterId):
        self.id = 0
        self.speed = 256 * 866 * 1000000
        self.taskList = []
        self.env = env
        self.clusterId = clusterId
        self.capacity = 100
        self.offChipAccess= 0

        self.a = 0.000001
        self.b = 10

        self.curCost = 0



    def submit(self, task):
        # if dmaTask not in self.taskList:
        self.taskList.append(task)
        for data in task.dataInsIn:
            self.curCost += data.total_size
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # print("dma begin")


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

            # yield self.env.timeout(0.0002)
            yield self.env.timeout(0.002)