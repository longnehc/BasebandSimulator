from ResourceModule import ResourcesManager as RM
import numpy as np

class reporter:

    def __init__(self):
        self.cnt = 0
        self.dspCurCostMap = {}
        self.memPeekMap = {}
        self.memAccessMap = {}
        self.recordedMemAccess = {}


    def log(self):
        clusterList = RM.getClusterList()
        dspCurCost = []
        dspTotalCost = []
        memPeek = []
        for cluster in clusterList:
            memory = RM.getMemory(cluster)
            # print("===================================")
            # print("MEM peek %d of cluster %d" % (memory.peek, cluster.clusterId))
            if cluster.clusterId in self.memPeekMap:
                self.memPeekMap[cluster.clusterId].append(memory.peek)
            else:
                self.memPeekMap[cluster.clusterId] = [memory.peek]
            memory.peek = 0

            for dsp in cluster.dspList:
                # print("%d %d || %d" %(dsp.id, dsp.curCost, dsp.totalCost))
                dspCurCost.append(dsp.curCost)
                dspTotalCost.append(dsp.totalCost)
                # dsp 
        self.dspCurCostArr.append(dspCurCost)
        self.dspTotalCostArr.append(dspTotalCost)
        self.cnt += 1

        # The utilization of dsp
        dspUtilization = []
        for cluster in RM.getClusterList():
            for dsp in cluster.dspList:
                dspUtilization.append(1.0-dsp.yieldTime)

        # Task begin and finish time

        # print("dsps std %d" % np.std(dspCurCost))
        # print(np.std(dspTotalCost))

    def report(self):
        dspCurStd = 0
        dspTotalStd = 0
        for dspCurCost in self.dspCurCostArr:
            dspCurStd += np.std(dspCurCost)
        for dspTotalCost in self.dspTotalCostArr:
            dspTotalStd += np.std(dspTotalCost)
        print("dsp avg. cur std %f" % (dspCurStd / self.cnt))
        print("dsp avg. total std %f" % (dspTotalStd / self.cnt))
         
        cnt = 0
        totalOffMem = 0
        for cluster in RM.getClusterList():
            for dsp in cluster.dspList:
                cnt += 1
                totalOffMem += RM.getDma(dsp).offChipAccess
                print("Off chip mem access : %d, dsp = %d" % (RM.getDma(dsp).offChipAccess, dsp.id))
        if cnt != 0:
            print("Total offmem = %f, avgerage offmem = %f" % (totalOffMem, totalOffMem/cnt))
        
    def graphReport(self):
        for keys in RM.getExecuteTimeMap(): 
            cnt = 0
            sum = 0
            for ele in RM.getExecuteTimeMap()[keys]:
                print("1. graph id, begin, end, cost: %d %f %f %f" % (keys, RM.getBeginTimeMap()[keys][cnt], RM.getEndTimeMap()[keys][cnt], ele))
                cnt += 1
                sum += ele
            print("2. graph %d avg cost %f" % (keys, sum / cnt))

    def loging(self, env):
        while True:
            print("Doing log at time: %f" % env.now)
            clusterList = RM.getClusterList()
            dspCurCost = [] 
            memPeek = []
            for cluster in clusterList:
                memory = RM.getMemory(cluster)
                # print("===================================")
                # print("MEM peek cluster %d is %d" % (cluster.clusterId, memory.peek))
                    
                if cluster.clusterId in self.memPeekMap:
                    self.memPeekMap[cluster.clusterId].append(memory.peek)
                else: 
                    self.memPeekMap[cluster.clusterId] = [memory.peek] 
                memory.peek = 0

                for dsp in cluster.dspList:
                    # print("%d %d || %d" %(dsp.id, dsp.curCost, dsp.totalCost))
                    if dsp.id in self.dspCurCostMap:
                        self.dspCurCostMap[dsp.id].append(dsp.curCost)
                    else:
                        self.dspCurCostMap[dsp.id] = [dsp.curCost] 
                        
                    curMemAccess = 0
                    if dsp.id in self.memAccessMap:
                        curMemAccess = RM.getDma(dsp).offChipAccess - self.recordedMemAccess[dsp.id]
                    else:
                        curMemAccess = RM.getDma(dsp).offChipAccess
                    self.recordedMemAccess[dsp.id] = RM.getDma(dsp).offChipAccess
                    if dsp.id in self.memAccessMap:
                        self.memAccessMap[dsp.id].append(curMemAccess)
                    else:
                        self.memAccessMap[dsp.id] = [curMemAccess]
                    
                    # print("%d || %d" %(dsp.id, curMemAccess))
            yield env.timeout(1)

    def memPeekReport(self):
        # print("memPeekReport")
        clusterList = RM.getClusterList()
        print(self.memPeekMap)
        for cluster in clusterList:
            # print("cccc %d" % cluster.clusterId)
            if cluster.clusterId in self.memPeekMap:
                print("3. Mem peek of cluster %d" % cluster.clusterId)
                print(*self.memPeekMap[cluster.clusterId]) 
    
    def dspCostReport(self):
        stdArr = []
        clusterList = RM.getClusterList()
        for cluster in clusterList:
            for dsp in cluster.dspList:
                if dsp.id in self.dspCurCostMap:
                    print("4. Dsp cost of dsp %d" % dsp.id)
                    print(*self.dspCurCostMap[dsp.id])
        print("=============%d" % len(self.dspCurCostMap[0]))
        for i in range(0, len(self.dspCurCostMap[0])):
            cost = []
            for cluster in clusterList:
                for dsp in cluster.dspList:
                    cost.append(self.dspCurCostMap[dsp.id][i])
            stdArr.append(np.std(cost))
        print("5. The dsp cost std is")
        print(*stdArr) 
                
    def memAccessReport(self):
        clusterList = RM.getClusterList()
        for cluster in clusterList:
            for dsp in cluster.dspList:
                if dsp.id in self.memAccessMap:
                    print("6. Dsp mem access of dsp %d" % dsp.id)
                    print(*self.memAccessMap[dsp.id])
        for i in range(0, len(self.memAccessMap[0])):
            access = []
            total = []
            for cluster in clusterList:
                for dsp in cluster.dspList:
                    access.append(self.memAccessMap[dsp.id][i])
            access.append(np.std(access))
            total.append(np.sum(access))
        print("7. The mem access std is")
        print(*access)
        print("8. The total mem access is")
        print(*total)

    def dspUtilReport(self):
        print("9. The utilization of dsp")
    
    def taskReport(self):
        print("10. Task begin time and end time")

    def run(self, env):
        reported = False
        while True: 
            print("system time: %f" % env.now)
            yield env.timeout(0.2)
            # if RM.getFinishGraphCnt() >= 6 and not reported:
            if env.now > 4 and not reported:
                self.graphReport()
                self.memPeekReport()
                self.dspCostReport()
                self.memAccessReport()
                self.dspUtilReport()
                self.taskReport()
                reported = True 
                
                