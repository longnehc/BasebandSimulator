from ResourceModule import ResourcesManager as RM 

class DMA:
    def __init__(self, clusterId):
        self.clusterId = clusterId

    def getData(self, data):
        accessTime = 0
        find = False
        """
        find from other cluster or DDR
        """
        for cluster in RM.getClusterList():
            Mem = cluster.memoryList[0]
            accessTime += 1
            if data.dataName + "-" + str(data.data_inst_idx) in Mem.map.keys():
                gotData = Mem.map[data.dataName + "-" + str(data.data_inst_idx)]
                find = True
                break
        #find in DDR
        if not find:
            accessTime += 1
            DDR = RM.getDDR()
            if data.dataName + "-" + str(data.data_inst_idx) in DDR.map.keys():
                gotData = DDR.map[data.dataName + "-" + str(data.data_inst_idx)]
                find = True
            else:
                print("not in DDR!!!!!!!!!!!!",data.dataName + "-" + str(data.data_inst_idx))
        return gotData,accessTime

    def saveData(self, data):
        #print("write data back to DDR!!!!!!!!!!")
        DDR = RM.getDDR()
        DDR.map[data.dataName + "-" + str(data.data_inst_idx)] = data
        return True