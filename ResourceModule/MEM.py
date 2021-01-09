from ResourceModule.DSP import *
from ResourceModule import ResourcesManager as RM
from collections import OrderedDict

import sys


class MEM:

    def __init__(self, clusterId):
        # key is dataName
        self.map = OrderedDict()
        #key:(data,isProducer,waitForVisit)

        #self.capacity = 1000000
        self.capacity = 1000000 * 10
        if clusterId < 0:
            self.capacity = sys.maxsize
        self.curSize = 0
        self.outSize = 0
        self.peek = 0

        self.dataBuffer = 0

        self.clusterId = clusterId

    def clusterSaveData(self, data):
        transmitTime = 0
        # can mem save data
        # print("%s-%d" % (data.dataName, data.data_inst_idx))
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            print("=====debug from Shine: already have this data in MEM!=====")
            return 0
        elif self.checkMem(data):
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = [data,False,0]
            self.curSize += data.total_size
            self.peek = max(self.curSize,self.peek)
            return 0
        else:
            key_list = list(self.map.keys())
            for key in key_list:
                if self.curSize + data.total_size <= self.capacity:
                    self.map[data.dataName + "-" + str(data.data_inst_idx)] = [data,False,0]
                    self.curSize += data.total_size
                    self.peek = max(self.curSize,self.peek)
                    return transmitTime
                tmpWaitForVisit = self.map[key][2]
                isProducer = self.map[key][1]
                if tmpWaitForVisit <= 0:
                    tmp = self.map[key][0]
                    self.curSize -= tmp.total_size
                    self.outSize += tmp.total_size
                    if tmp.remain_time < 0:
                        print("=====memory error: save data not valid!=====")
                    if tmp.remain_time != 0 and isProducer:
                        transmitTime += RM.dmaSaveData(tmp)
                    del self.map[key]
            if self.curSize + data.total_size > self.capacity:
                print("=====memory error: Insufficient memory space recommended to increase memory===========")

    # get data
    def getData(self, data):
        isProducer = False
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            validData = self.map[data.dataName + "-" + str(data.data_inst_idx)][0]
            isProducer = self.map[data.dataName + "-" + str(data.data_inst_idx)][1]
            self.map[data.dataName + "-" + str(data.data_inst_idx)][2] -= 1
            return validData, True, isProducer
        else:
            return data, False, isProducer

    def delData(self, data):
        data_key = data.dataName + "-" + str(data.data_inst_idx)
        if data_key in self.map.keys():
            tmp = self.map[data_key]
            if tmp[2]==0:
                del self.map[data_key]
                self.curSize -= data.total_size


    def checkData(self, data):
        # check if date is in this mem
        # print("check " + data.dataName)
        # print(data.dataName in self.map.keys())
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            return True
        else:
            # print("false %d" % self.curSize)
            return False
    
    def setVisit(self, data):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            self.map[data.dataName + "-" + str(data.data_inst_idx)][2] += 1

    def checkVisit(self, data):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            return self.map[data.dataName + "-" + str(data.data_inst_idx)][2]
        else:
            return 0

    def checkMem(self,data):
        # can mem save data
        if self.curSize + data.total_size >= self.capacity:
            return False
        else:
            return True

    def malloc(self, dataSize):
        transmitTime = 0
        if self.curSize + dataSize <= self.capacity:
            self.curSize += dataSize
            return transmitTime
        key_list = list(self.map.keys())
        for key in key_list:
            if self.curSize + dataSize <= self.capacity:
                self.curSize += dataSize
                return transmitTime
            waitForVisit = self.map[key][2]
            if waitForVisit <= 0:
                tmp = self.map[key][0]
                self.curSize -= tmp.total_size
                self.outSize += tmp.total_size
                del self.map[key]
                if tmp.remain_time < 0:
                    print("=====memory error: save data not valid!=====")
                if tmp.remain_time != 0:
                    transmitTime += RM.dmaSaveData(tmp)
        if self.curSize + dataSize > self.capacity:
            print("=====memory error: clusterId",self.clusterId)
            print("Insufficient memory space recommended to increase memory===========")

    def dspSave(self, data):
        if data.remain_time == 0:
            self.curSize -= data.total_size
        else:
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = [data, True, 0]
        self.peek = max(self.curSize, self.peek)

