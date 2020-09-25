
from TaskModule.TaskGraph import * 
from TaskModule.Task import *
from TaskModule.DataInstance import *
from ResourceModule import ResourcesManager as RM

import random

class TaskManager: 
    
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
        

    def submitGraph(self, env):
        while True:   
            for i in range (self.curBatch, self.batchId + 1):
                submitted = False
                for graphId in self.candidateGraphBuffer[i]:
                    graph = self.candidateGraphBuffer[i][graphId]
                    prepareToSumbit = True
                    # print("batch = %d, graphId= %d, graph-finished = %d" % (i, graphId, graph.finished))
                    #[for g in graph.getPrecedenceGraph() if g.submitted and not graph.submitted]
                    if not graph.submitted:
                        # print("Checking graph dependency....")
                        for preGraphId in graph.getPrecedenceGraph():
                            if not self.candidateGraphBuffer[i][preGraphId].finished:
                                prepareToSumbit = False         # the precedence graphs of the graph are all finished
                        if prepareToSumbit:
                            # graph.finished = True               # TODO: need to modify
                            graph.submitted = True                    # find a graph to submit
                            # TODO: EDF
                            for task in graph.getGlobalTaskList():
                                self.candidateTaskBuffer.append(task)
                            # print("Add all tasks of graph %d in the %d-th batch into candidateTaskBuffer at %f " % (graph.graphId, i, env.now))
                            # break
                    # if graphId == 4:
                    #     print(len(graph.globalTaskList))
                if submitted:
                    break
                else:
                    self.curBatch = i + 1                       # an improvement to skip the totally executed batch
            # print("---------------------================================")
            yield env.timeout(self.graphSubmitFrequency)
            # yield env.timeout(0.002)  # TODO

    def constructTask(self, task):
        #name, knrlType, instCnt, jobId, graphId, job_inst_idx
        #constructing new task based on task
        newtask = Task(task.taskName, task.knrlType, task.instCnt, task.jobId, task.taskGraphId, task.job_inst_idx, task.cost)
        #set the precedence task 
        newtask.setPrecedenceJobID(task.precedenceJobID)
        #set the input data instance
        dataInsIn = []
        for indata in task.dataInsIn:
            dataInsIn.append(DataInstance(indata.dataName, indata.mov_dir, indata.job_inst_idx,
                indata.total_size, indata.data_inst_idx))
        newtask.setDataInsIn(dataInsIn)
 
        #set the output data instance
        dataOutIn = []
        for outdata in task.dataInsOut:
            dataOutIn.append(DataInstance(outdata.dataName, outdata.mov_dir, outdata.job_inst_idx,
                outdata.total_size, outdata.data_inst_idx))
        newtask.setDataInsOut(dataOutIn)
        return newtask

    def contructGraphById(self, graphId):
        graph = self.graphList[graphId]
        newglobalTaskList = []
        #Note: this map is used to build precedenceTask
        newglobalTaskMap = {} #key:jobId: value: newtask  
        #construct global task list without dependency
        for task in graph.globalTaskList:
            newtask = self.constructTask(task)
            newglobalTaskList.append(newtask)
            newglobalTaskMap[task.jobId] = newtask
        #rebuild the task dependency based on the MAP and PRECEDENCE TASK NAME
        for task in newglobalTaskList:
            precedenceTaskList = []
            for jobId in task.precedenceJobID:
                precedenceTaskList.append(newglobalTaskMap[jobId])
            task.setPrecedenceTask(precedenceTaskList)
        newgraph = TaskGraph(graph.graphId, graph.graphName, graph.DDL, graph.period, newglobalTaskList, graph.precedenceGraph)        
        return newgraph

    def graphGenerator(self, env, graph):
        while True: 
            find = False
            newgraph = self.contructGraphById(graph.graphId)
            for i in range (1, self.batchId + 1):
                #print(self.candidateGraphBuffer[i])
                #print("=========")
                if graph.graphId not in self.candidateGraphBuffer[i]:      #new graph belongs to the existence batch
                    find = True
                    self.candidateGraphBuffer[i][graph.graphId] = newgraph
                    for task in newgraph.globalTaskList:
                        task.batchId = i
                    #print("not find graphid = %d in batch= %d" % (graph.graphId, i))
                    #print(self.candidateGraphBuffer[i])
                    # print("Add graph %d into candidate graph buffer of the %d-th batch at %f " % (graph.getGraphId(), i, env.now))
                    break
            if not find:                                                    #new graph belongs to the new batch
                self.batchId += 1
                self.candidateGraphBuffer[self.batchId] = {graph.graphId : newgraph}
                # print("Add graph %d into candidate graph buffer of the %d-th batch at %f " % (graph.getGraphId(), self.batchId, env.now))
                self.graphRecorder[i] = [newgraph]
                for task in newgraph.globalTaskList:
                    task.batchId = self.batchId
            yield env.timeout(graph.getPeriod())
            # yield env.timeout(0.1)
            
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
            for i in range(len(self.candidateTaskBuffer)):
                # print("********** %f" % env.now)
                task = self.candidateTaskBuffer[i]
                remove = []
                if task.taskStatus != TaskStatus.FINISH and task.taskStatus != TaskStatus.SUMBITTED:
                    prepareToSumbit = True
                    # print("Checking task dependency of %s... " % task.taskName)
                    for predTask in task.precedenceTask:
                        # print("========")
                        # print(predTask)
                        # print("========")
                        if predTask.taskStatus != TaskStatus.FINISH:
                            prepareToSumbit = False
                            print("%s wait for %s ...." % (task.taskName, predTask.taskName))
                    if prepareToSumbit:
                        # print("Submit %s !!!!!!!!!!!" % task.taskName)
                        #print(task)
                        # task.taskStatus = TaskStatus.FINISH    # TODO: need modified in other place
                        #schedule()
                        #ResourceManager.placeCluster(1)
                        remove.append(i)
                        task.taskStatus = TaskStatus.SUMBITTED
                        RM.submitTask(task, random.randint(0, 15), random.randint(0, 3))
                        # if task.taskGraphId == 4:
                        #     self.taskNum += 1
                        #     print(self.taskNum)
            for i in remove:
                self.candidateTaskBuffer.pop(i)
            # 0.05 ns
            yield env.timeout(0.0001)
            # yield env.timeout(1)

        
    def taskXMLParser(self, filename):
        #parse task parameteres and dependencies
        return 1


    def getGraph(self, i, j):
        return self.candidateGraphBuffer[i][j]

