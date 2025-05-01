# -*- coding: utf-8 -*-
"""
Title: LLMClass
Author: Jacob Christ
Date: 04/12/2025
"""

import os
from openai import OpenAI

class LLM:
    
    def __init__(self,
                 Name,
                 Model,
                 Temperature,
                 SystemPrompt,
                 BaseUrl):
        self.Name = Name
        self.Model = Model
        self.Temperature = Temperature
        self.SystemPrompt = SystemPrompt
        self.BaseUrl
        self.SourcePath = os.path.dirname(os.path.abspath(__file__))
        self.client = OpenAI(base_url= self.BaseUrl, api_key="lm-studio")
        
        
    def format_message(self,Role,Content):
        Message = { "role" : Role,
                   "content" : Content}
        return Message
    
    
    def chat(self,UserContent,Messages):
        UserMessage = self.format_message("User",UserContent)
        Messages.append(UserMessage)
        SystemResponse = self.client.chat.completions.create(
            model = self.Model,
            messages = Messages,
            temperature = self.Temperature)
        SystemMessage = SystemResponse.choices[0].message.content
        return SystemMessage
    
    
    
        
    
    



