from ResourceModule import ResourcesManager as RM
from collections import OrderedDict

class DDR:

    def __init__(self,capacity,initData):
        # key is dataName + datainstanceID
        self.map = OrderedDict()
        self.speed = 1
        # self.capacity = 100000 * 100
        self.capacity = capacity
        self.curSize = 0
        self.peek = 0
        for data in initData:
            key = data.dataName + "-" + str(data.data_inst_idx)
            self.map[key] = data
    
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
