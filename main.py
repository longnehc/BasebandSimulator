#coding=utf-8
import simpy
from TaskModule.XMLParse import *
from ResourceModule import ResourcesManager as RM
from report.reporter import reporter
from TaskModule import Scheduler as scheduler
from TaskModule.Scheduler import SchduleAlgorithm
from Algorithm import offChipMem
import math


def costCmp(g1, g2):
    return g1.graphCost - g2.graphCost

# 1TTI = 1s(*2000)
def setGraphLayer(graph):
    hight = 0
    for task in graph.globalTaskList:
        setTaskLayer(graph, task)
        hight = max(hight, task.layer)
    return hight + 1


def setTaskLayer(graph, task):
    if task.layer != -1:
        return task.layer
    elif len(task.precedenceTask) == 0:
        task.layer = 0
        return task.layer
    else:
        tmp = -1
        for t in task.precedenceTask:
            tmp = max(setTaskLayer(graph, t), tmp)
        task.layer = tmp + 1
        return task.layer


if __name__ == "__main__":
    # Setup and start the simulation
    print('Baseband simulator starting') 

  
    #taskGraphs = taskManager.taskXMLParser("taskgraph.xml")
    #hardwareConfig = ResourceManager.hardwareXMLParser("hardware.xml")
 
    ClusterNum = 20
    DSPPerCluster = 4
    MemCapacity = 100
    DMASpeed = 10
    DDRCapacity = 100
    SIM_TIME = 10
    """change with algo"""
    selectedAlgo = SchduleAlgorithm.QOSPreemptionG
    rpt = reporter()
    """change with algo"""
    """only reserve"""
    rpt.rflag = False

    # Create an environment and start the setup process
    env = simpy.Environment()

    #print("Task graph parser begins")
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = TaskXMLHandler()
    parser.setContentHandler( Handler )
    parser.parse("TaskGraph0903.xml")
    graphList = Handler.getGraphList()  
    #print(graphList)
    #print(len(graphList))
    #print("Task graph parser ends")

    initData = Handler.getInitData()
    producerMap = Handler.getProducerMap()
    consumerMap = Handler.getConsumerMap()
    #print("=====debug from Shine: init data,",initData) 
    
    # graph 0, 1, 2, 3, 4, 5
    DDLList = [100, 0.8, 1.5, 4, 1, 100]
    PeriodList = [1, 1, 1, 4, 1, 1]
    PriorityList = [1, 4, 3, 1, 1, 1]
    ArrivalTimeList = [0, 0, 0, 4, 0, 0]
    # DDLList = [100, 0.8, 1.5, 4, 1, 100]
    # PeriodList = [1, 1, 1, 1, 1, 1]
    # PriorityList = [1, 2, 3, 4, 5, 6]
    # ArrivalTimeList = [0, 0, 0, 0, 0, 0]
    graphIndex = 0
    of = open("0graphDependency.txt","w")
    for graph in graphList:
        precedenceGraphMap = {} 
        # print("=========")
        # print(precedenceGraphMap)
        # print("=========")
        # 87-100  #
        for task in graph.globalTaskList:
            for datains in task.dataInsIn:
                key = datains.dataName + "-" + str(datains.data_inst_idx)
                if key in producerMap:
                    if producerMap[key].taskGraphId != task.taskGraphId:
                        if producerMap[key].taskGraphId not in precedenceGraphMap:
                            precedenceGraphMap[producerMap[key].taskGraphId] = 1
                            print("graph%d depends on graph%d" % (task.taskGraphId, producerMap[key].taskGraphId))
                            of.write("%d " % producerMap[key].taskGraphId)
                        task.precedenceTask.append(producerMap[key])
                        task.precedenceJobID.append(producerMap[key].jobId)
                        # print("Cross graph task dependency: %s depends on %s" % (task.taskName, producerMap[key].taskName))
            for dataouts in task.dataInsOut:
                key = dataouts.dataName + "-" + str(dataouts.data_inst_idx)
                if key in consumerMap:
                    dataouts.mov_dir = consumerMap[key]
        of.write("\n")
        for key in precedenceGraphMap:
            graph.precedenceGraph.append(key)           #set precedenceGraph for graph, 除了时隙的都可以直接分析
        # print(graph.precedenceGraph)
        graph.DDL = DDLList[graphIndex]
        graph.period = PeriodList[graphIndex]
        graph.priority = PriorityList[graphIndex]
        graph.arrivalTime = ArrivalTimeList[graphIndex]
        graphIndex += 1
    of.close()

    taskManager = TaskManager(graphList)
    minPeriod = 1 # minimal period of all graphs
    env.process(taskManager.taskGenerator(env, minPeriod))



    """change with algo"""
    """only reserve"""
    # Qos Reserve
    """
    graphList[1].QosReserve = True
    graphList[4].QosReserve = True
    graphList[5].QosReserve = True
    """
    
    RM.setCluster(env, ClusterNum)
    for i in range(ClusterNum):
        RM.setDma(1,i)

    initDataIns = []
    for key in initData:
        idxList = key.split('-')
        refCnt = consumerMap[idxList[0]+'-'+idxList[1]]
        dataIns = DataInstance(idxList[0],refCnt,0,int(idxList[2]),idxList[1])
        #data initialized in DDR won't be removed
        dataIns.remain_time = 100000
        initDataIns.append(dataIns)
    RM.setDDR(1000000,initDataIns)
    
    RM.setReserveGraph(1, 0.8)

    # off-chip Mem
    if selectedAlgo == SchduleAlgorithm.OFFMEM:
        for graph in graphList:
            offChipMem.offChipMem(graph)

    # print("?????????%d"%len(graphList))
    # env.process(taskManager.graphGenerator(env, graphList[4]))
    
    maxCost = 0
    for graph in graphList:
        if graph.graphCost == -1:
                tmp = 0
                for task in graph.globalTaskList:
                    tmp += task.cost
                    graph.graphCost = tmp     
                if tmp > maxCost:
                    maxCost = tmp    
        #print("graph %d cost %f" % (graph.graphId, graph.graphCost))
        hight = setGraphLayer(graph)
        for i in range(0, hight):
            graph.layerCost.append(0)
            graph.layerDdl.append(0)
        for t in graph.globalTaskList:
            graph.layerCost[t.layer] += t.cost
        rate = 0
        for i in range(0, hight):
            graph.layerCost[i] /= (graph.graphCost + 1)
            rate += graph.layerCost[i]
            graph.layerDdl[i] = graph.DDL * rate
        # for i in range(0, hight):
        #     print(graph.layerDdl[i], end=",")
        # print(" ")


    # graphList = sorted(graphList, key=functools.cmp_to_key(costCmp))

    # for i in range(len(graphList)):
    #     graphList[i].graphCost = i
    #     print("graph %d normalized cost %d" % (graphList[i].graphId, graphList[i].graphCost))
    for graph in graphList: 
        graph.graphCost = math.ceil((graph.graphCost / maxCost) * 5)
        print("graph %d normalized cost %f" % (graph.graphId, graph.graphCost))

    for graph in graphList:
       env.process(taskManager.graphGenerator(env, graph))
    
    env.process(taskManager.submitGraph(env))
      
    # for(TaskManager.generateTask()) -> candidateGraphQ  tti 
    # submitgraph() indegree=0
    #    {  
    #       ####if offmem： {task.cluster = 1} = offmem()
    #       candidateTaskBuffer = {tasks} 
    #    }

    #ready_queue_update->->DSP
    # update task graph by time
    #schedule(a graph, all tasks)

    
    env.process(taskManager.submitTask(env))
    
    rpt.setAlgorithm(selectedAlgo)
   
    env.process(rpt.run(env))
    env.process(rpt.loging(env))
   
    scheduler.setAlgorithm(selectedAlgo)
    env.process(scheduler.run(env))
    for cluster in RM.getClusterList():
        env.process(cluster.run())
        for dsp in cluster.getDspList():
            env.process(dsp.run(taskManager))
        for FHAC in cluster.getFHACList():
            env.process(FHAC.run(taskManager))

    # Execute!
    env.run(until=SIM_TIME)
    #rpt.dspRunningReport()




