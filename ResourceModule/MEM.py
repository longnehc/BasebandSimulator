from ResourceModule.DMA import *
from ResourceModule.DSP import *
from ResourceModule import ResourcesManager as RM
from collections import OrderedDict


class MEM:

    def __init__(self, clusterId):
        # key is dataName
        self.map = OrderedDict()
        self.speed = 1

        #self.capacity = 100000
        self.capacity = 100000
        self.curSize = 0
        self.peek = 0

        self.clusterId = clusterId

    def saveData(self, data):
        saveToDDR = False
        # can mem save data
        # print("%s-%d" % (data.dataName, data.data_inst_idx))
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            self.map.pop(data.dataName + "-" + str(data.data_inst_idx))
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
        elif self.checkMem(data):
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
            self.curSize += data.total_size
        else:
            saveToDDR = True
            while self.curSize + data.total_size > self.capacity:
                tmp = self.map.popitem(last=False)[1]
                self.curSize -= tmp.total_size
                if tmp.remain_time < 0:
                    print("=====memory error: save data not valid!=====",tmp.dataName+'-'+str(tmp.data_inst_idx))
                if tmp.remain_time != 0:
                    # print("Writing back to DDR %s-%d, move: %d" % (tmp.dataName, tmp.data_inst_idx, tmp.mov_dir))
                    if not RM.submitWriteBackTaskToDma(tmp, self.clusterId, 0):
                        print("Write back buffer full, write back failed")
                # print("******************************%d"%tmp.total_size)
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
            self.curSize += data.total_size

        self.peek = max(self.curSize,self.peek)

        return saveToDDR

        # save data
        # print ("memory save %s" % data.dataName)

    # get data
    def getData(self, env, data, dsp):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            validData = self.map[data.dataName + "-" + str(data.data_inst_idx)]
        else:
            cluster = RM.getCluster(self.clusterId)
            validData, _ = cluster.getDma(0).getData(data)
        return validData

    def delData(self, env, data, dsp):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            self.map.pop(data.dataName + "-" + str(data.data_inst_idx))
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
