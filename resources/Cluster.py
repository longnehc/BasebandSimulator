from resources.dsp import DSP
from resources.memory import Memory
from resources.dma import *

class Cluster:

    def __init__(self, env):
        self.dspList = []
        self.setDsp(env, 4)

        self.memoryList = []
        self.setMemory(1)

        self.dmaList = []
        self.setDma(env,1)
    
    def setDsp(self, env, num):
        for i in range(0,num):
            self.dspList.append(DSP(env))

    def getDspList(self):
        return self.dspList

    def getDsp(self,index):
        return self.dspList[index]

    def setMemory(self,num):
        for i in range(0,num):
            self.memoryList.append(Memory())

    def getMemory(self,index):
        return self.memoryList[index]

    def setDma(self, env, num):
        for i in range(0,num):
            self.dmaList.append(Dma(env))

    def getDma(self,index):
        return self.dmaList[index]

    def getDmaList(self):
        return self.dmaList