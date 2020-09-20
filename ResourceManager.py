import resources.dsp as dsp

def hardwareXMLParser(filename):
    #parse hardware configuration 
    return 1

def placeCluster(task):
    print ("placeCluster")
    #task->dsp
    placeDSP(1,task)
    
def placeDSP(cluster,task):
    print ("placeDSP")
    dsp.submit(task)
    