from ResourceModule import ResourcesManager as RM
import numpy as np
from TaskModule.Scheduler import SchduleAlgorithm

class reporter:

    def __init__(self):
        self.cnt = 0
        self.dspCurCostMap = {}
        self.memPeekMap = {}
        self.memAccessMap = {}
        self.recordedMemAccess = {}
        self.dspUtilRecord = {}
        self.prefix = ""


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
        fo = open(self.prefix + "/1graphExecutionDur.txt", "w")
        fo2 = open(self.prefix + "/2graphAvgCost.txt","w")
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

    def maxExecutionReport(self):
        fo = open(self.prefix + "/11maxExecutionTime.txt", "w")
        cnt = 0
        satifycnt = 0
        # for keys in RM.getBeginTimeMap():
        #     fo.write("%d ", keys)
        # fo.write("\n")
        for keys in RM.getExecuteTimeMap():
            max = -1
            for ele in RM.getExecuteTimeMap()[keys]:
                if ele > max:
                    max = ele
            if keys in RM.getReserveGraph():
                cnt += 1
                if ele <= RM.getReserveGraph()[keys]:
                    satifycnt += 1
            fo.write("%f " % max)
        fo.write("\n%f" % (satifycnt / cnt))
        fo.close()
    
    def avgWaitTime(self):
        fo = open(self.prefix + "/12avgWaitTime.txt", "w")
        fo.write("%f " % (RM.getWaitTime() / RM.getSubmittedTaskNum()))
        fo.close()



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
                        self.dspUtilRecord[dsp.id].append((0.1 - dsp.yieldTime)/0.1)
                        dsp.yieldTime = 0
                    else:
                        self.dspUtilRecord[dsp.id] = [(0.1 - dsp.yieldTime)/0.1]
                        dsp.yieldTime = 0
            yield env.timeout(0.1)

    def memPeekReport(self):
        # print("memPeekReport")
        fo = open(self.prefix + "/3memPeek.txt","w")
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
        fo = open(self.prefix + "/4dspCost.txt","w")
        fo2 = open(self.prefix + "/5dspCostStd.txt","w")
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
        fo = open(self.prefix + "/6dspMemAccess.txt","w")
        fo2 = open(self.prefix + "/7dspMemStd.txt","w")
        fo3 = open(self.prefix + "/8totalMemAcess.txt", "w")
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
        fo = open(self.prefix + "/9DSPUtil.txt","w")
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
    
    
    def resourceUtilReport(self):
        fo = open(self.prefix + "/13resourceUtil.txt", "w")
        clusterList = RM.getClusterList()
        for i in range(0, len(self.dspUtilRecord[0])):
            util = 0.0
            cnt = 0
            for cluster in clusterList:
                for dsp in cluster.dspList:
                    if dsp.id in self.dspUtilRecord:
                        util += self.dspUtilRecord[dsp.id][i]
                        cnt += 1
            fo.write("%f " % (util / cnt))
        fo.close()
 
    
    def taskReport(self):
        fo = open(self.prefix + "/10TaskExecutionDur.txt","w")
        print("10. Task begin time and end time")
        taskTimeMap = {}
        for i in range(0, len(RM.getTaskExeMap())):
            for taskname in RM.getTaskExeMap()[i]:
                timelist = []
                for jobidx in RM.getTaskExeMap()[i][taskname]:
                    for j in range(0, len(RM.getTaskExeMap()[i][taskname][jobidx])):
                        timelist.append(RM.getTaskExeMap()[i][taskname][jobidx][j]) 
                print(*timelist)
                if taskname in taskTimeMap:
                    taskTimeMap[taskname].extend(timelist)
                else:
                    taskTimeMap[taskname] = timelist

        for taskname in taskTimeMap:
            fo.write("%s\n" % taskname)
            begin = taskTimeMap[taskname][0]
            end = taskTimeMap[taskname][1]
            for i in range(2, len(taskTimeMap[taskname])):
                if i % 2 == 0:
                    if taskTimeMap[taskname][i] > end:
                        fo.write("%f %f " % (begin, end))
                        begin = taskTimeMap[taskname][i]
                else:
                    end = taskTimeMap[taskname][i]
            fo.write("%f %f " % (begin, end))
            fo.write("\n")

        # for taskname in RM.getTaskLogMap():
        #     timelist = []
        #     print("The begin and end time of %s" % taskname)
        #     fo.write("%s\n" % taskname)
        #     for jobidx in RM.getTaskLogMap()[taskname]:
        #         for i in range(0, len(RM.getTaskLogMap()[taskname][jobidx])):
        #             timelist.append(RM.getTaskLogMap()[taskname][jobidx][i]) 
        #             # fo.write("%f " % RM.getTaskLogMap()[taskname][jobidx][i])
        #     print(*timelist)
        #     begin = timelist[0]
        #     end = timelist[1]
        #     for i in range(2, len(timelist)):
        #         if i % 2 == 0:
        #             if timelist[i] > end:
        #                 fo.write("%f %f " % (begin, end))
        #                 begin = timelist[i]
        #         else:
        #             end = timelist[i]
        #     fo.write("%f %f " % (begin, end))
        #     fo.write("\n")
        fo.close()

    def setAlgorithm(self, selectedAlgo):
        self.selectedAlgo = selectedAlgo

    def run(self, env):
        reported = False
        if self.selectedAlgo == SchduleAlgorithm.QOSPreemptionG and self.rflag == False:
            self.prefix = "QOSPreemptionG"
        elif self.selectedAlgo == SchduleAlgorithm.QOSPreemptionT:
            self.prefix = "QOSPreemptionT"
        elif self.selectedAlgo == SchduleAlgorithm.LB:
            self.prefix = "LB"
        elif self.selectedAlgo == SchduleAlgorithm.QOSPreemptionG and self.rflag == True:
            self.prefix = "QOSReserve"  
        else:
            self.prefix = "OFFMEM"
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
                self.maxExecutionReport()
                self.avgWaitTime()
                self.resourceUtilReport()
                reported = True