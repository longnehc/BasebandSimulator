from ResourceModule import ResourcesManager as RM
import numpy as np

class reporter:

    def __init__(self):
        self.cnt = 0
        self.dspCurCostMap = {}
        self.memPeekMap = {}
        self.memAccessMap = {}
        self.recordedMemAccess = {}
        self.dspUtilRecord = {}



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
        fo = open("1graphExecutionDur.txt", "w")
        fo2 = open("2graphAvgCost.txt","w")
        for keys in RM.getExecuteTimeMap(): 
            cnt = 0
            sum = 0
            fo.write("%d\n" % keys)
            fo2.write("%d\n" % keys)
            for ele in RM.getExecuteTimeMap()[keys]:
                fo.write("%f %f " % (RM.getBeginTimeMap()[keys][cnt], RM.getEndTimeMap()[keys][cnt]))
                print("1. graph id, begin, end, cost: %d %f %f %f" % (keys, RM.getBeginTimeMap()[keys][cnt], RM.getEndTimeMap()[keys][cnt], ele))
                cnt += 1
                sum += ele
            fo.write("\n")
            fo2.write("%f \n" % (sum / cnt))
            print("2. graph %d avg cost %f" % (keys, sum / cnt))

        fo.close()
        fo2.close()

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

                    # The utilization of dsp
                    if dsp.id in self.dspUtilRecord:
                        self.dspUtilRecord[dsp.id].append(0.1 - dsp.yieldTime)
                        dsp.yieldTime = 0
                    else:
                        self.dspUtilRecord[dsp.id] = [0.1 - dsp.yieldTime]
                        dsp.yieldTime = 0
            yield env.timeout(0.1)

    def memPeekReport(self):
        # print("memPeekReport")
        fo = open("3memPeek.txt","w")
        clusterList = RM.getClusterList()
        print(self.memPeekMap)
        for cluster in clusterList:
            # print("cccc %d" % cluster.clusterId)
            if cluster.clusterId in self.memPeekMap:
                fo.write("%d\n" % cluster.clusterId) 
                for i in range(0, len(self.memPeekMap[cluster.clusterId])):
                    fo.write("%f " % self.memPeekMap[cluster.clusterId][i])
                fo.write("\n")
                print("3. Mem peek of cluster %d" % cluster.clusterId)
                print(*self.memPeekMap[cluster.clusterId]) 
        fo.close()
    
    def dspCostReport(self):
        fo = open("4dspCost.txt","w")
        fo2 = open("5dspCostStd.txt","w")
        stdArr = []
        clusterList = RM.getClusterList()
        for cluster in clusterList:
            for dsp in cluster.dspList:
                if dsp.id in self.dspCurCostMap:
                    print("4. Dsp cost of dsp %d" % dsp.id)
                    print(*self.dspCurCostMap[dsp.id])
                    fo.write("%d\n" % dsp.id)
                    for i in range(0, len(self.dspCurCostMap[dsp.id])):
                        fo.write("%f " % self.dspCurCostMap[dsp.id][i])
                    fo.write("\n")
        print("=============%d" % len(self.dspCurCostMap[0]))
        for i in range(0, len(self.dspCurCostMap[0])):
            cost = []
            for cluster in clusterList:
                for dsp in cluster.dspList:
                    cost.append(self.dspCurCostMap[dsp.id][i])
            stdArr.append(np.std(cost))
        print("5. The dsp cost std is")
        for i in range(0, len(stdArr)):
            fo2.write("%f " % stdArr[i])
        print(*stdArr) 
        fo.close()
        fo2.close()
                
    def memAccessReport(self):
        fo = open("6dspMemAccess.txt","w")
        fo2 = open("7dspMemStd.txt","w")
        fo3 = open("8totalMemAcess.txt", "w")
        clusterList = RM.getClusterList()
        for cluster in clusterList:
            for dsp in cluster.dspList:
                if dsp.id in self.memAccessMap:
                    print("6. Dsp mem access of dsp %d" % dsp.id)
                    print(*self.memAccessMap[dsp.id])
                    fo.write("%d\n" % dsp.id)
                    for i in range(0, len(self.memAccessMap[dsp.id])):
                        fo.write("%f " % self.memAccessMap[dsp.id][i])
                    fo.write("\n")
        total = []
        memstd = []
        for i in range(0, len(self.memAccessMap[0])):
            access = [] 
            for cluster in clusterList:
                for dsp in cluster.dspList:
                    access.append(self.memAccessMap[dsp.id][i])
            memstd.append(np.std(access))
            total.append(np.sum(access))
        print("7. The mem access std is")
        print(*memstd)
        for i in range(0, len(memstd)):
            fo2.write("%f " % memstd[i])
        print("8. The total mem access is")
        for i in range(0, len(total)):
            fo3.write("%f " % total[i])
        print(*total)
        fo.close()
        fo2.close()
        fo3.close()

    def dspUtilReport(self):
        fo = open("9DSPUtil.txt","w")
        print("9. The utilization of dsp")
        clusterList = RM.getClusterList()
        for cluster in clusterList:
            for dsp in cluster.dspList:
                if dsp.id in self.dspUtilRecord:
                    print("dsp %d" % dsp.id)
                    print(*self.dspUtilRecord[dsp.id])
                    fo.write("%d\n" % dsp.id)
                    for i in range(0, len(self.dspUtilRecord[dsp.id])):
                        fo.write("%f " % self.dspUtilRecord[dsp.id][i])
                    fo.write("\n")
        fo.close()
    
    def taskReport(self):
        fo = open("10TaskExecutionDur.txt","w")
        print("10. Task begin time and end time")
        for taskname in RM.getTaskLogMap():
            timelist = []
            print("The begin and end time of %s" % taskname)
            fo.write("%s\n" % taskname)
            for jobidx in RM.getTaskLogMap()[taskname]:
                for i in range(0, len(RM.getTaskLogMap()[taskname][jobidx])):
                    timelist.append(RM.getTaskLogMap()[taskname][jobidx][i]) 
                    fo.write("%f " % RM.getTaskLogMap()[taskname][jobidx][i])
            print(*timelist)
            fo.write("\n")
        fo.close()

    def run(self, env):
        reported = False
        while True: 
            print("system time: %f" % env.now)
            yield env.timeout(0.2)
            # if RM.getFinishGraphCnt() >= 6 and not reported:
            if env.now > 6 and not reported:
                self.graphReport()
                self.memPeekReport()
                self.dspCostReport()
                self.memAccessReport()
                self.dspUtilReport()
                self.taskReport()
                reported = True