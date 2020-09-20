from resources import dma
from resources import memory

def submit(dsp):
    print ("add task to dsp's queue")
    #Q <- task
    # while(true)
    execute(1)

#while true
def execute(task):
    # memory.get_data(task.data) time_out1
    # exe task (TIME_OUT) time_out2
    # memory.save(task.data) time_out3
    #isfinsih
    #while(true)
    # Q.pop()
    memory.getData(1)
    exe_task (1)
    memory.save(1)

def exe_task(task):
    print("exe task")