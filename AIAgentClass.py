# -*- coding: utf-8 -*-
"""
Title: AIAgentClass
Author: Jacob Christ
Date: 04/13/2024
"""

import os
from LoggerWrapper import LoggerWrapper
from LLMClass import LLM
from os.path import isfile


class GeneralAIAgent:
    """
    General AI Agent used for basic chatting
    """
    
    
    def __init__(self,
                 Name,
                 Model,
                 Temperature,
                 SystemPrompt,
                 BaseUrl,
                 ProjectPath):
        self.Name = Name
        self.Model = Model
        self.Temperature = Temperature
        self.SystemPrompt = SystemPrompt
        self.BaseUrl = BaseUrl
        self.LLM = LLM(self.Name,
                       self.Model,
                       self.Temperature,
                       self.SystemPrompt,
                       self.BaseUrl)
        self.ProjectPath = ProjectPath
        
        
class ArchivistAgent:
    """
    Agent that summarizes the information in the agent's assigned file (text).
    Intended to be used with a KnowledgeCoordinationAgent to faciliate Agentic
    RAG
    """
    
    
    def __init__(self,
                 Name,
                 Model,
                 Temperature,
                 DomainOfExpertise,
                 File,
                 BaseUrl):
        self.Name = Name
        self.Model = Model
        self.Temperature = Temperature
        self.DomainOfExpertise = DomainOfExpertise
        self.File = File
        self.BaseUrl
        self.Type = "Archivist"
        
    
    def mk_memory(self):
        """
        Converts the contents of a text file into a string to be read into an
        LLM
        """
        with open(self.File,"r") as File:
            Memory = File.read()
            File.close()
        return Memory
       
    
    def recall(self,Prompt):
        """ 
        Examines information from the file and returns information relavent to 
        the given prompt
        """    
        SystemPrompt = "You are an expert on " + self.DomainOfExpertise
        Query = "Summarize any knowledge you possess related to the prompt " + Prompt
        Memory = self.mk_memory()
        self.LLM = LLM(self.Name,
                       self.Model,
                       self.Temperature,
                       self.SystemPrompt,
                       self.BaseUrl)
        Messages = list(self.LLM.format_message("system",Memory))
        Knowledge = self.LLM.chat(Query,SystemPrompt + Messages)
        return Knowledge
    
    
class KnowledgeCoordinationAgent:
    """
    An agent designed to manage a vast nested database system.  Uses an
    assortment of subagents to manage the task of retreiving information,
    including other KnowledgeCoordinationAgents and ArchivistAgents
    """
    
    
    def __init__(self,
                 Name,
                 Model,
                 Temperature,
                 DomainOfExpertise,
                 DataBase,
                 BaseUrl):
        self.Name = Name
        self.Model = Model
        self.Temperature = Temperature
        self.DomainOfExpertise = DomainOfExpertise
        self.SystemPrompt = "You are an expert on " + self.DomainOfExpertise
        self.DataBase = DataBase
        self.BaseUrl
        self.SubAgents = []
        self.KnowledgeList = []
        self.Type = "KnowledgeCoordinator"
        self.mk_sub_agents()
        
        
    def mk_sub_agents(self):
        """ 
        Creates a set of sub-agents that manage branches of the database tree 
        managed by the current agent.
        """
        DataBaseContents = os.listdir(self.DataBase)
        for Item in DataBaseContents:
            self.KnowledgeList.append(Item)
            if not isfile(self.DataBase + "/" + Item):
                SubAgent = KnowledgeCoordinationAgent(self.Item + "Agent",
                                                       self.Model,
                                                       self.Temperature,
                                                       Item,
                                                       self.DataBase + "/" + Item,
                                                       self.BaseUrl)
            else:
                DoE = Item.split(",")[0]
                SubAgent = ArchivistAgent(self.Item + "Agent",
                                          self.Model,
                                          self.Tempreature,
                                          DoE,
                                          self.DataBase + "/" + Item,
                                          self.BaseUrl)
            self.SubAgents.append(SubAgent)
                
                
        def summarize(self,InfoList):
            """ 
            Uses an LLM to summarize the information in the given list.
            """
            self.LLM = LLM(self.Name,
                           self.Model,
                           self.Temperature,
                           self.SystemPrompt,
                           self.BaseUrl)
            Memory = " ".join(InfoList)
            Summary = self.LLM.chat("Provide a brief summary of the following information " +
                                    Memory,
                                    self.SystemPrompt)
            return Summary
            
            
        def recall(self,Prompt):
            """ 
            Queries sub-agents for information related to the given prompt
            and summarizes the information returned.
            """
            InfoList = []
            for Agent in self.SubAgents:
                Info = list(Agent.recall(Prompt))
                InfoList += Info
            Summary = self.summarize(InfoList)
            return Summary
                
            
class CoordinationAgent:
    """
    An agent designed to manage other agents.  Intented to act as a fully
    autonomous agent.
    """

    def __init__(self,
                 Name,
                 Model,
                 Temperature,
                 SystemPrompt,
                 DataBase,
                 BaseUrl,
                 MemorySizeLimit):      
        self.Name = Name
        self.Model = Model
        self.Temperature = Temperature
        self.SystemPrompt = SystemPrompt
        self.DataBase = DataBase
        self.BaseUrl
        self.MemorySizeLimit = MemorySizeLimit
        self.MemoryAgents = []
        self.Type = "MasterAgent"
        self.memory_setup()
        self.mk_memory_agent()
        self.mk_reference_agent()
        self.LLM = LLM(self.Name,
                       self.Model,
                       self.Temperature,
                       self.SystemPrompt,
                       self.BaseUrl)
        self.Log = LoggerWrapper(self.Name + " Chat Log",self.ShortTermMemoryPath,)
        
        
    def memory_setup(self):
        """ 
        Sets up the memory directory for the agent.
        """
        self.MemoryPath = self.DataBase + "/Memory"
        self.ShortTermMemoryPath = self.MemoryPath + "/ShortTermMemory"
        self.LongTermMemoryPath = self.MemoryPath + "/LongTermMemory"
        if not os.path.exists(self.MemoryPath):
            os.makedir(self.MemoryPath)
        if not os.path.exists(self.ShortTermMemory):
            os.makedir(self.ShortTermMemory)
        if not os.path.exists(self.LongTermMemory):
            os.makedir(self.LongTermMemory)
            
            
    def mk_memory_agent(self): 
        self.MemoryAgent = KnowledgeCoordinationAgent(self,
                     self.Name,
                     self.Model,
                     self.Temperature,
                     "Memory",
                     self.MemoryPath,
                     self.BaseUrl)
        self.MemoryAgent.SystemPrompt = "You are the memory of " + self.Name
        
    
    def mk_reference_agent(self):
        self.ReferencePath = self.DataBase + "/Reference"
        if os.path.exists(self.ReferencePath):
            self.ReferenceAgent = self.MemoryAgent = KnowledgeCoordinationAgent(self,
                         self.Name,
                         self.Model,
                         self.Temperature,
                         "Research",
                         self.MemoryPath,
                         self.BaseUrl)
            self.ReferenceAgent.SystemPrompt = "You are the reference function for " + self.Name
        else:
            self.ReferenceAgent = None 
             
        
    def remember(self,Prompt):
        """ 
        Queries the agent's memories for information related to the prompt.
        """
        return self.MemoryAgent.recall(Prompt)
    
    
    def research(self,Prompt):
        """ 
        Queries the agent's reference database for information related to the
        prompt.
        """
        return self.ReferenceAgent.recall(Prompt)
    
    
    def summarize(self,InfoList):
        """ 
        Uses an LLM to summarize the information in the given list.
        """
        Memory = " ".join(InfoList)
        Summary = self.LLM.chat("Provide a brief summary of the following information " +
                                Memory,
                                self.SystemPrompt)
        return Summary
    
    
    def recall(self,Prompt):
        """ 
        Returns a summary of information that the Agent can use to answer the
        prompt.
        """
        ReferenceInfo = self.research(Prompt)
        MemoryInfo = self.recall(Prompt)
        return self.summarize([ReferenceInfo,MemoryInfo])
    
    
    def generate_response(self,Prompt):
        """ 
        Generates the agent's response to the prompt.
        """
        Info = self.recall(Prompt)
        Response = self.LLM.chat(Prompt,
                                 [self.SystemPrompt,Info])
        return Response
        
    
    def chat(self,Prompt,Speaker = "User"):
        Response = self.generate_response(Prompt)
        self.Log.Logger.info(Speaker + ": " + Prompt)
        self.Log.Logger.info(self.Name + ": " + Response)
        return Response
        
        
    def manage_memory(self):
        """ 
        Manages the database that stores the agents memories.  Compresses and
        reorganises the database if it exceeds the agent's memory limit.
        """
        def get_directory_size(path):
            """ 
            Gets the size in GB of the provided path.
            """
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            return total_size/1073741824
        
        
        def manage_short_term_memory():
            """ 
            Summaries the content of all but the first 5 files in the short 
            term memory directory for compression to store in long term memory.
            Deletes the summarized files to save system memory. 
            """
            FileList = os.listdir(self.ShortTermMemoryPath)
            FileList.sort()
            NumProcessed = 0
            FileSummaries =  []
            for File in FileList:
                NumProcessed += 1
                if len(FileList)-NumProcessed > 5:
                    FilePath = self.ShortTermMemoryPath + "/" + File
                    FileObject = open(FilePath)
                    FileText = FileObject.read()
                    FileObject.close()
                    FileSummaries.append(self.summarize(list(FileText)))
                    os.remove(FilePath)
            return self.summarize(FileSummaries)
        
        
        def manage_long_term_memory(ShortTermSummary):
            """ 
            Combines the summary of the short term memory and the long term 
            memory into one file.
            """
            FilePath = self.LongTermMemoryPath + "/LongTermMemory.txt"
            FileObject = open(FilePath)
            FileText = FileObject.read()
            FileObject.close()
            NewLongTermText = self.summarize([ShortTermSummary,FileText])
            os.remove(FilePath)
            NewFileObject = open(FilePath,"w")
            NewFileObject.write(NewLongTermText)
            NewFileObject.close()

                    
        MemorySize = get_directory_size(self.MemoryDataBase)
        if MemorySize >= self.MemorySizeLimit:
            ShortTermSummary = manage_short_term_memory()
            manage_long_term_memory(ShortTermSummary)
            try:
                self.manage_memory()
            except:
                pass
            
        
                
        

