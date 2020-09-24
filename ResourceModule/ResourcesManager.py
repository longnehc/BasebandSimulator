from ResourceModule import Cluster
from ResourceModule import DMA


class ResourcesManager:

    def __init__(self):
        self.name = "ResourceModule manager"
        self.clusterList = []


resourcesManager = ResourcesManager()

def getData(env, dsp, data):
    cluster = getCluster(dsp.clusterId)
    memory = cluster.getMemory(0)
    memory.getData(env, data, dsp)


def saveData(env, dsp, data):
    cluster = getCluster(dsp.clusterId)
    memory = cluster.getMemory(0)
    memory.saveData(env, data)


def submitTask(task, clusterId, dspId):
    cluster = getCluster(clusterId)
    dsp = cluster.getDsp(dspId)
    dsp.submit(task)


def getClusterList():
    return resourcesManager.clusterList


def getCluster(index):
    return resourcesManager.clusterList[index]


def setCluster(env, num):
    for i in range(0, num):
        # print("set cluster %d"%i)
        resourcesManager.clusterList.append(Cluster.Cluster(env, i))


def checkData(dsp, data):
    # get memory
    cluster = getCluster(dsp.clusterId)
    memory = cluster.getMemory(0)
    return memory.checkData(data)


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