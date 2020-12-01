from ResourceModule.DMA import *
from ResourceModule.DSP import *
from ResourceModule import ResourcesManager as RM
from collections import OrderedDict


class MEM:

    def __init__(self, clusterId):
        # key is dataName
        self.map = OrderedDict()

        #self.capacity = 100000
        self.capacity = 100000
        self.curSize = 0
        self.peek = 0

        self.clusterId = clusterId

    def saveData(self, data):
        transmitTime = 0
        # can mem save data
        # print("%s-%d" % (data.dataName, data.data_inst_idx))
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            print("=====debug from Shine: already have this data in MEM!=====")
            print("%s-%d" % (data.dataName, data.data_inst_idx))
            old = self.map[data.dataName + "-" + str(data.data_inst_idx)]
            if id(old)!=id(data):
                print("the old remain and new remain is: ",old.remain_time,data.remain_time)
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = old
        elif self.checkMem(data):
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
            self.curSize += data.total_size
        else:
            while self.curSize + data.total_size > self.capacity:
                tmp = self.map.popitem(last=False)[1]
                self.curSize -= tmp.total_size
                if tmp.remain_time < 0:
                    print("=====memory error: save data not valid!=====",tmp.dataName+'-'+str(tmp.data_inst_idx))
                if tmp.remain_time != 0:
                    # print("Writing back to DDR %s-%d, move: %d" % (tmp.dataName, tmp.data_inst_idx, tmp.mov_dir))
                    transmitTime += RM.submitWriteBackTaskToDma(tmp, self.clusterId, 0)
                # print("******************************%d"%tmp.total_size)
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
            self.curSize += data.total_size

        self.peek = max(self.curSize,self.peek)

        return transmitTime

        # save data
        # print ("memory save %s" % data.dataName)

    # get data
    def getData(self, env, data, dsp):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            validData = self.map[data.dataName + "-" + str(data.data_inst_idx)]
            transmitTime = 0
        else:
            cluster = RM.getCluster(self.clusterId)
            validData,accessTime,transmitTime = cluster.getDma(0).getData(data)
        return validData,transmitTime

    def delData(self, env, data, dsp):
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
