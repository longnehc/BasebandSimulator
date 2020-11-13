from ResourceModule import ResourcesManager as RM
from collections import OrderedDict

class DDR:

    def __init__(self,capacity):
        # key is dataName + datainstanceID
        self.map = OrderedDict()
        self.speed = 1
        # self.capacity = 100000 * 100
        self.capacity = capacity
        self.curSize = 0
        self.peek = 0 
    
    def saveData(self, data):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            self.map.pop(data.dataName + "-" + str(data.data_inst_idx))
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
        elif self.checkDDRCapacity(data):
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
            self.curSize += data.total_size
        else:
            while self.curSize + data.total_size > self.capacity:
                tmp = self.map.popitem(last=False)[1]
                self.curSize -= tmp.total_size    
                # print("******************************%d"%tmp.total_size)
            self.map[data.dataName + "-" + str(data.data_inst_idx)] = data
            self.curSize += data.total_size
    
    def checkData(data):
        if data.dataName + "-" + str(data.data_inst_idx) in self.map.keys():
            return True
        else:
            return False

    def checkDDRCapacity(self,data):
        # can mem save data
        if self.curSize + data.total_size >= self.capacity:
            return False
        else:
            return True
