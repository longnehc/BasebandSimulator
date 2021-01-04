import functools

import simpy
from TaskModule.Task import TaskStatus
from ResourceModule.MEM import *
from queue import Queue
from ResourceModule import ResourcesManager as RM
from TaskModule import Scheduler as scheduler

from TaskModule.Scheduler import SchduleAlgorithm


def QosPreemption(t1, t2):
    # p1 = (a * t1.graphCost + b * t1.graphPriority)/(t1.graphDDL - TaskManager.env.now + 0.001)
    # p2 = (a * t2.graphCost + b * t2.graphPriority) / (t2.graphDDL - TaskManager.env.now + 0.001)
    if scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionG.value:
        # print("QOSPreemptionG")
        p1 = (t1.graphCost + t1.graphPriority) / (t1.graphDDL - DSP.env.now + 0.001)
        p2 = (t2.graphCost + t2.graphPriority) / (t2.graphDDL - DSP.env.now + 0.001)
        return p2 - p1
    elif scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionT.value:
        if t1.graphDDL != t2.graphDDL:
            return t1.graphDDL - t2.graphDDL
        else:
            return t2.cost - t1.cost
    elif scheduler.getAlgorithm().value == SchduleAlgorithm.QOSReserve.value:
        # print("算法：%d；实际：%d"%(scheduler.getAlgorithm().value,SchduleAlgorithm.QOSPreemptionT.value))
        p1 = (t1.graphCost + t1.graphPriority) / (t1.graphDDL - DSP.env.now + 0.001)
        p2 = (t2.graphCost + t2.graphPriority) / (t2.graphDDL - DSP.env.now + 0.001)
        return p2 - p1
    else:
        # print("????????????????????")
        return -1


class DSP:
    num = 0
    env = None

    def __init__(self, env, clusterId, type, dmaControl):
        self.type = type
        """speed is 1.3 * 1000000000"""
        self.speed = 1.3 * 1000000000
        #type is "DSP" or "FHAC" ...
        if self.type == 'FHAC':
            self.speed *= 32
            self.id = -1
        else:
            self.id = DSP.num
            DSP.num += 1
        self.taskQueue = []
        self.clusterId = clusterId
        self.env = env

        self.totalCost = 0
        self.curCost = 0

        self.yieldTime = 0
        self.executionTime = 0
        self.dmaTransmitTime = 0
        self.capacity = 15

        self.preemptionCnt = 0
        self.sortNum = 1
        if DSP.env == None:
            DSP.env = env
        self.dmaControl = dmaControl

    def submit(self, task):
        self.taskQueue.append(task)

        # for report
        self.curCost += task.cost
        self.totalCost += task.cost
        # print("%d || %d" % (self.curCost, self.totalCost))
        if self.type == 'DSP':
            self.preemptionCnt += 1
            if self.preemptionCnt == self.sortNum:
                self.preemptionCnt = 0
                self.taskQueue = sorted(self.taskQueue, key=functools.cmp_to_key(QosPreemption))
                # if 0.08 > self.env.now > 0.06:
                #     for i in range(0, len(self.taskQueue)):
                #         print(self.taskQueue[i].taskGraphId, end=" ")
                #     print(self.taskQueue.pop(0).taskGraphId)
                #     print("dsp")

    def setQosDma(self, flag, QosClusterNum):
        # if flag:
        #     self.dmaControl = simpy.Resource(self.env, capacity=QosClusterNum)
        # else:
        #     self.dmaControl = simpy.Resource(self.env, capacity=len(RM.getClusterList()) - QosClusterNum)
        tmp = 1

    def finishQosDma(self):
        # self.dmaControl = simpy.Resource(self.env, capacity=len(RM.getClusterList()))
        tmp = 1

    def run(self, taskManager):
        while (True):
            while len(self.taskQueue) > 0:
                task = self.taskQueue.pop(0)
                
                if task.knrlType == "FHAC" and self.type == 'DSP':
                    print("error: find a FHAC task on DSP!!!!!!!")

                for data in task.dataInsIn:
                    gotData,flag = RM.getMemory(self).getData(data)
                    if not flag:
                        with self.dmaControl.request() as req:  # 寻求进入
                            yield req
                            gotData,accessTime,transmitTime = RM.dmaGetData(data)
                            """remember to add this to REPORTER"""
                            self.dmaTransmitTime += transmitTime
                            yield self.env.timeout(transmitTime)
                    gotData.remain_time -= 1
                    if gotData.remain_time == 0:
                        RM.delData(gotData)
                    if gotData.remain_time < 0:
                        print("memory error: get data not valid!",gotData.dataName)


                # exe
                yield self.env.timeout(2000 * task.cost / self.speed)  # TTI = 0.5ms
                self.executionTime += 2000 * task.cost / self.speed

                # write back
                '''
                for data in task.getDataInsOut():
                    saveFlag = RM.getMemory(self).saveData(data, False)
                    if saveFlag < 0:
                        with self.dmaControl.request() as req:  # 寻求进入
                            yield req
                            transmitTime = RM.getMemory(self).saveData(data, True)
                            self.dmaTransmitTime += transmitTime
                            yield self.env.timeout(transmitTime)
                '''
                for data in task.getDataInsOut():
                    RM.getMemory(self).dspSave(data)


                # finish task
                task.taskStatus = TaskStatus.FINISH
                self.curCost -= task.cost
                graph = taskManager.getGraph(task.batchId, task.taskGraphId)
                graph.taskNum -= 1
                if graph.taskNum == 0:
                    graph.finished = True
                    for data in task.getDataInsOut():
                        with self.dmaControl.request() as req:  # 寻求进入
                            yield req
                            transmitTime = RM.dmaSaveData(data)
                            self.dmaTransmitTime += transmitTime
                            yield self.env.timeout(transmitTime)

                    if graph.QosReserve:
                        scheduler.qosReserveFinish()
                        # print("//////////////////////////qosfinish by dsp")
                    print("graph %d of batch %d finish %f and cost %f" % (
                    graph.graphId, graph.batchId, self.env.now, self.env.now - graph.submitTime))
                    if graph.graphId in RM.getExecuteTimeMap():
                        RM.getExecuteTimeMap()[graph.graphId].append(self.env.now - graph.submitTime)
                        RM.getBeginTimeMap()[graph.graphId].append(graph.submitTime)
                        RM.getEndTimeMap()[graph.graphId].append(self.env.now)
                    else:
                        RM.setFinishGraphCnt(RM.getFinishGraphCnt() + 1)
                        print("getFinishGraphCnt: %d" % RM.getFinishGraphCnt())
                        RM.getExecuteTimeMap()[graph.graphId] = [self.env.now - graph.submitTime]
                        RM.getBeginTimeMap()[graph.graphId] = [graph.submitTime]
                        RM.getEndTimeMap()[graph.graphId] = [self.env.now]



                # if graph.taskNum < 0:
                #     print("graph %d task %d %s" % (graph.graphId,graph.taskNum,task.taskName))
                # print(task.taskName + " finish in: %f" % self.env.now)
                # print(task.graphDDL)

                RM.getTaskExeMap()[task.batchId - 1][task.taskName][task.job_inst_idx].append(self.env.now)
                RM.getTaskLogMap()[task.taskName][task.job_inst_idx].append(self.env.now)
            yield self.env.timeout(0.0002)