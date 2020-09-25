from ResourceModule import ResourcesManager as RM
import numpy as np

class reporter:

    def report(self):
        clusterList = RM.getClusterList()
        dspCurCost = []
        dspTotalCost = []
        for cluster in clusterList:
            memory = RM.getMemory(cluster)
            print("===================================")
            print("MEM peek %d"%memory.peek)
            memory.peek = 0

            for dsp in cluster.dspList:
                # print("%d %d || %d" %(dsp.id, dsp.curCost, dsp.totalCost))
                dspCurCost.append(dsp.curCost)
                dspTotalCost.append(dsp.totalCost)
                # dsp
            print("dsps std %d"%np.std(dspCurCost))
            # print(np.std(dspTotalCost))
    def run(self, env):
        while True:
            # self.report()
            print(env.now)
            yield env.timeout(0.5)