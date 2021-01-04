from ResourceModule import Cluster
from ResourceModule import DDR

from TaskModule.Task import TaskStatus
from TaskModule import Scheduler as scheduler
import random


class ResourcesManager:

    def __init__(self):
        self.name = "ResourceModule manager"
        self.clusterList = []
        self.finishGraphCnt = 0
        self.executeTimeMap = {}
        self.beginTimeMap = {}
        self.endTimeMap = {}
        self.taskExeMap = []
        self.taskLogMap = {}
        self.submittedTaskNum = 0
        self.waitTime = 0.0
        self.reserveGraph = {}
        self.DDR = {}
        self.FHAC = {}
        #dma speed is 256 * 866 * 1000000
        self.speed = 256 * 866 * 1000000



resourcesManager = ResourcesManager()

 
 
def submitTaskToCluster(task, clusterId, env):
    cluster = getCluster(clusterId)
    if cluster.submit(task):
        task.taskStatus = TaskStatus.SUMBITTED
        task.submittedTime = env.now
        resourcesManager.submittedTaskNum += 1
        resourcesManager.waitTime += (task.submittedTime - task.graphSumbittedTime)
        return True
    else:
        # print(len(dma.taskList))
        return False
    # dma.submit(task)
    # task.taskStatus = TaskStatus.SUMBITTED

def submitTaskToDsp(task, clusterId, dspId):
    cluster = getCluster(clusterId)
    dsp = cluster.getDsp(dspId)
    # 01
    dsp.submit(task)

def dmaSaveData(data):
    #print("write data back to DDR!!!!!!!!!!")
    DDR = getDDR()
    DDR.map[data.dataName + "-" + str(data.data_inst_idx)] = data
    transmitTime = 2000 * data.total_size / resourcesManager.speed
    return transmitTime

def dmaGetData(data):
    accessTime = 0
    transmitTime = 2000 * data.total_size / resourcesManager.speed
    find = False
    #find from other cluster or DDR
    for cluster in getClusterList():
        Mem = cluster.memoryList[0]
        accessTime += 1
        if data.dataName + "-" + str(data.data_inst_idx) in Mem.map.keys():
            gotData = Mem.map[data.dataName + "-" + str(data.data_inst_idx)][0]
            find = True
            break
    #find from FHAC mem
    if not find:
        accessTime += 1
        Mem = getCluster(-1).memoryList[0]
        if data.dataName + "-" + str(data.data_inst_idx) in Mem.map.keys():
            gotData = Mem.map[data.dataName + "-" + str(data.data_inst_idx)][0]
            find = True
    #find in DDR
    if not find:
        accessTime += 1
        DDR = getDDR()
        if data.dataName + "-" + str(data.data_inst_idx) in DDR.map.keys():
            gotData = DDR.map[data.dataName + "-" + str(data.data_inst_idx)]
            find = True
        else:
            print("not in DDR!!!!!!!!!!!!",data.dataName + "-" + str(data.data_inst_idx))
    return gotData, accessTime, transmitTime

def delData(data):
    if data.remain_time > 0:
        print("memory error!:del dependency data!")
    for cluster in resourcesManager.clusterList:
        mem = cluster.getMemory(0)
        mem.delData(data)
    fhacMem = getCluster(-1).getMemory(0)
    fhacMem.delData(data)

def getSubmittedTaskNum():
    return resourcesManager.submittedTaskNum

def getWaitTime():
    return resourcesManager.waitTime

def getExecuteTimeMap():
    return resourcesManager.executeTimeMap

def getBeginTimeMap():
    return resourcesManager.beginTimeMap

def getEndTimeMap():
    return resourcesManager.endTimeMap

def getFinishGraphCnt():
    return resourcesManager.finishGraphCnt

def setFinishGraphCnt(cnt):
    resourcesManager.finishGraphCnt = cnt

def getClusterList():
    return resourcesManager.clusterList

def getClusterNum():
    return len(resourcesManager.clusterList)

def getCluster(index):
    if index < 0:
        return resourcesManager.FHAC
    else:
        return resourcesManager.clusterList[index]

def setCluster(env, num, dmaControl):

    #withpooling
    for i in range(0, num):
        # print("set cluster %d"%i)
        resourcesManager.clusterList.append(Cluster.Cluster(env, i, dmaControl))
    """
    #withoutpooling
    for i in range(0, num):
        # print("set cluster %d"%i)
        resourcesManager.clusterList.append(Cluster.Cluster(env, i, dmaControl[num]))
    """

def setFhacCluster(env, dmaControl):
    
    #withpooling
    resourcesManager.FHAC = Cluster.Cluster(env,-1, dmaControl)
    """
    #withoutpooling
    resourcesManager.FHAC = Cluster.Cluster(env,-1, dmaControl[-1])
    """

def setReserveGraph(id, ddl):
    resourcesManager.reserveGraph[id] = ddl

def getReserveGraph():
    return resourcesManager.reserveGraph

def getMemory(component):
    cluster = getCluster(component.clusterId)
    return cluster.getMemory(0)

def getTransmitSpeed(component):
    cluster = getCluster(component.clusterId)
    return cluster.speed

# clear cluster's taskList [] TODO:
def clearCluster(start, end):
    for i in range(start, end + 1):
        # cnt = end + 1
        cluster = resourcesManager.clusterList[i]
        for task in cluster.taskList:
            chosenCluster = resourcesManager.clusterList[random.randint(end+1, getClusterNum()-1)]
            chosenCluster.submit(task)
            # cnt += 1
        cluster.taskList = []


def getTaskExeMap():
    return resourcesManager.taskExeMap

def getTaskLogMap():
    return resourcesManager.taskLogMap

def setDDR(capacity, dataInit):
    resourcesManager.DDR = DDR.DDR(capacity, dataInit)

def getDDR():
    return resourcesManager.DDR
 

def test(env, data, memory):
    print("TTTTTTTTTTTTTTTTTTTTTTTest")

"""
def getIdleDma():
    dma = None
    for cluster in resourcesManager.clusterList:
        for dsp in cluster.dspList:
            if len(dsp.taskQueue) == 0:
                dma = cluster.getDma(0)
                return dma
    return dma
"""

def checkDspIdle(clusterId,env):
    cluster = resourcesManager.clusterList[clusterId]
    mem = cluster.getMemory(0)
    waitTime = 0
    speed = cluster.dspList[0].speed
    cost = []
    for dsp in cluster.dspList:
        cost.append(dsp.curCost)
    cost.sort()
    interval = (cost[0]+cost[1]+2)/2
    WaitTimeCtrl = (cost[2]+cost[3])/2
    while True:
        if mem.curSize > 1900000:
            waitTime += interval/speed
            if waitTime > WaitTimeCtrl/speed:
                print("tooooooooooooooo long")
                transmitTime = mem.squeeze()
                yield env.timeout(transmitTime/5)
                break
            yield env.timeout(interval/speed)
        else:
            break