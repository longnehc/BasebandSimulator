from ResourceModule.DSP import *
from ResourceModule import ResourcesManager as RM
from collections import OrderedDict

import sys


class MEM:

    def __init__(self, clusterId):
        # key is dataName
        self.map = OrderedDict()

        #self.capacity = 1000000
        self.capacity = sys.maxsize
        if clusterId < 0:
            self.capacity = sys.maxsize
        self.curSize = 0
        self.peek = 0

        self.clusterId = clusterId

    def saveData(self, data, admission):
        transmitTime = 0
        # can mem save data
        # print("%s-%d" % (data.dataName, data.data_inst_idx))
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            # print("=====debug from Shine: already have this data in MEM!=====")
            # print("%s-%d" % (data.dataName, data.data_inst_idx))
            old = self.map[data.dataName + "-" + str(data.data_inst_idx)]
            if id(old)!=id(data):
                print("the old remain and new remain is: ",old.remain_time,data.remain_time)
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = old
            self.peek = max(self.curSize,self.peek)
            return 0
        elif self.checkMem(data):
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
            self.curSize += data.total_size
            self.peek = max(self.curSize,self.peek)
            return 0
        else:
            if not admission:
                return -1
            else:
                while self.curSize + data.total_size > self.capacity:
                    tmp = self.map.popitem(last=False)[1]
                    self.curSize -= tmp.total_size
                    if tmp.remain_time < 0:
                        print("=====memory error: save data not valid!=====",tmp.dataName+'-'+str(tmp.data_inst_idx))
                    if tmp.remain_time != 0:
                        # print("Writing back to DDR %s-%d, move: %d" % (tmp.dataName, tmp.data_inst_idx, tmp.mov_dir))
                        transmitTime += RM.dmaSaveData(tmp)
                    # print("******************************%d"%tmp.total_size)
                self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
                self.curSize += data.total_size
                self.peek = max(self.curSize,self.peek)
                return transmitTime

        # save data
        # print ("memory save %s" % data.dataName)

    # get data
    def getData(self, data):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            validData = self.map[data.dataName + "-" + str(data.data_inst_idx)]
            return validData,True
        else:
            return data,False

    def delData(self, data):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            tmp = self.map.pop(data.dataName + "-" + str(data.data_inst_idx))
            if tmp.remain_time > 0:
                print("memory error!:del dependency data!")
                self.map[data.dataName + "-" + str(data.data_inst_idx)] = tmp
            else:
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

    def checkMem(self,data):
        # can mem save data
        if self.curSize + data.total_size >= self.capacity:
            return False
        else:
            return True
