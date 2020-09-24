from TaskModule.Task import TaskStatus
from resources import dma
from resources import memory
from queue import Queue
import resources.ResourcesManager as RM
from resources.dma import *
from resources.DMATask import *


class DSP:
    num = 0
    def __init__(self, env):
        self.id = DSP.num
        DSP.num += 1
        self.taskQueue = Queue()
        self.speed = 1
        self.clusterId = 0
        self.env = env

        self.finishGetData = env.event()
        self.finishExe = env.event()
        self.finishTransmit = env.event()

    def submit(self, task):
        # print ("*************** %s"%self)
        self.taskQueue.put(task)

    def takeDataToMem(self,task):
        # print(task.taskName + "===========================%d" % len(task.getDataInsIn()))
        # get memory
        for data in task.getDataInsIn():
            if not RM.checkData(self, data):
                # submit to dma
                dma = RM.getDma(self)
                dma.submit(DmaTask(data))
                # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        # yield self.env.timeout(1)



    def run(self):
        while(True):
            while not self.taskQueue.empty():
                # yield self.env.timeout(1)
                task = self.taskQueue.get()

                print(task.taskName + " begin in %s"% self.id)

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
                        yield self.env.timeout(1)
                    else:
                        # print("dma finish########################")
                        break

                # transmit data
                for data in task.getDataInsIn():
                    # yield self.env.timeout(data.total_size/memSpeed)
                    yield self.env.timeout(1)

                # exe
                # yield self.env.timeout(task.cost/self.speed)
                yield self.env.timeout(1)
                # print("exe task %d" % task.cost)

                # write back
                for data in task.getDataInsOut():
                    time = RM.getMemory(self).saveData(data)
                    print("dsp save %s" % data.data_inst_idx)
                    # yield self.env.timeout(time)
                    yield self.env.timeout(0.0001)
                    print(self.env.now)

                # finish task
                task.taskStatus = TaskStatus.FINISH
                print(task.taskName + " finish")

            yield self.env.timeout(1)
            # memory.get_data(task.data) time_out1
            # exe task (TIME_OUT) time_out2
            # memory.save(task.data) time_out3
            #isfinsih
            #while(true)
            # Q.pop()
            # memory.getData(1)
            # exe_task (1)
            # memory.save(1)