
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
    SIM_TIME = 50
    selectedAlgo = SchduleAlgorithm.LB

    # Create an environment and start the setup process
    env = simpy.Environment()
    
    # #dataName, mov_dir, job_inst_idx, total_size, data_inst_idx
    # d0 = DataInstance("data0", 0, 0, 100, 33792)
    # d1 = DataInstance("data1", 1, 0, 100, 256)
    # #name, knrlType, instCnt, jobId, graphId, job_inst_idx
    # t0 = Task("task0", "DSP", 1, 0, 0, 0)
    # t0.setDataInsIn([d0])
    # t0.setDataInsOut([d1])
    # t0.setPrecedenceJobID([])
    # #t0.setPrecedenceTask([])
    #
    # d2 = DataInstance("data2", 0, 0, 100, 3136)
    # d3 = DataInstance("data3", 1, 0, 100, 4032)
    #
    # t1 = Task("task1", "DSP", 1, 1, 1, 0)
    # t1.setDataInsIn([d2])
    # t1.setDataInsOut([d3])
    # t1.setPrecedenceJobID([])
    # #t1.setPrecedenceTask([])
    #
    # d4 = DataInstance("data3", 0, 0, 100, 102)
    # d5 = DataInstance("data4", 0, 0, 100, 3122)
    #
    # t2 = Task("task2", "DSP", 1, 2, 1, 0)
    # t2.setDataInsIn([d4])
    # t2.setDataInsOut([d5])
    # t2.setPrecedenceJobID([1])
    # #t2.setPrecedenceTask([t1])
    #
    # #graphId, graphName, DDL, period, globalTaskList, precedenceGraph
    # tg0 = TaskGraph(0, "graph0", 1, 1, [t0], [])
    # tg1 = TaskGraph(1, "graph1", 2, 1.5, [t1, t2], [0])
    
    #tg0: d0-t0-d1
    #tg1: d2-t1-d3, d4-t2-d5

    #graphList = [tg0, tg1] 

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

    
    
    taskManager = TaskManager(graphList)
    minPeriod = 1 # minimal period of all graphs 
    env.process(taskManager.taskGenerator(env, minPeriod))
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
                producerMap = Handler.getProducerMap()
                if key in producerMap:
                    if producerMap[key].taskGraphId != task.taskGraphId:
                        if producerMap[key].taskGraphId not in precedenceGraphMap:
                            precedenceGraphMap[producerMap[key].taskGraphId] = 1
                            print("graph%d depends on graph%d" % (task.taskGraphId, producerMap[key].taskGraphId))
                            of.write("%d " % producerMap[key].taskGraphId)
                        task.precedenceTask.append(producerMap[key])
                        task.precedenceJobID.append(producerMap[key].jobId)
                        # print("Cross graph task dependency: %s depends on %s" % (task.taskName, producerMap[key].taskName))
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
    # Qos Reserve
    graphList[1].QosReserve = True
    graphList[4].QosReserve = True
    graphList[5].QosReserve = True
    
    RM.setCluster(env, ClusterNum)

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
        print("graph %d cost %f" % (graph.graphId, graph.graphCost))


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
    rpt = reporter()
    env.process(rpt.run(env))
    env.process(rpt.loging(env))
   
    scheduler.setAlgorithm(selectedAlgo)
    env.process(scheduler.run(env))
    for cluster in RM.getClusterList():
        for dsp in cluster.getDspList():
            env.process(dsp.run(taskManager))
        for dma in cluster.getDmaList():
            env.process(dma.run())

    # Execute!
    env.run(until=SIM_TIME)