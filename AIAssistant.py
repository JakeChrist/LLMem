# -*- coding: utf-8 -*-
"""
Title: AI Assistant
Author: Jacob Christ
Date: 03/07/2025
"""
import ast
import os
import configparser
import logging
import logging.config
import torch
import soundfile as sf
import noisereduce as nr
from pedalboard import *
from pedalboard.io import AudioFile
from TTS.api import TTS
from openai import OpenAI
from IPython.display import Audio
import sounddevice as sd


class LoggerWrapper:
    
    def get_log_config(self):
        LogConfigText = """ 
        [loggers]\n
        keys=root,AIAssistant\n\n
        
        [handlers]\n
        keys=consoleHandler\n\n

        [formatters]\n
        keys=simpleFormatter\n\n

        [logger_root]\n
        level=INFO\n
        handlers=consoleHandler\n\n

        [logger_AIAssistant]\n
        level=INFO\n
        handlers=consoleHandler\n
        qualname=AIAssistant\n
        propagate=0\n\n
        
        [handler_consoleHandler]\n
        class=StreamHandler\n
        level=INFO\n
        formatter=simpleFormatter\n
        args=(sys.stdout,)\n\n
        
        [formatter_simpleFormatter]\n
        format=%(asctime)s - %(name)s - %(levelname)s - %(message)s\n      
        """
        return LogConfigText


    def __init__(self,Path):
        LogFileName = Path + "/Outputs/Log.txt"
        LogConfigFile = Path + "/Inputs/Configs/" + "Logging.cfg"
        if not os.path.exists(LogConfigFile):
            LogConfigText = self.get_log_config()
            with open(LogConfigFile,'w') as File:
                File.write(LogConfigText)
                File.close()
        if os.path.exists(LogFileName):
            os.remove(LogFileName)
        open(LogFileName,'w').close()
        logging.config.fileConfig(LogConfigFile)
        logging.basicConfig(filename = LogFileName,
                            filemode = "a",
                            datefmt = "%H:%M:%S",
                            level = logging.INFO)
        Logger = logging.getLogger("AIAssistant")
        LogFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        LogHandler = logging.FileHandler(LogFileName)
        LogHandler.setLevel(logging.INFO)
        LogHandler.setFormatter(LogFormat)
        Logger.addHandler(LogHandler)
        self.Logger = Logger
        
        
Log = LoggerWrapper(os.path.dirname(os.path.abspath(__file__)))


class AIAssistant:
    
    def __init__(self):
        Log.Logger.info("Initializing AI Assistant")
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.ConfigFile = self.Path + "/Inputs/Configs/Default.cfg"
        Config = configparser.ConfigParser()
        Log.Logger.info("Attempting to read " + self.ConfigFile)
        try:
            Config.read(self.ConfigFile)
            Log.Logger.info("Successfully read " + self.ConfigFile)
        except Exception as Error:
            Log.Logger.error("Could not read " + self.ConfigFile)
            Log.Logger.error(Error)
        try:
            self.Name = ast.literal_eval(Config["ASSISTANT DATA"]["AssistantName"])
            Log.Logger.info("Successfully read AssistantName from " + self.ConfigFile)
        except Exception as Error:
            Log.Logger.error("Could not read AssistantName from " + self.ConfigFile)
            Log.Logger.error(Error)
        try:
            self.SystemPrompt = ast.literal_eval(Config["ASSISTANT DATA"]["SystemPrompt"])
            Log.Logger.info("Successfully read SystemPrompt from " + self.ConfigFile)
        except Exception as Error:
            Log.Logger.error("Could not read SystemPrompt from " + self.ConfigFile)
            Log.Logger.error(Error)
        try: 
            self.Voice = self.Path + ast.literal_eval(Config["ASSISTANT DATA"]["Voice"])
            Log.Logger.info("Successfully read Voice from " + self.ConfigFile)
        except Exception as Error:
            Log.Logger.info("Could not read Voice from " + self.ConfigFile)
            Log.Logger.error(Error)
        try:
            self.Model = ast.literal_eval(Config["ASSISTANT DATA"]["Model"])
            Log.Logger.info("Successfully read Model from " + self.ConfigFile)
        except Exception as Error:
            Log.Logger.error("Could not read Model from " + self.ConfigFile)
            Log.Logger.error(Error)
        try:
            self.Temperature = ast.literal_eval(Config["ASSISTANT DATA"]["Temperature"])
            Log.Logger.info("Successfully read Temperature from " + self.ConfigFile)
        except Exception as Error:
            Log.Logger.error("Could not read Temperature from " + self.ConfigFile)
            Log.Logger.error(Error)
        try:
            self.BaseUrl = ast.literal_eval(Config["ASSISTANT DATA"]["BaseUrl"])
            Log.Logger.info("Successfully read BaseUrl from " + self.ConfigFile)
        except Exception as Error:
            Log.Logger.error("Could not read BaseUrl from " + self.ConfigFile)
            Log.Logger.error(Error)
        self.LLM = LLM(self.Name,
                                   self.SystemPrompt,
                                   self.Model,
                                   self.BaseUrl,
                                   self.Temperature)
        self.Vocals = Vocals(self.Voice)
            
        
    def chat(self,UserContent):
        SystemResponse = self.LLM.chat(UserContent)
        if self.Voice != "None":
            self.Vocals.talk(SystemResponse)
                
            
class LLM:
    
    
    def __init__(self,Name,SystemPrompt,Model,BaseUrl,Temperature):
        Log.Logger.info("Initialzing LLM")
        self.Name = Name
        self.SystemPrompt = SystemPrompt
        self.Model = Model
        self.BaseUrl = BaseUrl
        self.Temperature = Temperature
        self.Messages = []
        self.Messages.append(self.format_message("system",SystemPrompt))
        self.client = OpenAI(base_url= self.BaseUrl, api_key="lm-studio")
        self.ChatLog = ["SystemPrompt: " + SystemPrompt]
        Log.Logger.info("LLM Initialized")
        
        
    def format_message(self,Role,Content):
        Log.Logger.info("Formatting " + Role + "message")
        Message = { "role" : Role,
                   "content" : Content}
        return Message
        
    def log_chat(self,Message,Role):
        self.ChatLog.append(Role + ": " + Message)
        
        
    def chat(self,UserContent):
        Log.Logger.info("Beginning chat completion")
        UserMessage = self.format_message("user",UserContent)
        self.log_chat(UserContent, "user")
        self.Messages.append(UserMessage)
        Log.Logger.info("Generating System response...")
        SystemResponse = self.client.chat.completions.create(
            model = self.Model,
            messages = self.Messages,
            temperature = self.Temperature)
        SystemMessage = SystemResponse.choices[0].message.content
        print(SystemMessage)
        self.log_chat(SystemMessage,"system")
        self.Messages.append(SystemMessage)
        Log.Logger.info("...System response completed and logged")
        return SystemMessage
                
            
class Vocals:
    
    
    def __init__(self,Voice):
        Log.Logger.info("Initialzing AIAssistant Vocals")
        self.Voice = Voice
        self.sr = 24000
        Log.Logger.info("AIAssistant Vocals Initialized")
        
        
    def enhance_audio(self,Audio):
        Log.Logger.info("Enhancing Audio")
        ReducedNoise = nr.reduce_noise(y = Audio,
                                       sr = self.sr,
                                       stationary = True,
                                       prop_decrease = 0.75)
        return ReducedNoise
        
        
        
    def talk(self,Text):
        Log.Logger.info("Vocalizing system message")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        VocalizedText = tts.tts(text = Text, speaker_wav= self.Voice, language="en")
        EnhancedAudio = self.enhance_audio(VocalizedText)
        sd.play(EnhancedAudio,self.sr)
        Log.Logger.info("System message vocalized")
                    
                    
                    
                
Eve = AIAssistant()               
                
                
            
            
            
            
            
            
            
            