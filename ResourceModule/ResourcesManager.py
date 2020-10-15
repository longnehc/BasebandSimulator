from ResourceModule import Cluster
from ResourceModule import DMA

from TaskModule.Task import TaskStatus


class ResourcesManager:

    def __init__(self):
        self.name = "ResourceModule manager"
        self.clusterList = []
        self.finishGraphCnt = 0
        self.executeTimeMap = {}


resourcesManager = ResourcesManager()

 
 
def submitTaskToDma(task, clusterId, dmaId):
    cluster = getCluster(clusterId)
    dma = cluster.getDma(dmaId)
    if len(dma.taskList) < dma.capacity:
        dma.submit(task)
        task.taskStatus = TaskStatus.SUMBITTED
        return True
    else:
        # print(len(dma.taskList))
        return False
    # dma.submit(task)
    # task.taskStatus = TaskStatus.SUMBITTED


def submitTaskToDsp(task, clusterId, dspId):
    cluster = getCluster(clusterId)
    dsp = cluster.getDsp(dspId)
    dsp.submit(task)


def getExecuteTimeMap():
    return resourcesManager.executeTimeMap

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

def test(env, data, memory):
    print("TTTTTTTTTTTTTTTTTTTTTTTest")