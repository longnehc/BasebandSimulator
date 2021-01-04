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
        self.capacity = 500000000
        if clusterId < 0:
            self.capacity = sys.maxsize
        self.curSize = 0
        self.outSize = 0
        self.peek = 0

        self.clusterId = clusterId

    def saveData(self, data, admission, isProducer):
        transmitTime = 0
        # can mem save data
        # print("%s-%d" % (data.dataName, data.data_inst_idx))
        waitForVisit = True
        if isProducer:
            waitForVisit = False
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            print("=====debug from Shine: already have this data in MEM!=====")
            return 0
        elif self.checkMem(data):
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = [data,isProducer,waitForVisit]
            self.curSize += data.total_size
            self.peek = max(self.curSize,self.peek)
            return 0
        else:
            if not admission:
                return -1
            else:
                while self.curSize + data.total_size > self.capacity:
                    tmp = self.map.popitem(last=False)[1][0]
                    self.curSize -= tmp.total_size
                    self.outSize += tmp.total_size
                    if tmp.remain_time < 0:
                        print("=====memory error: save data not valid!=====",tmp.dataName+'-'+str(tmp.data_inst_idx))
                    if tmp.remain_time != 0:
                        # print("Writing back to DDR %s-%d, move: %d" % (tmp.dataName, tmp.data_inst_idx, tmp.mov_dir))
                        transmitTime += RM.dmaSaveData(tmp)
                    # print("******************************%d"%tmp.total_size)
                self.map[data.dataName + "-" + str(data.data_inst_idx)] = [data,isProducer,waitForVisit]
                self.curSize += data.total_size
                self.peek = max(self.curSize,self.peek)
                return transmitTime

        # save data
        # print ("memory save %s" % data.dataName)

    # get data
    def getData(self, data):
        isProducer = False
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            validData = self.map[data.dataName + "-" + str(data.data_inst_idx)][0]
            isProducer = self.map[data.dataName + "-" + str(data.data_inst_idx)][1]
            return validData, True, isProducer
        else:
            return data, False, isProducer

    def delData(self, data):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            tmp = self.map.pop(data.dataName + "-" + str(data.data_inst_idx))
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
    
    def setVisit(self, data, waitForVisit):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            self.map[data.dataName + "-" + str(data.data_inst_idx)][2] = waitForVisit

    def checkMem(self,data):
        # can mem save data
        if self.curSize + data.total_size >= self.capacity:
            return False
        else:
            return True

    def squeeze(self):
        transmitTime = 0
        for key in self.map.keys():
            validData = self.map[key][0]
            isProducer = self.map[key][1]
            waitForVisit = self.map[key][2]
            if isProducer and not waitForVisit:
                transmitTime += RM.dmaSaveData(validData)
                self.curSize -= validData.total_size
        return transmitTime