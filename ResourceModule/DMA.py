import functools

from ResourceModule.DSP import *
from queue import Queue
from ResourceModule import ResourcesManager as RM 
import random

from TaskModule.Scheduler import SchduleAlgorithm
from TaskModule import Scheduler as scheduler

class DMA:
    totalBus = None
    def __init__(self, clusterId, totalBus):
        self.speed = 256 * 866 * 1000000
        self.env = env
        self.clusterId = clusterId
        self.offChipAccess = 0

        if DMA.totalBus == None:
            DMA.totalBus = totalBus

    def getData(self, data):
        accessTime = 0
        find = False
        """
        find from other cluster or DDR
        """
        for cluster in self.totalBus.clusterList:
            Mem = cluster.memoryList[0]
            accessTime += 1
            if data.dataName + "-" + str(data.data_inst_idx) in Mem.map.keys():
                find = True
                break
        #find in DDR
        if not find:
            accessTime += 1
            DDR = self.totalBus.getDDR()
            if data.dataName + "-" + str(data.data_inst_idx) in DDR.map.keys():
                find = True
            else:
                print("not in DDR!!!!!!!!!!!!")
                self.saveData(data)
        totalBus.getCluster(clusterId).memoryList[0].saveData()
        return accessTime

    def saveData(self, data):
        DDR = self.totalBus.getDDR()
        DDR.map[data.dataName + "-" + str(data.data_inst_idx)] = data

    def submitWriteTask(self, data):
        self.writeTaskList.append(data)

    def writeBackWorker(self):    
        while(True):
            while len(self.writeTaskList) > 0:
                data = self.writeTaskList.pop(0)
                transmitTime = 2000 * data.total_size / self.writeBackSpeed
                yield self.env.timeout(transmitTime)
            yield self.env.timeout(0.002)