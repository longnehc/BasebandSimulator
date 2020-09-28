from ResourceModule.DSP import *
from queue import Queue
from ResourceModule import ResourcesManager as RM
from ResourceModule.DMATask import *
import random




class DMA:
    def __init__(self, env, clusterId):
        self.id = 0
        self.speed = 256 * 866 * 1000000
        self.taskList = []
        self.env = env
        self.clusterId = clusterId



    def submit(self, task):
        # if dmaTask not in self.taskList:
        self.taskList.append(task)
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

                for data in task.getDataInsIn():
                    if not RM.checkData(self, data):
                        transmitTime = 2000 * data.total_size / self.speed
                        yield self.env.timeout(transmitTime)
                        # print("dma save " + data.dataName)
                        RM.getMemory(self).saveData(data)

                RM.submitTaskToDsp(task, self.clusterId, random.randint(0, 3))

            yield self.env.timeout(0.0002)