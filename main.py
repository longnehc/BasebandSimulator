import collections 
import simpy 
import TaskManager
import ResourceManager

 
if __name__ == "__main__":
    # Setup and start the simulation
    print('Baseband simulator starting') 

    taskGraphs = TaskManager.taskXMLParser("taskgraph.xml")
    hardwareConfig = ResourceManager.hardwareXMLParser("hardware.xml")
 
    ClusterNum = 4
    DSPPerCluster = 4
    MemCapacity = 100
    DMASpeed = 10
    DDRCapacity = 100
    SIM_TIME = 10

    # Create an environment and start the setup process
    env = simpy.Environment()

    env.process(TaskManager.submitTaskGraph(env, taskGraphs))
    # for(TaskManager.generateTask()) -> candidateGraphQ  tti 
    # submitgraph() indegree=0
    #    {  
    #       ####if offmem： {task.cluster = 1} = offmem()
    #       candidateTaskQ = {tasks} 
    #    }

    #ready_queue_update-pinglv>->DSP
    # update task graph by time
    #schedule(a graph, all tasks)
    env.process(TaskManager.ready_queue_update(env,1))

    # Execute!
    env.run(until=SIM_TIME)