from ResourceModule import ResourcesManager as RM 

class DMA:
    def __init__(self, clusterId):
        self.clusterId = clusterId

    def getData(self, data):
        print("get data from other clusters or DDR!!!!!!!!!!")
        accessTime = 0
        find = False
        """
        find from other cluster or DDR
        """
        for cluster in RM.getClusterList():
            Mem = cluster.memoryList[0]
            accessTime += 1
            if data.dataName + "-" + str(data.data_inst_idx) in Mem.map.keys():
                find = True
                break
        #find in DDR
        if not find:
            accessTime += 1
            DDR = RM.getDDR()
            if data.dataName + "-" + str(data.data_inst_idx) in DDR.map.keys():
                find = True
            else:
                print("not in DDR!!!!!!!!!!!!")
                self.saveData(data)
        RM.getCluster(self.clusterId).memoryList[0].saveData()
        return accessTime

    def saveData(self, data):
        print("write data back to DDR!!!!!!!!!!")
        DDR = RM.getDDR()
        DDR.map[data.dataName + "-" + str(data.data_inst_idx)] = data
        return True