from ResourceModule.DSP import *
from queue import Queue
from ResourceModule import ResourcesManager as RM
from ResourceModule.DMATask import *




class DMA:
    def __init__(self, env, clusterId):
        self.id = 0
        self.speed = 256 * 866 * 1000000
        self.taskList = []
        self.env = env
        self.clusterId = clusterId



    def submit(self, dmaTask):
        if dmaTask not in self.taskList:
            self.taskList.append(dmaTask)
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


    def run(self):
        while(True):
            while len(self.taskList) > 0:
                dmaTask = self.taskList.pop(0)

                transmitTime = 2000 * dmaTask.data.total_size / self.speed
                yield self.env.timeout(transmitTime)

                # print("dma save " + dmaTask.data.dataName)
                RM.getMemory(self).saveData(dmaTask.getData())


            yield self.env.timeout(0.002)