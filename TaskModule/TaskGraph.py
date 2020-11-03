class TaskGraph :
    def __init__(self, graphId, graphName, DDL, period, globalTaskList, precedenceGraph):
        self.graphId = graphId
        self.graphName = graphName
        self.DDL = DDL
        self.period = period
        self.globalTaskList = globalTaskList         #任务实例列表
        self.precedenceGraph = precedenceGraph       #存储该图前驱图的graphID
        self.submitTime = 0 
        self.finished = False
        self.taskNum = len(globalTaskList)
        self.submitted = False
        self.arrivalTime = 0
        self.priority = 0
        self.QosReserve = False
        self.batchId = 0

        self.graphCost = -1

        self.layerCost = []
        self.layerDdl = []
        
 
    def isSubmitted(self):
        return self.submitted

    def getGraphId(self):
        return self.graphId

    def getGlobalTaskList(self) :
        return self.globalTaskList
    
    def getPeriod(self) :
        return self.period
    
    def getPrecedenceGraph(self) :
        return self.precedenceGraph

    def setSubmitTime(self, submitTime):
        self.submitTime = submitTime