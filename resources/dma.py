from resources import dsp
from queue import Queue
import resources.ResourcesManager as RM
import resources.DMATask




class Dma:
    def __init__(self, env):
        self.id = 0
        self.speed = 1
        self.taskList = []
        self.env = env
        self.clusterId = 0


    def submit(self, dmaTask):
        if dmaTask not in self.taskList:
            self.taskList.append(dmaTask)
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


    def run(self):
        while(True):
            while len(self.taskList) > 0:
                dmaTask = self.taskList.pop(0)

                # transmitTime = dmaTask.data.total_size / self.speed
                # yield self.env.timeout(transmitTime)
                yield self.env.timeout(1)
                print("dma save " + dmaTask.data.dataName)
                RM.getMemory(self).saveData(dmaTask.getData())


            yield self.env.timeout(1)