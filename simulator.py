import collections 
import simpy

def taskXMLParser(filename):
    #parse task parameteres and dependencies
    return 1

def hardwareXMLParser(filename):
    #parse hardware configuration 
    return 1

def submitTaskGraph(env, taskGraphs):
    taskGraphtti=1
    while True: 
        print("submit taskGraph to resourceManager per tti at %d " % env.now)
        yield env.timeout(taskGraphtti)


def schedule(env):
    scheduleFrequency=2
    while True:
        print("schedule algorithm is invoked at %d " % env.now)
        res = getScheduleRes()
        updateResource(res)
        yield env.timeout(scheduleFrequency)

def getScheduleRes():
    print("Make schedulings: load-balance/min-offchipmem/greedy/QoSguarantee")
    return 1

def updateResource(res):
    print("Update resource availablities based on scheduling results")
    return 1

   
if __name__ == "__main__":
    # Setup and start the simulation
    print('Baseband simulator starting') 

    taskGraphs = taskXMLParser("taskgraph.xml")
    hardwareConfig = hardwareXMLParser("hardware.xml")
 
    ClusterNum = 4
    DSPPerCluster = 4
    MemCapacity = 100
    DMASpeed = 10
    DDRCapacity = 100
    SIM_TIME = 10

    # Create an environment and start the setup process
    env = simpy.Environment()
    env.process(submitTaskGraph(env, taskGraphs))
    env.process(schedule(env)) 

    # Execute!
    env.run(until=SIM_TIME)


