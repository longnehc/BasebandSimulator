import functools

from TaskModule.TaskGraph import *
from TaskModule.Task import *
from TaskModule.DataInstance import *
from ResourceModule import ResourcesManager as RM
from TaskModule import Scheduler as scheduler
from TaskModule.Task import TaskStatus
from Algorithm import offChipMem

import random

from TaskModule.Scheduler import SchduleAlgorithm

a = 0.000001
b = 10
def QosPreemption(t1, t2):
    # p1 = (a * t1.graphCost + b * t1.graphPriority)/(t1.graphDDL - TaskManager.env.now + 0.001)
    # p2 = (a * t2.graphCost + b * t2.graphPriority) / (t2.graphDDL - TaskManager.env.now + 0.001)
    if scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionG.value:
        p1 = (t1.graphCost + t1.graphPriority) / (max(0, t1.graphDDL - TaskManager.env.now) + 0.001)
        p2 = (t2.graphCost + t2.graphPriority) / (max(0, t2.graphDDL - TaskManager.env.now) + 0.001)
        return p2 - p1
    elif scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionT.value:
        if t1.graphDDL != t2.graphDDL:
            return t1.graphDDL - t2.graphDDL
        else:
            return t1.cost - t2.cost
    else:
        # print("算法：%d；实际：%d"%(scheduler.getAlgorithm().value,SchduleAlgorithm.QOSPreemptionT.value))
        p1 = (t1.graphCost + t1.graphPriority) / (max(0, t1.graphDDL - TaskManager.env.now) + 0.001)
        p2 = (t2.graphCost + t2.graphPriority) / (max(0, t2.graphDDL - TaskManager.env.now) + 0.001)
        return p2 - p1


class TaskManager:
    env = None
    
    def __init__(self, graphList):
        self.graphSubmitFrequency = 2 
        self.taskSubmitFrequency = 1
        self.curBatch = 1
        self.batchId = 1
        self.graphList = graphList 
        self.candidateGraphBuffer = {self.batchId:{}}  # {key:batchID, value: {{graphId : graph}}}
        self.candidateTaskBuffer = []
        # {key:batchId,value:graph}
        self.graphRecorder = {self.batchId:[]}
        self.taskBatch = 1
        self.taskFactory = {self.taskBatch: []} #{key:batchId : value:{key: jobId: value: task}}


      
        

    def submitGraph(self, env):
        if TaskManager.env is None:
            TaskManager.env = env
        while True:    
            for i in range (1, self.batchId + 1):
                submitted = False 
                for graphId in self.candidateGraphBuffer[i]:
                    # print("i: %d  graphId: %d"%(i,graphId))
                    graph = self.candidateGraphBuffer[i][graphId]
                    prepareToSumbit = True
                    # print("batch = %d, graphId= %d, graph-finished = %d" % (i, graphId, graph.finished))
                    #[for g in graph.getPrecedenceGraph() if g.submitted and not graph.submitted]
                    if not graph.submitted:
                        # print("Checking graph dependency of graph%d" % graph.graphId)
                        # print(graph.getPrecedenceGraph())
                        for preGraphId in graph.getPrecedenceGraph():
                            # print("%d, %d,%d"%(i, preGraphId, self.candidateGraphBuffer[i][preGraphId].finished))
                            if preGraphId in self.candidateGraphBuffer[i] and not self.candidateGraphBuffer[i][preGraphId].finished:
                                prepareToSumbit = False         # the precedence graphs of the graph are all finished
                        if prepareToSumbit:
                            # print("%d, %d,%d" % (graphId, preGraphId, self.candidateGraphBuffer[i][preGraphId].finished))
                            # OffChip schedule
                            # offChipMem.offChipMem(graph)
                            graph.submitted = True                    # find a graph to submit
                            submitted = True
                            # TODO: EDF
                            for task in graph.getGlobalTaskList():
                                self.candidateTaskBuffer.append(task)
                            print("Add all tasks of graph %d in the %d-th batch into candidateTaskBuffer at %f " % (graph.graphId, i, env.now))
                            # QOS Preemption
                            # print("%s | %s" % (scheduler.getAlgorithm(),SchduleAlgorithm.QOSPreemptionG))
                            # print(scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionG.value)
                            if scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionG.value or scheduler.getAlgorithm().value == SchduleAlgorithm.QOSReserve.value or scheduler.getAlgorithm().value == SchduleAlgorithm.QOSPreemptionT.value:
                                # print(graph.QosReserve)
                                self.candidateTaskBuffer = sorted(self.candidateTaskBuffer,
                                                              key=functools.cmp_to_key(QosPreemption))
                                # for jj in range(0, len(self.candidateTaskBuffer)):
                                #     print(self.candidateTaskBuffer[jj].taskGraphId, end=" ")
                                # print("TM")
                                cost = 0
                                ddl = 1000
                                reserveList = []
                                # Qos reserve
                                if graph.QosReserve and scheduler.getAlgorithm().value != SchduleAlgorithm.QOSReserve.value:
                                    for gId in self.candidateGraphBuffer[i]:
                                        g = self.candidateGraphBuffer[i][gId]
                                        if g.QosReserve:
                                            reserveList.append(g.graphId)
                                            ddl = min(ddl, g.submitTime + g.DDL)
                                            for task in g.getGlobalTaskList():
                                                cost += task.cost
                                    print("submitTime is %.2f,now is %.2f, so we have %.2f, and cost is %.2f"% (graph.submitTime, env.now, (ddl - env.now), cost))
                                    clusterNum = (int)(1.8 * (2000 * cost / (5.2 * 1000000000)) / (ddl - env.now))
                                    clusterList = RM.getClusterList()
                                    dspCost = 0
                                    clusterNum = min(clusterNum, RM.getClusterNum()-1)
                                    for ii in range(0, clusterNum):
                                        for dsp in clusterList[ii].getDspList():
                                            dspCost += dsp.curCost
                                    print("dsp cost is %d"%dspCost)
                                    clusterNum += (int)(1.8 * (2000 * dspCost / (5.2 * 1000000000)) / (ddl - env.now))
                                    if clusterNum < 0:
                                        clusterNum = RM.getClusterNum() * 0.9
                                    clusterNum = min(clusterNum, RM.getClusterNum()-1)
                                    for id in reserveList:
                                        print("graph %d has %d cluster"%(id, clusterNum))
                                    scheduler.beginQosReserve(reserveList, ddl, (int)(clusterNum))
                            # break
                    # if graphId == 4:
                    #     print(len(graph.globalTaskList))
            # print("---------------------================================")
            # yield env.timeout(self.graphSubmitFrequency)
            # yield env.timeout(0.05)  # TODO
            yield env.timeout(0.01)  # TODO

    def constructTask(self, task):
        #name, knrlType, instCnt, jobId, graphId, job_inst_idx
        #constructing new task based on task
        newtask = Task(task.taskName, task.knrlType, task.instCnt, task.jobId, task.taskGraphId, task.job_inst_idx, task.cost)
        newtask.clusterId = task.clusterId
        #set the precedence task
        newtask.setPrecedenceJobID(task.precedenceJobID)
        #set the input data instance
        dataInsIn = []
        for indata in task.dataInsIn:
            dataDataInstance = DataInstance(indata.dataName, indata.mov_dir, indata.job_inst_idx, indata.total_size, indata.data_inst_idx)
            dataInsIn.append(dataDataInstance)
        newtask.setDataInsIn(dataInsIn)
 
        #set the output data instance
        dataOutIn = []
        for outdata in task.dataInsOut:
            dataDataInstance = DataInstance(outdata.dataName, outdata.mov_dir, outdata.job_inst_idx,
                outdata.total_size, outdata.data_inst_idx)
            dataDataInstance.remain_time = outdata.mov_dir
            dataOutIn.append(dataDataInstance)
        newtask.setDataInsOut(dataOutIn)
        return newtask

    def contructGraphById(self, graphId, batchId):
        graph = self.graphList[graphId]
        newglobalTaskList = []
        #Note: this map is used to build precedenceTask
        newglobalTaskMap = {} #key:jobId: value: newtask  
        #construct global task list without dependency
        for task in graph.globalTaskList:
            newglobalTaskList.append(self.taskFactory[batchId][task.jobId])
            #rebuild the task dependency based on the MAP and PRECEDENCE TASK NAME
        for task in newglobalTaskList:
            precedenceTaskList = []
            for jobId in task.precedenceJobID:
                precedenceTaskList.append(self.taskFactory[batchId][jobId])
            task.setPrecedenceTask(precedenceTaskList)
        newgraph = TaskGraph(graph.graphId, graph.graphName, graph.DDL, graph.period, newglobalTaskList, graph.precedenceGraph)        
        return newgraph
 

    def taskGenerator(self, env, minPeriod):
        while True:
            taskMap = {}
            for graph in self.graphList:
                for task in graph.globalTaskList:
                    newtask = self.constructTask(task)
                    # newtask.graphDDL = graph.DDL + env.now
                    taskMap[newtask.jobId] = newtask
                    # if newtask.taskGraphId == 3:
                        # print("*******************")
            self.taskFactory[self.taskBatch] = taskMap
            self.taskBatch += 1
            yield env.timeout(minPeriod)

    def graphGenerator(self, env, graph):
        yield env.timeout(graph.arrivalTime)
        while True: 
            find = False
            # print(graph.graphId)
            for i in range (1, self.batchId + 1):
                #print(self.candidateGraphBuffer[i])
                #print("=========")
                if graph.graphId not in self.candidateGraphBuffer[i]:      #new graph belongs to the existence batch
                    find = True
                    newgraph = self.contructGraphById(graph.graphId, i)
                    self.candidateGraphBuffer[i][graph.graphId] = newgraph
                    newgraph.submitTime = env.now
                    newgraph.batchId = i
                    newgraph.QosReserve = graph.QosReserve


                    newgraph.graphCost = graph.graphCost
                    for task in newgraph.globalTaskList:
                        task.batchId = i
                        task.graphDDL = graph.layerDdl[task.layer] + env.now
                        task.graphCost = graph.graphCost
                        task.graphPriority = graph.priority
                        task.graphSumbittedTime = newgraph.submitTime 
                        # if task.taskGraphId == 3:
                        #     print("******************** %d" % task.graphDDL)
                    # print("not find graphid = %d in batch= %d" % (graph.graphId, i))
                    # print(self.candidateGraphBuffer[i])
                    # print("Add graph %d into candidate graph buffer of the %d-th batch at %f " % (graph.getGraphId(), i, env.now))
                    break
            if not find:                                                    #new graph belongs to the new batch
                self.batchId += 1
                # print("batch id %d %d" % (self.batchId, graph.graphId))
                newgraph = self.contructGraphById(graph.graphId, self.batchId)
                newgraph.submitTime  = env.now
                newgraph.batchId = self.batchId
                newgraph.QosReserve = graph.QosReserve
                self.candidateGraphBuffer[self.batchId] = {graph.graphId : newgraph}
                # print("Add graph %d into candidate graph buffer of the %d-th batch at %f " % (graph.getGraphId(), self.batchId, env.now))
                self.graphRecorder[i] = [newgraph]
                for task in newgraph.globalTaskList:
                    task.batchId = self.batchId
                    task.graphDDL = graph.DDL + env.now
                    task.graphSumbittedTime = newgraph.submitTime 
                    # if task.taskGraphId == 3:
                    #     print("******************** %d"%task.graphDDL)
            yield env.timeout(graph.getPeriod())
            # yield env.timeout(1)
            
    def schedule(self, env):
        #       ####if offmem： {task.cluster = 1} = offmem()
        #taskGraphs[], candidateTask[]
        scheduleFrequency=2
        while True:
            #print("schedule algorithm is invoked at %d " % env.now)
            #res = getScheduleRes()
            #updateResource(res)
            yield env.timeout(scheduleFrequency)
            # yield env.timeout(0.002)

    def getScheduleRes(self):
        #print("Make schedulings: load-balance/min-offchipmem/greedy/QoSguarantee")
        return 1

    def updateResource(self, res):
        #print("Update resource availablities based on scheduling results")
        return 1

    taskNum = 0
    def submitTask(self, env):
        # for task in candidate_queue:
        #     # check if task is ready
        #     if check_task_dependency(task):
        #         candidate_queue.remove(task)
        #         scheduleUtil.allocate_cluster
        while True: 
            remove = []
            for i in range(len(self.candidateTaskBuffer)):
                # print("********** %f" % env.now)
                task = self.candidateTaskBuffer[i]

                if task.taskStatus != TaskStatus.FINISH and task.taskStatus != TaskStatus.SUMBITTED:
                    prepareToSumbit = True
                    # print("Checking task dependency of %s... " % task.taskName)
                    for predTask in task.precedenceTask:
                        # print("========")
                        # print(predTask)
                        # print("========")
                        if predTask.taskStatus != TaskStatus.FINISH:
                            prepareToSumbit = False
                            #print("%s wait for %s ...." % (task.taskName, predTask.taskName))
                    if prepareToSumbit:
                        # print("Submit %s !!!!!!!!!!!" % task.taskName)
                        #print(task)
                        # task.taskStatus = TaskStatus.FINISH    # TODO: need modified in other place
                        #schedule()
                        #ResourceManager.placeCluster(1)
                        remove.append(i)
                        # task.taskStatus = TaskStatus.SUMBITTED
                        #TODO: QoS guarantee/Load balancing/greedy/random/offmem chip
                        # print(task.taskGraphId, end="*")
                        scheduler.submit(task)
                        #env.process(scheduler.run(env)) 
                        # if task.taskGraphId == 4:
                        #     self.taskNum += 1
                        #     print(self.taskNum)
            self.candidateTaskBuffer = [self.candidateTaskBuffer[i] for i in range(len(self.candidateTaskBuffer)) 
                if i not in remove] 
            # 0.05 ns
            yield env.timeout(0.0001)
            # yield env.timeout(1)

        
    def taskXMLParser(self, filename):
        #parse task parameteres and dependencies
        return 1


    def getGraph(self, i, j):
        return self.candidateGraphBuffer[i][j]


