from resources import dma 
from resources import dsp 

def save(data):
    # can mem save data
    while not checkMem(data):
        LRU()
    # save data
    print ("save data")

# get data
def getData(data):
    if not checkData(data):
        # generate dma task
        dma.getData(data)
    # transform data(TIME_OUT)  #time_out5
    print ("trasform data")

def LRU():
    #LRU
    print("LRU")

def checkData(data):
    # check if date is in this mem
    print("check data")
    return 0

def checkMem(data):
    # can mem save data
    return 1