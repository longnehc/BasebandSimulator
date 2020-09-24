from TaskModule.Task import TaskStatus
from resources import dma
from resources import memory
from queue import Queue
import resources.ResourcesManager as RM
from resources.dma import *
from resources.DMATask import *


class DSP:
    num = 0
    def __init__(self, env, clusterId):
        self.id = DSP.num
        DSP.num += 1
        self.taskQueue = Queue()
        self.speed = 1.3 * 1000000000
        self.clusterId = clusterId
        self.env = env

        self.totalCost = 0
        self.curCost = 0

    def submit(self, task):
        # print ("*************** %s"%self)
        self.taskQueue.put(task)

        # for report
        self.curCost += task.cost
        self.totalCost += task.cost
        # print("%d || %d" % (self.curCost, self.totalCost))

    def takeDataToMem(self,task):
        # print(task.taskName + "===========================%d" % len(task.getDataInsIn()))
        # get memory
        for data in task.getDataInsIn():
            if not RM.checkData(self, data):
                # submit to dma
                dma = RM.getDma(self)
                dma.submit(DmaTask(data))
                # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")



    def run(self):
        while(True):
            while not self.taskQueue.empty():
                task = self.taskQueue.get()

                # print(task.taskName + " begin in %s"% self.id)

                self.takeDataToMem(task)
                while True:
                    flag = True
                    for data in task.getDataInsIn():
                        if not RM.checkData(self, data):
                            print("%s not found %s" %(task.taskName, data.dataName) )
                            flag = False
                            break
                    if not flag:
                        # print("wait")
                        # wait for dma

                        # 0.001ms ->0.002s
                        yield self.env.timeout(0.002)
                    else:
                        # print("dma finish########################")
                        break

                # transmit data
                for data in task.getDataInsIn():
                    transmitTime = 2000 * data.total_size / RM.getTransmitSpeed(self)
                    yield self.env.timeout(transmitTime)

                # exe
                yield self.env.timeout(2000 * task.cost/self.speed)
                # print("exe task %d" % task.cost)

                # write back
                for data in task.getDataInsOut():
                    time = RM.getMemory(self).saveData(data)
                    # print("dsp save %s" % data.data_inst_idx)
                    transmitTime = 2000 * data.total_size / RM.getTransmitSpeed(self)
                    yield self.env.timeout(transmitTime)


                # finish task
                task.taskStatus = TaskStatus.FINISH
                self.curCost -= task.cost
                # print(task.taskName + " finish in: %f" % self.env.now)

            yield self.env.timeout(0.002)
            # memory.get_data(task.data) time_out1
            # exe task (TIME_OUT) time_out2
            # memory.save(task.data) time_out3
            #isfinsih
            #while(true)
            # Q.pop()
            # memory.getData(1)
            # exe_task (1)
            # memory.save(1)