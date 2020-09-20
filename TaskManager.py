import ResourceManager


def submitTaskGraph(env, taskGraphs):
    taskGraphtti = 1
    while True: 
        print("submit taskGraph to resourceManager per tti at %d " % env.now)
        yield env.timeout(taskGraphtti)


def schedule(env):
    
    #       ####if offmem： {task.cluster = 1} = offmem()
    #taskGraphs[], candidateTask[]
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

def checkGraphDependency():
    print("checkGraphDependency")

def checkTaskDependency(task):
    print("checkTaskDependency")
    return 1

# update ready_queue task
def ready_queue_update(env,candidate_queue):
    # for task in candidate_queue:
    #     # check if task is ready
    #     if check_task_dependency(task):
    #         candidate_queue.remove(task)
    #         scheduleUtil.allocate_cluster

    for i in range(1,5):
        # check if task is ready
        if checkTaskDependency(1):
            #schedule()
            ResourceManager.placeCluster(1)
    # TIME_OUT
    yield env.timeout(1)

def taskXMLParser(filename):
    #parse task parameteres and dependencies
    return 1