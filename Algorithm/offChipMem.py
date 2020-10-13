from ResourceModule import ResourcesManager as RM
import functools
import random


class ClusterNode:
    cnt = 0

    def __init__(self):
        self.load = 0
        self.totalSize = 0
        self.id = ClusterNode.cnt
        ClusterNode.cnt += 1

def cmpTask(t1, t2):
    dataIn1 = 0
    dataIn2 = 0
    for data in t1.getDataInsIn():
        dataIn1 += data.total_size;
    for data in t2.getDataInsIn():
        dataIn2 += data.total_size;
    # 大到小
    return dataIn2 - dataIn1

def cmpCluster(c1, c2):
    global clusterNum

    if c1.load > c2.load * 3:
        return 1
    elif c2.load > c1.load * 3:
        return -1
    elif c1.totalSize != c2.totalSize:
        # print("min off-chip mem")
        return c2.totalSize - c1.totalSize
    elif c1.load != c2.load:
        return c1.load - c2.load
    else:
        # print("random %d"%clusterNum)
        return random.randint(0, clusterNum)

clusterDataCnt = []
clusterMap = {}
dataProducerMap = {}
clusterNum = 0


def offChipMem(taskGraph):
    print("off-chip begin")
    global clusterNum
    global clusterDataCnt
    global clusterMap
    global dataProducerMap

    clusterNum = RM.getClusterNum()
    clusterDataCnt = []
    ClusterNode.cnt = 0
    clusterMap.clear()
    dataProducerMap.clear()
    for i in range(0, clusterNum):
        clusterNode = ClusterNode()
        clusterDataCnt.append(clusterNode)
        clusterMap[i] = clusterNode

    # print(clusterNum)
    tmpTaskList = sorted(taskGraph.globalTaskList, key=functools.cmp_to_key(cmpTask))

    for i in range(0, len(tmpTaskList)):
        task = tmpTaskList[i]
        for data in task.dataInsOut:
            dataProducerMap[data] = task
    # print("###############################%d"%len(dataProducerMap.keys()))


    for i in range(0, len(tmpTaskList)):
        task = tmpTaskList[i]
        if task.clusterId != -1:
            continue
        setCluster(task, taskGraph)

    # for task in tmpTaskList:
    #     print("%d||%d"%(task.taskGraphId,task.clusterId))

    # for cluster in clusterDataCnt:
    #     print(cluster.load)

    # print("finish set")

def setCluster(task, taskGraph):
    global clusterDataCnt
    global clusterMap
    global dataProducerMap

    # print("set %d" % task.jobId)

    if task.clusterId != -1:
        return task.clusterId
    if len(taskGraph.globalTaskList) == 0:
        return 0

    dataIn = task.dataInsIn
    clearClusterNode()

    for dataInstance in dataIn:
        if dataInstance in dataProducerMap.keys():
            producer = dataProducerMap.get(dataInstance)
            # get producer's cluster
            precedenceCluster = setCluster(producer, taskGraph)
            clusterMap.get(precedenceCluster).totalSize += dataInstance.total_size
        else:
            continue

    # print("----------------------------")
    # for cluster in clusterDataCnt:
    #     print("%d||%d"%(cluster.id, cluster.totalSize))
    # print("============================")

    clusterList = sorted(clusterDataCnt, key=functools.cmp_to_key(cmpCluster))
    # print("----------------------------")
    # for cluster in clusterList:
    #     print("%d||%d"%(cluster.id, cluster.load))
    # print("============================")

    task.clusterId = clusterList[0].id

    clusterNode = clusterMap.get(task.clusterId)
    # print("load in %d but the task.cluster id is %d"% (clusterNode.id,task.clusterId))
    clusterNode.load += task.cost
    return task.clusterId

def clearClusterNode():
    for cluster in clusterDataCnt:
        cluster.totalSize = 0