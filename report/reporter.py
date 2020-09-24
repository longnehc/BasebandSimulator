import resources.ResourcesManager as RM

class reporter:

    def report(self):
        clusterList = RM.getClusterList()
        for cluster in clusterList:
            memory = RM.getMemory(cluster)
            print(memory.curSize)

            for dsp in cluster.dspList:
                print("%d %d || %d" %(dsp.id, dsp.curCost, dsp.totalCost))

    def run(self, env):
        while True:
            self.report()
            yield env.timeout(0.1)