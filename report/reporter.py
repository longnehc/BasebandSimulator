from ResourceModule import ResourcesManager as RM
import numpy as np

class reporter:

    def __init__(self):
        self.cnt = 0
        self.dspCurCostArr = []
        self.dspTotalCostArr = []
        self.memPeekMap = {}

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
        for cluster in RM.getClusterList():
            if cluster.clusterId in self.memPeekMap:
                print("Mem peek of cluster %d" % cluster.clusterId)
                print(*self.memPeekMap[cluster.clusterId]) 
                # for memPeek in self.memPeekMap[cluster.clusterId]:
                #     print("Mem peek of cluster %d is %d" % (cluster.clusterId, memPeek))
        cnt = 0
        totalOffMem = 0
        for cluster in RM.getClusterList():
            for dsp in cluster.dspList:
                cnt += 1
                totalOffMem += RM.getDma(dsp).offChipAccess
                print("Off chip mem access : %d, dsp = %d" % (RM.getDma(dsp).offChipAccess, dsp.id))
        if cnt != 0:
            print("Total offmem = %f, avgerage offmem = %f" % (totalOffMem, totalOffMem/cnt))
        


    def run(self, env):
        reported = False
        while True:
            self.log()
            print("system time: %f" % env.now)
            yield env.timeout(0.2)
            if RM.getFinishGraphCnt() >= 6 and not reported:
                reported = True
                self.report()
                for keys in RM.getExecuteTimeMap(): 
                    cnt = 0
                    sum = 0
                    for ele in RM.getExecuteTimeMap()[keys]:
                        cnt += 1
                        sum += ele
                        print("graph %d cost %f" % (keys, ele))
                    print("graph %d avg cost %f" % (keys, sum / cnt))