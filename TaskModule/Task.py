from enum import Enum
# cost：开销
# instCnt：个数
# property：优先级
# knrlType：处理器类型

class TaskStatus(Enum):
    WAIT = 0 
    EXECUTING = 1
    FINISH = 2
    SUMBITTED = 3

class Task:
    # taskName,knrlType,instCnt,cost,priority,dataForTask,job_inst_idx,total_size,data_inst_idx
    
    def __init__(self, name, knrlType, instCnt, jobId, graphId, job_inst_idx, cost):
        self.taskName = name
        self.knrlType = knrlType
        self.instCnt = instCnt
        self.cost = 0
        self.property = 0
        self.jobId = jobId
        self.taskGraphId = graphId
        self.job_inst_idx = job_inst_idx
        self.cost = cost

        #graphSchedule
        self.clusterId = -1

        #输入输出数据总量
        self.InputDataSize = 0
        self.OutputDataSize = 0
 
        self.taskStatus = TaskStatus.WAIT
        self.precedenceJobID = []
        self.precedenceTask = []
        self.precedenceGraphID = []

        #任务实例属性 
        self.graphDDL = 0.0 
        self.submittedTime = 0
    
        #输入输出的data实例
        self.dataInsIn = [] #DataInstance
        self.dataInsOut = [] #DataInstance

        self.batchId = 0


    def getTaskStatus(self) :
        return self.taskStatus
    
    def setTaskStatus(self, taskStatus) :
        self.taskStatus = taskStatus
    
    def setPrecedenceTask(self, precedenceTask) :
        self.precedenceTask = precedenceTask

    def setPrecedenceJobID(self, precedenceJobID) :
        self.precedenceJobID = precedenceJobID    

    def setPrecedenceGraphID(self, precedenceGraphID) :
        self.precedenceGraphID = precedenceGraphID    

    def setDataInsIn(self, dataInsIn) :
        self.dataInsIn = dataInsIn
    

    def setDataInsOut(self, dataInsOut) :
        self.dataInsOut = dataInsOut

    def getDataInsIn(self):
        return self.dataInsIn

    def getDataInsOut(self) :
        return self.dataInsOut


    def getJob_inst_idx(self) :
        return job_inst_idx
    
    def setTaskGraphId(self, taskGraphId) :
        self.taskGraphId = taskGraphId
    
    def setGraphDDL(self, graphDDL):
        self.graphDDL = graphDDL
    
    def setSubmittedTime(self, submittedTime):
        self.submittedTime = submittedTime

    def ifFinish(self):
        if self.taskStatus == TaskStatus.FINISH:
            return True
        else:
            return False
    
   

