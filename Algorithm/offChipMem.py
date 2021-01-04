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
        dataIn1 += data.total_size
    for data in t2.getDataInsIn():
        dataIn2 += data.total_size
    # 大到小
    return dataIn2 - dataIn1

def cmpCluster(c1, c2):
    global clusterNum

    if c1.load > c2.load * 1.5:
        return 1
    elif c2.load > c1.load * 1.5:
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
offMEMSize = 0


def offChipMem(taskGraph):
    print("graph %d off-chip begin"% taskGraph.graphId)
    global clusterNum
    global clusterDataCnt
    global clusterMap
    global dataProducerMap
    global offMEMSize

    clusterNum = RM.getClusterNum()
    # print(clusterNum)
    clusterDataCnt = []
    ClusterNode.cnt = 0
    clusterMap.clear()
    dataProducerMap.clear()
    for i in range(0, clusterNum + 1):
        clusterNode = ClusterNode()
        clusterDataCnt.append(clusterNode)
        clusterMap[i] = clusterNode

    for i in range(0, len(taskGraph.globalTaskList)):
        task = taskGraph.globalTaskList[i]
        for data in task.dataInsOut:
            dataProducerMap[data.dataName + "-" + str(data.data_inst_idx)] = task
    # print("###############################%d"%len(dataProducerMap.keys()))

    initTaskList = []
    for i in range(0, len(taskGraph.globalTaskList)):
        task = taskGraph.globalTaskList[i]
        if len(task.dataInsIn) == 0:
            initTaskList.append(task)
        else:
            flag = True
            for data in task.dataInsIn:
                if data.dataName + "-" + str(data.data_inst_idx) in dataProducerMap.keys():
                    flag = False
            if flag:
                initTaskList.append(task)

    print("**********************%d,--%d"%(len(initTaskList), len(initTaskList) / clusterNum))

    clusterTaskNum = len(initTaskList) / clusterNum
    tmp = 0
    initClusterId = 0
    k = 0
    while tmp < len(initTaskList):
        for i in range(0, clusterNum):
            task = initTaskList[tmp]
            task.clusterId = k
            tmp += 1
            if tmp == len(initTaskList):
                break
        k += 1
        if k == clusterNum:
            k = 0

    # for i in range(0, len(initTaskList)):
    #     task = initTaskList[i]
    #     print("-----------%d"%task.clusterId)



    # print(clusterNum)
    tmpTaskList = sorted(taskGraph.globalTaskList, key=functools.cmp_to_key(cmpTask))



    for i in range(0, len(tmpTaskList)):
        task = tmpTaskList[i]
        if task.clusterId != -1:
            continue
        setCluster(task, taskGraph)

    # for task in tmpTaskList:
    #     print("%d||%d"%(task.taskGraphId,task.clusterId))

    for cluster in clusterDataCnt:
        print(cluster.load)
    print(offMEMSize)

    print("graph %d off-chip done"% taskGraph.graphId)

def setCluster(task, taskGraph):
    global clusterDataCnt
    global clusterMap
    global dataProducerMap
    global offMEMSize

    # print("set %d" % task.jobId)

    if task.knrlType == "FHAC":
        task.clusterId = clusterNum
        return clusterNum

    if len(taskGraph.globalTaskList) == 0:
        return 0

    dataIn = task.dataInsIn
    clearClusterNode()

    for dataInstance in dataIn:
        if dataInstance.dataName + "-" + str(dataInstance.data_inst_idx) in dataProducerMap.keys():
            producer = dataProducerMap.get(dataInstance.dataName + "-" + str(dataInstance.data_inst_idx))
            if producer.clusterId == -1:
                setCluster(producer, taskGraph)
        else:
            continue

    for dataInstance in dataIn:
        if dataInstance.dataName + "-" + str(dataInstance.data_inst_idx) in dataProducerMap.keys():
            producer = dataProducerMap.get(dataInstance.dataName + "-" + str(dataInstance.data_inst_idx))
            # get producer's cluster
            precedenceCluster = producer.clusterId
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
    if task.clusterId == clusterNum:
        task.clusterId = clusterList[1].id

    for cluster in clusterDataCnt:
        if cluster.id != task.clusterId and cluster.id != clusterNum:
            offMEMSize += cluster.totalSize

    clusterNode = clusterMap.get(task.clusterId)
    # print("load in %d but the task.cluster id is %d"% (clusterNode.id,task.clusterId))
    clusterNode.load += task.cost
    return task.clusterId

def clearClusterNode():
    for cluster in clusterDataCnt:
        cluster.totalSize = 0