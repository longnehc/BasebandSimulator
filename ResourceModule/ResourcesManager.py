from ResourceModule import Cluster
from ResourceModule import DMA
from ResourceModule import DDR

from TaskModule.Task import TaskStatus
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
    # 02
    # if dsp.taskQueue.qsize() < dsp.capacity:
    #     dsp.submit(task)
    #     return True
    # else:
    #     # print(len(dma.taskList))
    #     return False

def submitTaskToFHAC(task, clusterId):
    cluster = getCluster(clusterId)
    dsp = cluster.getFHACList()[0]
    dsp.submit(task)

def submitWriteBackTaskToDma(data, clusterId, dmaId):
    cluster = getCluster(clusterId)
    dma = cluster.getDma(dmaId)
    return dma.saveData(data)

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
    return resourcesManager.clusterList[index]


def setCluster(env, num):
    for i in range(0, num):
        # print("set cluster %d"%i)
        resourcesManager.clusterList.append(Cluster.Cluster(env, i))

def setDma(num, clusterId):
    cluster = getCluster(clusterId)
    for i in range(0,num):
        cluster.dmaList.append(DMA.DMA(clusterId))

def setReserveGraph(id, ddl):
    resourcesManager.reserveGraph[id] = ddl

def getReserveGraph():
    return resourcesManager.reserveGraph
  
def getDma(dsp):
    # get memory
    cluster = getCluster(dsp.clusterId)
    return cluster.getDma(0)


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