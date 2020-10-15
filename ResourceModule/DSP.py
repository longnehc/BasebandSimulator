from TaskModule.Task import TaskStatus
from ResourceModule.DMA import *
from ResourceModule.MEM import *
from queue import Queue
from ResourceModule import ResourcesManager as RM


class DSP:
    num = 0
    def __init__(self, env, clusterId):
        self.id = DSP.num
        DSP.num += 1
        self.taskQueue = Queue()
        self.speed = 1.3 * 1000000000
        self.clusterId = clusterId
        self.env = env

        self.totalCost = 0
        self.curCost = 0

    def submit(self, task):
        # print ("*************** %s"%self)
        self.taskQueue.put(task)

        # for report
        self.curCost += task.cost
        self.totalCost += task.cost
        # print("%d || %d" % (self.curCost, self.totalCost))


    def run(self, taskManager):
        while(True):
            while not self.taskQueue.empty():
                task = self.taskQueue.get()

                # print(task.taskName + " begin in %s"% self.id)
                # TODO: Task -> schedule(all task, dsp) -> DMA -> DSP -> DMA()

                # exe
                yield self.env.timeout(2000 * task.cost/self.speed)

                # write back
                for data in task.getDataInsOut():
                    RM.getMemory(self).saveData(data)
                    # print("dsp save %s" % data.data_inst_idx)

                # finish task
                task.taskStatus = TaskStatus.FINISH
                self.curCost -= task.cost
                graph = taskManager.getGraph(task.batchId, task.taskGraphId)
                graph.taskNum -= 1
                if graph.taskNum == 0:
                    graph.finished = True
                    print("graph %d finish %f and cost %f"% (graph.graphId, self.env.now, self.env.now - graph.submitTime))
                    if graph.graphId in RM.getExecuteTimeMap():
                        RM.getExecuteTimeMap()[graph.graphId].append(self.env.now - graph.submitTime)
                    else:
                        RM.setFinishGraphCnt(RM.getFinishGraphCnt() + 1)
                        RM.getExecuteTimeMap()[graph.graphId] = [self.env.now - graph.submitTime]
                # if graph.taskNum < 0:
                #     print("graph %d task %d %s" % (graph.graphId,graph.taskNum,task.taskName))
                # print(task.taskName + " finish in: %f" % self.env.now)

            yield self.env.timeout(0.0002)