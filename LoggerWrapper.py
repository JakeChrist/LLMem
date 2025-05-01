# -*- coding: utf-8 -*-
"""
Title: Pythong Logging Wrapper
Author: Jacob Christ
Date: 04/12/2025
"""

import logging
import logging.config
import os


class LoggerWrapper:
    
    def get_log_config(self,LoggerName):
        LogConfigText = """ 
        [loggers]\n
        keys=root,{LoggerName}\n\n
        
        [handlers]\n
        keys=consoleHandler\n\n

        [formatters]\n
        keys=simpleFormatter\n\n

        [logger_root]\n
        level=INFO\n
        handlers=consoleHandler\n\n

        [logger_{LoggerName}]\n
        level=INFO\n
        handlers=consoleHandler\n
        qualname={LoggerName}\n
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
    
    
    def __init__(self,LoggerName,AppLogPath):
        self.SourcePath = os.path.dirname(os.path.abspath(__file__))
        LogFileName = AppLogPath + "/{LoggerName}Log.txt"
        LogConfigFile = AppLogPath + "/{LoggerName}LoggingConfig.txt"
        if not os.path.exists(LogConfigFile):
            LogConfigText = self.get_log_config(LoggerName)
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
        Logger = logging.getLogger(LoggerName)
        LogFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        LogHandler = logging.FileHandler(LogFileName)
        LogHandler.setLevel(logging.INFO)
        LogHandler.setFormatter(LogFormat)
        Logger.addHandler(LogHandler)
        self.Logger = Logger
        
        
        