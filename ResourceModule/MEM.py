from ResourceModule.DMA import *
from ResourceModule.DSP import *
from ResourceModule import ResourcesManager as RM
from collections import OrderedDict


class MEM:

    def __init__(self, clusterId):
        # key is dataName
        self.map = OrderedDict()
        self.speed = 1

        self.capacity = 100000
        self.curSize = 0
        self.peek = 0

        self.clusterId = clusterId

    def saveData(self, data):
        # can mem save data
        if data.dataName in self.map.keys():
            self.map.pop(data.dataName)
            self.map[data.dataName] = data
        elif self.checkMem(data):
            self.map[data.dataName] = data
            self.curSize += data.total_size
        else:
            while self.curSize + data.total_size > self.capacity:
                tmp = self.map.popitem(last=False)[1]
                self.curSize -= tmp.total_size
                # print("******************************%d"%tmp.total_size)
            self.map[data.dataName] = data
            self.curSize += data.total_size

        self.peek = max(self.curSize,self.peek)

        # save data
        # print ("memory save %s" % data.dataName)

    # get data
    def getData(self, env, data, dsp):
        if not data.dataName in self.map.keys():
            RM.submitDmaTask(env, data, self)
        # else:
        #     print("data is in the mem =================")

        transformTime = data.total_size / self.speed
        # yield env.timeout(transformTime)
        # print ("get data in mem")


    def checkData(self,data):
        # check if date is in this mem
        # print("check " + data.dataName)
        # print(data.dataName in self.map.keys())
        if data.dataName in self.map.keys():
            return True
        else:
            # print("false %d" % self.curSize)
            return False

    def checkMem(self,data):
        # can mem save data
        if self.curSize + data.total_size >= self.capacity:
            return False
        else:
            return True