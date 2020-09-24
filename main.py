
import simpy
from TaskModule.XMLParse import *
import resources.ResourcesManager as RM
from report.reporter import reporter

# 1TTI = 1s(*2000)
if __name__ == "__main__":
    # Setup and start the simulation
    print('Baseband simulator starting') 

  
    #taskGraphs = taskManager.taskXMLParser("taskgraph.xml")
    #hardwareConfig = ResourceManager.hardwareXMLParser("hardware.xml")
 
    ClusterNum = 4
    DSPPerCluster = 4
    MemCapacity = 100
    DMASpeed = 10
    DDRCapacity = 100
    SIM_TIME = 1

    # Create an environment and start the setup process
    env = simpy.Environment()
    #
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

    for graph in graphList:     #TODO
        graph.DDL = 1
        graph.period = 1
        graph.precedenceGraph = []

    taskManager = TaskManager(graphList)
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

    env.process(reporter().run(env))
    RM.setCluster(env, 16)
    for cluster in RM.getClusterList():
        for dsp in cluster.getDspList():
            env.process(dsp.run())
        for dma in cluster.getDmaList():
            env.process(dma.run())

    # Execute!
    env.run(until=SIM_TIME)