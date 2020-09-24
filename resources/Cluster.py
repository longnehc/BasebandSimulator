from resources.dsp import DSP
from resources.memory import Memory
from resources.dma import *

class Cluster:

    def __init__(self, env, clusterId):
        self.dspList = []
        self.setDsp(env, 4, clusterId)

        self.memoryList = []
        self.setMemory(1, clusterId)

        self.dmaList = []
        self.setDma(env, 1, clusterId)

        self.clusterId = clusterId

        self.speed = 2 * 256 * 866 * 1000000
    
    def setDsp(self, env, num, clusterId):
        for i in range(0,num):
            self.dspList.append(DSP(env, clusterId))

    def getDspList(self):
        return self.dspList

    def getDsp(self,index):
        return self.dspList[index]

    def setMemory(self, num, clusterId):
        for i in range(0,num):
            self.memoryList.append(Memory(clusterId))

    def getMemory(self,index):
        return self.memoryList[index]

    def setDma(self, env, num, clusterId):
        for i in range(0,num):
            self.dmaList.append(Dma(env, clusterId))

    def getDma(self,index):
        return self.dmaList[index]

    def getDmaList(self):
        return self.dmaList