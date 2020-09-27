#!/usr/bin/python
# encoding: utf-8
import xml.sax
from TaskModule.TaskManager import *



 #定义TaskGraph
class TaskXMLHandler( xml.sax.ContentHandler ):
   def __init__(self):
      self.CurrentData = "" 
      self.type = ""  
      self.jobId = 0
 
      self.graphId = -1          
      self.graphName = ""
      self.globalTaskList = [] 
      self.DDL = 1 
      self.period = 1  
      
      self.taskInsList = []  

      self.taskName=""
      self.cost=0
      self.instCnt=0
      self.graphId=0
      self.graphName=""
      self.knrlType="DSP"
      self.data_name=""
      self.mov_dir=0
      self.job_inst_idx=0
      self.total_size=0
      self.data_inst_idx=[] 
      self.graphList=[] 
      self.producerMap = {} #key:dataInsOut : value: task

   def getProducerMap(self):   
      return self.producerMap

   def getGraphList(self):
      return self.graphList

   def startElement(self, tag, attributes):
      self.CurrentData = tag
      if tag == "task_graph": 
            self.graphId = int(attributes["id"])
            self.graphName=attributes["name"]
            # print("Task graph begins: id=%d, name=%s" %(self.graphId, self.graphName))
      elif tag=="data_info":
            # print("Update the task dependency")
            for task in self.globalTaskList:
               precedenceTask = []
               precedenceJobId = [] 
               for datains in task.dataInsIn: 
                  key = datains.dataName + "-" + str(datains.data_inst_idx)
                  if key in self.producerMap:
                     precedenceTask.append(self.producerMap[key])
                     precedenceJobId.append(self.producerMap[key].jobId)
                     #print("%s depends on %s (jobId=%d)" % 
                     #(task.taskName, self.producerMap[key].taskName, self.producerMap[key].jobId))
               task.setPrecedenceJobID(precedenceJobId)
               task.setPrecedenceTask(precedenceTask) 
            # print("Task graph parse ends: id=%d, name=%s" %(self.graphId, self.graphName))
            tg = TaskGraph (self.graphId, self.graphName, 
               self.DDL, self.period, self.globalTaskList, [])
            # print(len(self.globalTaskList))
            self.graphList.append(tg)
            # print("Prepare for the next graph")
            self.graphId = -1
            self.graphName = ""
            self.globalTaskList = []
            #self.producerMap = {}
      elif tag=="task":
            self.taskName=attributes["name"]
            #print("Find %s" % self.taskName) 
      elif tag=="properties": 
            self.instCnt=int(attributes["instCnt"])
            self.cost = int(attributes["cost"])
            self.knrlType=attributes["type"]
            self.taskInsList = [] 
            #print("Task properties: instCnt=%d, cost=%d, type=%s" %(self.instCnt, self.cost, self.knrlType))
            for task_index in range(self.instCnt):
               #print("task: taskName=%s, instCnt=%d, jobId=%d, graphId=%d, job_inst_idx=%d" 
               # % (self.taskName, self.instCnt, self.jobId, self.graphId, task_index))
               self.taskInsList.append(Task(self.taskName, self.knrlType, self.instCnt, self.jobId, 
               self.graphId, task_index, self.cost))
               self.jobId += 1
            self.globalTaskList.extend(self.taskInsList)
      elif tag=="proc_item":
            self.id = attributes["id"]
            self.data_name=attributes["data_name"]
            self.mov_dir=int(attributes["mov_dir"]) 
            #print("proc_item: id=%s, data_name=%s, mov_dir=%d" %(self.id, self.data_name, self.mov_dir))
      elif tag=="data_inst":
            self.job_inst_idx=int(attributes["job_inst_idx"])
            self.total_size=int(attributes["total_size"])
            data_inst_idx_str=attributes["data_inst_idx"]
 
            self.data_inst_idx=data_inst_idx_str.split(",")
            self.data_inst_idx.pop() 

            dataInsIn = []
            dataInsOut = []   
            datasize = self.total_size/len(self.data_inst_idx)   
            if self.mov_dir==0:
               for dataid in range (len(self.data_inst_idx)):
                  #dataName, mov_dir, job_inst_idx, data_size, data_inst_idx
                  datains=DataInstance(self.data_name, self.mov_dir, self.job_inst_idx, datasize, dataid)
                  dataInsIn.append(datains)
                  #print("input datainstance: job_inst_idx=%d, datasize=%d, data_inst_idx=%d" 
                  #% (self.job_inst_idx, datasize, dataid))
               self.taskInsList[self.job_inst_idx].setDataInsIn(dataInsIn)
               #print("set dataInsIn for jobId=%d" % self.taskInsList[self.job_inst_idx].jobId)               
            else:
               for dataid in range (len(self.data_inst_idx)):
                  #dataName, mov_dir, job_inst_idx, data_size, data_inst_idx
                  datains=DataInstance(self.data_name, self.mov_dir, self.job_inst_idx, datasize, dataid)
                  dataInsOut.append(datains)
                  self.producerMap[self.data_name + "-" +str(dataid)] = self.taskInsList[self.job_inst_idx]
                  #print("output datainstance: job_inst_idx=%d, datasize=%d, data_inst_idx=%d of jobid=%d" 
                  #% (self.job_inst_idx, datasize, dataid, self.taskInsList[self.job_inst_idx].jobId))  
               self.taskInsList[self.job_inst_idx].setDataInsOut(dataInsOut)
               #print("set dataInsOut for jobId=%d" % self.taskInsList[self.job_inst_idx].jobId)

               
              
if ( __name__ == "__main__"):
   parser = xml.sax.make_parser()
   # turn off namepsaces
   parser.setFeature(xml.sax.handler.feature_namespaces, 0)
   Handler = TaskXMLHandler()
   parser.setContentHandler( Handler )
   parser.parse("TaskGraph0903.xml")
   graphList = Handler.getGraphList()
   print(graphList)
   print(len(graphList))
